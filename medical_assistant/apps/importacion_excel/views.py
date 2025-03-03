## Views.py app/imporacion_excel
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.template.loader import render_to_string
from .utils import ExcelProcessor, ProcesadorExcel
from .models import ExcelImport, CorreccionDatos, ReglaCorreccion, MapeoColumnas
from .forms import ArchivoExcelForm, MapeoColumnasForm, ReglaCorreccionForm, CorreccionManualForm
from .validators import ValidadorExcel
from django.db import transaction
from django.db.models import Count, Avg, Sum, F, ExpressionWrapper, FloatField
from django.db.models.functions import TruncMonth, TruncDate
from django.utils import timezone
import pandas as pd
import json
from io import BytesIO
from django.core.paginator import Paginator
from django.db.models import Q
import csv
from datetime import datetime, timedelta
import xlsxwriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

@login_required
def importar_excel(request):
    """Vista principal para la importación de archivos Excel"""
    if request.method == 'POST':
        form = ArchivoExcelForm(request.POST, request.FILES)
        if form.is_valid():
            importacion = form.save(commit=False)
            importacion.usuario = request.user
            importacion.save()
            
            try:
                # Leer archivo y validar estructura
                df = pd.read_excel(importacion.archivo.path)
                importacion.registros_totales = len(df)
                importacion.datos_originales = df.to_json(orient='records')
                importacion.save()
                
                return redirect('importacion_excel:previsualizar_excel', pk=importacion.pk)
            except Exception as e:
                importacion.delete()
                messages.error(request, f'Error al procesar el archivo: {str(e)}')
    else:
        form = ArchivoExcelForm()
    
    # Mostrar historial de importaciones recientes
    importaciones_recientes = ExcelImport.objects.filter(
        usuario=request.user
    ).order_by('-fecha_subida')[:5]
    
    return render(request, 'importacion_excel/importar.html', {
        'form': form,
        'importaciones_recientes': importaciones_recientes
    })

@login_required
def previsualizar_excel(request, pk):
    """Vista para previsualizar y validar los datos antes de importar"""
    importacion = get_object_or_404(ExcelImport, pk=pk)
    
    if importacion.estado != 'PENDIENTE':
        messages.warning(request, 'Esta importación ya fue procesada.')
        return redirect('importacion_excel:ver_resultados', pk=pk)
    
    try:
        df = pd.read_json(importacion.datos_originales)
        processor = ExcelProcessor()
        
        # Procesar primeras 10 filas para previsualización
        muestra_datos = []
        errores = []
        advertencias = []
        
        for idx, row in df.head(10).iterrows():
            datos, errs, warns = processor.procesar_registro(row, idx, 'Sheet1')
            muestra_datos.append(datos)
            errores.extend(errs)
            advertencias.extend(warns)
        
        context = {
            'importacion': importacion,
            'columnas': df.columns.tolist(),
            'muestra_datos': muestra_datos,
            'errores': errores,
            'advertencias': advertencias,
            'total_registros': len(df)
        }
        
        return render(request, 'importacion_excel/previsualizar.html', context)
        
    except Exception as e:
        messages.error(request, f'Error al previsualizar los datos: {str(e)}')
        return redirect('importacion_excel:importar_excel')

@login_required
@transaction.atomic
def revisar_excel(request):
    """Vista para revisar y corregir datos antes de la importación final"""
    if request.method == 'POST':
        importacion_id = request.POST.get('importacion_id')
        importacion = get_object_or_404(ExcelImport, pk=importacion_id)
        
        if importacion.estado != 'PENDIENTE':
            messages.warning(request, 'Esta importación ya fue procesada.')
            return redirect('importacion_excel:ver_resultados', pk=importacion_id)
        
        try:
            importacion.estado = 'EN_REVISION'
            importacion.save()
            
            processor = ProcesadorExcel(importacion_id)
            resultado = processor.procesar_archivo()
            
            if resultado:
                messages.success(request, 'Datos procesados correctamente.')
                return redirect('importacion_excel:ver_resultados', pk=importacion_id)
            else:
                messages.error(request, 'Error al procesar los datos.')
                
        except Exception as e:
            messages.error(request, f'Error durante el procesamiento: {str(e)}')
        
        return redirect('importacion_excel:previsualizar_excel', pk=importacion_id)
    
    return redirect('importacion_excel:importar_excel')

@login_required
@transaction.atomic
def ver_resultados(request, pk):
    """Vista para ver los resultados de la importación"""
    importacion = get_object_or_404(ExcelImport, pk=pk)
    tasa_exito = 0
    if importacion.registros_totales > 0:
        tasa_exito = (importacion.registros_procesados - importacion.registros_con_error) / importacion.registros_totales * 100 
    estadisticas = {
        'total': importacion.registros_totales,
        'procesados': importacion.registros_procesados,
        'con_error': importacion.registros_con_error,
        'tasa_exito': tasa_exito
    }
    reglas_aplicadas = importacion.correcciones.all()
    return render(request, 'importacion_excel/resultados.html', {
        'importacion': importacion,
        'estadisticas': estadisticas,
        'reglas_aplicadas': reglas_aplicadas
    })

@login_required
def descargar_errores(request, importacion_id):
    """Vista para descargar el reporte de errores"""
    importacion = get_object_or_404(ExcelImport, pk=importacion_id)
    
    if not importacion.log_procesamiento:
        messages.error(request, 'No hay registro de errores disponible.')
        return redirect('importacion_excel:ver_resultados', pk=importacion_id)
    
    # Crear Excel con errores
    df_errores = pd.DataFrame(json.loads(importacion.log_procesamiento))
    
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename=errores_importacion_{importacion_id}.xlsx'
    
    df_errores.to_excel(response, index=False)
    return response

@login_required
def descargar_plantilla(request, tipo):
    """Descarga una plantilla Excel según el tipo de importación"""
    try:
        # Obtener configuración de mapeo para el tipo
        mapeos = MapeoColumnas.objects.filter(tipo_importacion=tipo)
        
        # Crear DataFrame con columnas mapeadas
        df = pd.DataFrame(columns=[m.nombre_columna_excel for m in mapeos])
        
        # Agregar fila de ejemplo si es necesario
        if request.GET.get('incluir_ejemplo') == '1':
            ejemplo = {m.nombre_columna_excel: m.valor_defecto for m in mapeos}
            df = df.append(ejemplo, ignore_index=True)
        
        # Generar Excel
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename=plantilla_{tipo.lower()}.xlsx'
        df.to_excel(response, index=False)
        return response
        
    except Exception as e:
        messages.error(request, f"Error al generar la plantilla: {str(e)}")
        return redirect('importacion_excel:importar_excel')

@login_required
def lista_mapeos(request):
    """Lista los mapeos de columnas configurados"""
    mapeos = MapeoColumnas.objects.all().order_by('nombre_columna_excel')
    return render(request, 'importacion_excel/mapeos/lista.html', {
        'mapeos': mapeos
    })

@login_required
def crear_mapeo(request):
    """Crea un nuevo mapeo de columnas"""
    if request.method == 'POST':
        form = MapeoColumnasForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Mapeo creado correctamente")
            return redirect('importacion_excel:lista_mapeos')
    else:
        form = MapeoColumnasForm()
    
    return render(request, 'importacion_excel/mapeos/form.html', {
        'form': form,
        'titulo': 'Crear Mapeo'
    })

@login_required
def editar_mapeo(request, pk):
    """Edita un mapeo existente"""
    mapeo = get_object_or_404(MapeoColumnas, pk=pk)
    if request.method == 'POST':
        form = MapeoColumnasForm(request.POST, instance=mapeo)
        if form.is_valid():
            form.save()
            messages.success(request, "Mapeo actualizado correctamente")
            return redirect('importacion_excel:lista_mapeos')
    else:
        form = MapeoColumnasForm(instance=mapeo)
    
    return render(request, 'importacion_excel/mapeos/form.html', {
        'form': form,
        'titulo': 'Editar Mapeo'
    })

@login_required
def eliminar_mapeo(request, pk):
    """Elimina un mapeo"""
    mapeo = get_object_or_404(MapeoColumnas, pk=pk)
    if request.method == 'POST':
        mapeo.delete()
        messages.success(request, "Mapeo eliminado correctamente")
    return redirect('importacion_excel:lista_mapeos')

@login_required
def lista_reglas(request):
    """Lista las reglas de corrección"""
    reglas = ReglaCorreccion.objects.all().order_by('-confianza')
    return render(request, 'importacion_excel/reglas/lista.html', {
        'reglas': reglas
    })

@login_required
def crear_regla(request):
    """Crea una nueva regla de corrección"""
    if request.method == 'POST':
        form = ReglaCorreccionForm(request.POST)
        if form.is_valid():
            regla = form.save(commit=False)
            regla.creada_por = request.user
            regla.save()
            messages.success(request, "Regla creada correctamente")
            return redirect('importacion_excel:lista_reglas')
    else:
        form = ReglaCorreccionForm()
    
    return render(request, 'importacion_excel/reglas/form.html', {
        'form': form,
        'titulo': 'Crear Regla'
    })

@login_required
def editar_regla(request, pk):
    """Edita una regla existente"""
    regla = get_object_or_404(ReglaCorreccion, pk=pk)
    if request.method == 'POST':
        form = ReglaCorreccionForm(request.POST, instance=regla)
        if form.is_valid():
            form.save()
            messages.success(request, "Regla actualizada correctamente")
            return redirect('importacion_excel:lista_reglas')
    else:
        form = ReglaCorreccionForm(instance=regla)
    
    return render(request, 'importacion_excel/reglas/form.html', {
        'form': form,
        'titulo': 'Editar Regla'
    })

@login_required
def eliminar_regla(request, pk):
    """Elimina una regla"""
    regla = get_object_or_404(ReglaCorreccion, pk=pk)
    if request.method == 'POST':
        regla.delete()
        messages.success(request, "Regla eliminada correctamente")
    return redirect('importacion_excel:lista_reglas')

@login_required
def historial_importaciones(request):
    """Vista para ver el historial de importaciones"""
    importaciones = ExcelImport.objects.filter(usuario=request.user).order_by('-fecha_subida')
    
    # Filtros
    tipo = request.GET.get('tipo')
    estado = request.GET.get('estado')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    if tipo:
        importaciones = importaciones.filter(tipo_importacion=tipo)
    if estado:
        importaciones = importaciones.filter(estado=estado)
    if fecha_desde:
        importaciones = importaciones.filter(fecha_subida__gte=fecha_desde)
    if fecha_hasta:
        importaciones = importaciones.filter(fecha_subida__lte=fecha_hasta)
    
    # Paginación
    paginator = Paginator(importaciones, 15)
    page = request.GET.get('page')
    importaciones_paginadas = paginator.get_page(page)
    
    context = {
        'importaciones': importaciones_paginadas,
        'tipos_importacion': ExcelImport.TIPOS_IMPORTACION,
        'estados': ExcelImport.ESTADOS,
        'filtros': {
            'tipo': tipo,
            'estado': estado,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta
        }
    }
    
    return render(request, 'importacion_excel/historial.html', context)

@login_required
def estadisticas_importaciones(request):
    """Vista para ver estadísticas de importaciones"""
    # Obtener período
    dias = int(request.GET.get('dias', 30))
    tipo = request.GET.get('tipo')
    
    estadisticas = obtener_estadisticas(dias, tipo)
    
    return render(request, 'importacion_excel/estadisticas.html', {
        'estadisticas': estadisticas,
        'dias': dias,
        'tipo_selected': tipo,
        'tipos_importacion': ExcelImport.TIPOS_IMPORTACION
    })

@login_required
def actualizar_estadisticas(request):
    """Vista para actualizar las estadísticas vía AJAX"""
    try:
        # Obtener parámetros de filtro
        periodo = int(request.GET.get('periodo', 30))
        tipo = request.GET.get('tipo', 'todos')
        estado = request.GET.get('estado', 'todos')
        
        # Obtener estadísticas filtradas
        datos = obtener_estadisticas(
            dias=periodo,
            tipo_importacion=tipo if tipo != 'todos' else None,
            estado=estado if estado != 'todos' else None
        )
        
        return JsonResponse(datos)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)

def obtener_estadisticas(dias=30, tipo_importacion=None, estado=None):
    """Función auxiliar para obtener estadísticas filtradas"""
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count, Avg, F, Q
    from django.db.models.functions import TruncDate
    
    fecha_inicio = timezone.now() - timedelta(days=dias)
    
    # Construir filtro base
    filtro_base = Q(fecha_subida__gte=fecha_inicio)
    if tipo_importacion:
        filtro_base &= Q(tipo_importacion=tipo_importacion)
    if estado:
        filtro_base &= Q(estado=estado)
    
    # Obtener queryset base
    importaciones = ExcelImport.objects.filter(filtro_base)
    
    # Calcular estadísticas generales
    total_importaciones = importaciones.count()
    importaciones_exitosas = importaciones.filter(estado='IMPORTADO').count()
    tasa_exito = round((importaciones_exitosas / total_importaciones * 100) if total_importaciones > 0 else 0, 1)
    
    # Estadísticas detalladas
    stats = {
        'total_importaciones': total_importaciones,
        'tasa_exito': tasa_exito,
        'promedio_registros': round(importaciones.aggregate(avg=Avg('registros_totales'))['avg'] or 0),
        'total_errores': importaciones.aggregate(total=Sum('registros_con_error'))['total'] or 0,
        
        # Datos para gráfico de tendencia
        'tendencia': {
            'labels': [],
            'datos': []
        },
        
        # Datos para gráfico de distribución por estado
        'estados': {
            'labels': [],
            'datos': []
        },
        
        # Datos para gráfico de errores comunes
        'errores': {
            'labels': [],
            'datos': []
        },
        
        # Datos para gráfico de tasa de corrección
        'correccion': {
            'labels': [],
            'datos': []
        }
    }
    
    # Tendencia diaria
    tendencia = (
        importaciones
        .annotate(fecha=TruncDate('fecha_subida'))
        .values('fecha')
        .annotate(total=Count('id'))
        .order_by('fecha')
    )
    
    stats['tendencia']['labels'] = [t['fecha'].strftime('%d/%m/%Y') for t in tendencia]
    stats['tendencia']['datos'] = [t['total'] for t in tendencia]
    
    # Distribución por estado
    estados = (
        importaciones
        .values('estado')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    
    stats['estados']['labels'] = [e['estado'] for e in estados]
    stats['estados']['datos'] = [e['total'] for e in estados]
    
    # Errores más comunes
    errores_comunes = (
        CorreccionDatos.objects
        .filter(importacion__in=importaciones)
        .values('campo')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )
    
    stats['errores']['labels'] = [e['campo'] for e in errores_comunes]
    stats['errores']['datos'] = [e['total'] for e in errores_comunes]
    
    # Tasa de corrección por tipo
    correcciones = (
        importaciones
        .values('tipo_importacion')
        .annotate(
            tasa=ExpressionWrapper(
                (F('registros_procesados') - F('registros_con_error')) * 100.0 / F('registros_totales'),
                output_field=FloatField()
            )
        )
        .order_by('tipo_importacion')
    )
    
    stats['correccion']['labels'] = [c['tipo_importacion'] for c in correcciones]
    stats['correccion']['datos'] = [round(c['tasa'], 1) for c in correcciones]
    
    return stats

@login_required
def validar_columna(request):
    """API para validar una columna específica"""
    try:
        valor = request.POST.get('valor')
        campo = request.POST.get('campo')
        validator = ValidadorExcel()
        resultado, valor_corregido = validator.validar_campo(campo, valor)
        return JsonResponse({
            'valido': resultado,
            'valor_corregido': valor_corregido
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)

@login_required
def sugerir_correccion(request):
    """API para sugerir correcciones basadas en reglas existentes"""
    try:
        valor = request.POST.get('valor')
        campo = request.POST.get('campo')
        
        # Buscar reglas aplicables
        reglas = ReglaCorreccion.objects.filter(
            campo=campo,
            activa=True
        ).order_by('-confianza')
        
        sugerencias = []
        for regla in reglas:
            valor_corregido = regla.aplicar(valor)
            if valor_corregido != valor:
                sugerencias.append({
                    'valor': valor_corregido,
                    'confianza': regla.confianza,
                    'regla_id': regla.id
                })
        
        return JsonResponse({
            'sugerencias': sugerencias
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)

@login_required
def filtrar_importaciones_ajax(request):
    """Vista para manejar filtros AJAX en el historial"""
    try:
        # Obtener parámetros de filtro
        estado = request.GET.get('estado')
        tipo = request.GET.get('tipo')
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        busqueda = request.GET.get('busqueda')
        page = request.GET.get('page', 1)

        # Query base
        importaciones = ExcelImport.objects.all().order_by('-fecha_subida')

        # Aplicar filtros
        if estado:
            importaciones = importaciones.filter(estado=estado)
        if tipo:
            importaciones = importaciones.filter(tipo_importacion=tipo)
        if fecha_desde:
            importaciones = importaciones.filter(fecha_subida__gte=fecha_desde)
        if fecha_hasta:
            importaciones = importaciones.filter(fecha_subida__lte=fecha_hasta)
        if busqueda:
            importaciones = importaciones.filter(
                Q(archivo__icontains=busqueda) |
                Q(usuario__first_name__icontains=busqueda) |
                Q(usuario__last_name__icontains=busqueda)
            )

        # Paginación
        paginator = Paginator(importaciones, 10)
        page_obj = paginator.get_page(page)

        # Renderizar solo la tabla
        html = render_to_string('importacion_excel/partials/tabla_importaciones.html', {
            'importaciones': page_obj,
            'request': request
        })

        # Devolver respuesta JSON
        return JsonResponse({
            'html': html,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'total_items': paginator.count
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def exportar_datos(request):
    """
    Vista para exportar datos en diferentes formatos (Excel, CSV, PDF)
    """
    try:
        importacion_id = request.GET.get('importacion_id')
        formato = request.GET.get('formato', 'excel').lower()
        
        if not importacion_id:
            return JsonResponse({
                'error': 'Se requiere el ID de importación'
            }, status=400)
            
        importacion = get_object_or_404(ExcelImport, id=importacion_id)
        
        # Preparar datos para exportar
        datos = {
            'info_general': {
                'fecha': importacion.fecha_subida.strftime('%d/%m/%Y'),
                'usuario': importacion.usuario.get_full_name(),
                'tipo': importacion.get_tipo_importacion_display(),
                'estado': importacion.get_estado_display()
            },
            'estadisticas': {
                'total_registros': importacion.registros_totales,
                'procesados': importacion.registros_procesados,
                'con_error': importacion.registros_con_error
            },
            'registros': importacion.datos_originales,
            'correcciones': list(importacion.correcciones.values())
        }
        
        if formato == 'excel':
            return exportar_excel(datos, f'importacion_{importacion_id}')
        elif formato == 'csv':
            return exportar_csv(datos, f'importacion_{importacion_id}')
        elif formato == 'pdf':
            return exportar_pdf(datos, f'importacion_{importacion_id}')
        else:
            return JsonResponse({
                'error': 'Formato no soportado'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'error': f'Error al exportar: {str(e)}'
        }, status=500)

def exportar_excel(datos, nombre_archivo):
    """Exporta los datos en formato Excel."""
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    
    # Formato para títulos
    titulo_formato = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'align': 'center',
        'bg_color': '#4F81BD',
        'font_color': 'white'
    })
    
    # Hoja de información general
    ws_info = workbook.add_worksheet('Información General')
    for i, (key, value) in enumerate(datos['info_general'].items()):
        ws_info.write(i, 0, key.replace('_', ' ').title(), titulo_formato)
        ws_info.write(i, 1, value)
    
    # Hoja de estadísticas
    ws_stats = workbook.add_worksheet('Estadísticas')
    for i, (key, value) in enumerate(datos['estadisticas'].items()):
        ws_stats.write(i, 0, key.replace('_', ' ').title(), titulo_formato)
        ws_stats.write(i, 1, value)
    
    # Hoja de registros
    if datos['registros']:
        ws_registros = workbook.add_worksheet('Registros')
        for hoja, registros in datos['registros'].items():
            if registros:
                headers = list(registros[0].keys())
                for col, header in enumerate(headers):
                    ws_registros.write(0, col, header, titulo_formato)
                for row, registro in enumerate(registros, 1):
                    for col, value in enumerate(registro.values()):
                        ws_registros.write(row, col, value)
    
    # Hoja de correcciones
    if datos['correcciones']:
        ws_correcciones = workbook.add_worksheet('Correcciones')
        headers = ['Campo', 'Valor Original', 'Valor Corregido', 'Usuario', 'Fecha']
        for col, header in enumerate(headers):
            ws_correcciones.write(0, col, header, titulo_formato)
        for row, correccion in enumerate(datos['correcciones'], 1):
            ws_correcciones.write(row, 0, correccion['campo'])
            ws_correcciones.write(row, 1, correccion['valor_original'])
            ws_correcciones.write(row, 2, correccion['valor_corregido'])
            ws_correcciones.write(row, 3, correccion['usuario'])
            ws_correcciones.write(row, 4, correccion['fecha'])
    
    workbook.close()
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={nombre_archivo}.xlsx'
    return response

def exportar_csv(datos, nombre_archivo):
    """Exporta los datos en formato CSV."""
    output = BytesIO()
    writer = csv.writer(output)
    
    # Información general
    writer.writerow(['INFORMACIÓN GENERAL'])
    for key, value in datos['info_general'].items():
        writer.writerow([key.replace('_', ' ').title(), value])
    
    writer.writerow([])  # Línea en blanco
    
    # Estadísticas
    writer.writerow(['ESTADÍSTICAS'])
    for key, value in datos['estadisticas'].items():
        writer.writerow([key.replace('_', ' ').title(), value])
    
    writer.writerow([])  # Línea en blanco
    
    # Registros
    if datos['registros']:
        writer.writerow(['REGISTROS'])
        for hoja, registros in datos['registros'].items():
            if registros:
                writer.writerow([f'Hoja: {hoja}'])
                headers = list(registros[0].keys())
                writer.writerow(headers)
                for registro in registros:
                    writer.writerow(registro.values())
            writer.writerow([])  # Línea en blanco
    
    # Correcciones
    if datos['correcciones']:
        writer.writerow(['CORRECCIONES'])
        headers = ['Campo', 'Valor Original', 'Valor Corregido', 'Usuario', 'Fecha']
        writer.writerow(headers)
        for correccion in datos['correcciones']:
            writer.writerow([
                correccion['campo'],
                correccion['valor_original'],
                correccion['valor_corregido'],
                correccion['usuario'],
                correccion['fecha']
            ])
    
    output.seek(0)
    response = HttpResponse(output.read(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={nombre_archivo}.csv'
    return response

def exportar_pdf(datos, nombre_archivo):
    """Exporta los datos en formato PDF."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={nombre_archivo}.pdf'
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos de tabla
    style_table = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    
    # Información general
    elements.append(Table(
        [['INFORMACIÓN GENERAL']] + 
        [[k.replace('_', ' ').title(), v] for k, v in datos['info_general'].items()],
        style=style_table
    ))
    elements.append(Table([[' ']], style=style_table))  # Espacio
    
    # Estadísticas
    elements.append(Table(
        [['ESTADÍSTICAS']] + 
        [[k.replace('_', ' ').title(), v] for k, v in datos['estadisticas'].items()],
        style=style_table
    ))
    elements.append(Table([[' ']], style=style_table))  # Espacio
    
    # Registros
    if datos['registros']:
        for hoja, registros in datos['registros'].items():
            if registros:
                headers = list(registros[0].keys())
                data = [headers] + [list(r.values()) for r in registros]
                elements.append(Table(
                    [[f'REGISTROS - {hoja}']] + data,
                    style=style_table
                ))
                elements.append(Table([[' ']], style=style_table))  # Espacio
    
    # Correcciones
    if datos['correcciones']:
        headers = ['Campo', 'Valor Original', 'Valor Corregido', 'Usuario', 'Fecha']
        data = [headers] + [
            [c['campo'], c['valor_original'], c['valor_corregido'], 
             c['usuario'], c['fecha']]
            for c in datos['correcciones']
        ]
        elements.append(Table(
            [['CORRECCIONES']] + data,
            style=style_table
        ))
    
    # Generar PDF
    doc.build(elements)
    return response

## Fin del Modulo


