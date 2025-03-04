from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse, HttpResponseNotFound, HttpResponseServerError
from django.conf import settings
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .models import Informe, VersionInforme, ProtocoloProcedimiento, FirmaDigital, FirmaInforme
from .utils import GeneradorPDF
import difflib
import json
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
import os
from io import BytesIO

# Create your views here.

@login_required
def editar_informe(request, informe_id):
    """
    Vista para editar un informe existente.
    """
    informe = get_object_or_404(Informe, id=informe_id)
    
    # Verificar permisos
    if informe.medico != request.user.medico:
        raise PermissionDenied("No tienes permiso para editar este informe")
    
    if request.method == 'POST':
        contenido_nuevo = request.POST.get('contenido')
        motivo = request.POST.get('motivo_modificacion')
        
        if not motivo:
            messages.error(request, "Debes proporcionar un motivo para la modificación")
            return redirect('editar_informe', informe_id=informe.id)
        
        # Crear nueva versión
        version = VersionInforme.objects.create(
            informe=informe,
            contenido=informe.contenido,  # Guardamos el contenido anterior
            variables_utilizadas=informe.variables_utilizadas,
            medico_modificacion=request.user.medico,
            motivo_modificacion=motivo
        )
        
        # Actualizar informe con nuevo contenido
        informe.contenido = contenido_nuevo
        informe.save()
        
        # Regenerar PDF si es necesario
        if hasattr(informe, 'protocolo_procedimiento'):
            pdf_buffer = informe.protocolo_procedimiento.generar_pdf()
            informe.archivo_generado.save(
                f'informe_{informe.id}_v{version.version}.pdf',
                pdf_buffer,
                save=True
            )
        
        messages.success(request, "Informe actualizado correctamente")
        return redirect('ver_informe', informe_id=informe.id)
    
    context = {
        'informe': informe,
        'versiones': informe.versiones.all(),
        'puede_editar': True
    }
    return render(request, 'informes/editar_informe.html', context)

@login_required
def ver_version_informe(request, version_id):
    """
    Vista para ver una versión específica de un informe.
    """
    version = get_object_or_404(VersionInforme, id=version_id)
    informe = version.informe
    
    if informe.medico != request.user.medico:
        raise PermissionDenied("No tienes permiso para ver este informe")
    
    context = {
        'informe': informe,
        'version': version,
        'es_version_anterior': True
    }
    return render(request, 'informes/ver_version_informe.html', context)

@login_required
@require_POST
def comparar_versiones(request):
    """
    Vista para comparar dos versiones de un informe.
    Utiliza difflib para mostrar diferencias detalladas.
    """
    version1_id = request.POST.get('version1')
    version2_id = request.POST.get('version2')
    
    version1 = get_object_or_404(VersionInforme, id=version1_id)
    version2 = get_object_or_404(VersionInforme, id=version2_id)
    
    if version1.informe != version2.informe:
        return JsonResponse({'error': 'Las versiones deben ser del mismo informe'}, status=400)
    
    if version1.informe.medico != request.user.medico:
        raise PermissionDenied("No tienes permiso para comparar estas versiones")
    
    # Comparar contenido usando difflib
    diff = list(difflib.unified_diff(
        version1.contenido.splitlines(),
        version2.contenido.splitlines(),
        fromfile=f'Versión {version1.version}',
        tofile=f'Versión {version2.version}',
        lineterm=''
    ))

    # Comparar variables
    vars1 = version1.variables_utilizadas
    vars2 = version2.variables_utilizadas
    variables_diff = {}
    all_keys = set(vars1.keys()) | set(vars2.keys())
    
    for key in all_keys:
        if key not in vars1:
            variables_diff[key] = {'tipo': 'agregado', 'valor': vars2[key]}
        elif key not in vars2:
            variables_diff[key] = {'tipo': 'eliminado', 'valor': vars1[key]}
        elif vars1[key] != vars2[key]:
            variables_diff[key] = {
                'tipo': 'modificado',
                'valor_anterior': vars1[key],
                'valor_nuevo': vars2[key]
            }
    
    diferencias = {
        'contenido': {
            'diff': diff,
            'tiene_cambios': bool(diff)
        },
        'variables': {
            'diff': variables_diff,
            'tiene_cambios': bool(variables_diff)
        },
        'fecha_modificacion': {
            'v1': version1.fecha_modificacion.strftime('%d/%m/%Y %H:%M'),
            'v2': version2.fecha_modificacion.strftime('%d/%m/%Y %H:%M')
        },
        'medico_modificacion': {
            'v1': version1.medico_modificacion.nombre_completo,
            'v2': version2.medico_modificacion.nombre_completo
        },
        'motivo': {
            'v1': version1.motivo_modificacion,
            'v2': version2.motivo_modificacion
        }
    }
    
    return JsonResponse({'diferencias': diferencias})

@login_required
def ver_informe(request, informe_id):
    """Vista para ver un informe y su estado de firmas"""
    informe = get_object_or_404(Informe, id=informe_id)
    medico = request.user.medico
    
    # Verificar permisos básicos
    if not (informe.medico == medico or informe.operacion.medicos.filter(id=medico.id).exists()):
        raise PermissionDenied("No tienes permiso para ver este informe")
    
    # Determinar si puede firmar
    puede_firmar = False
    if informe.estado != 'FIRMADO':
        roles_disponibles = set(['PRINCIPAL', 'REVISOR', 'SUPERVISOR'])
        roles_firmados = set(informe.firmas.filter(medico=medico).values_list('rol', flat=True))
        puede_firmar = bool(roles_disponibles - roles_firmados)
    
    context = {
        'informe': informe,
        'puede_editar': informe.medico == medico and informe.estado != 'FIRMADO',
        'puede_firmar': puede_firmar,
    }
    return render(request, 'informes/ver_informe.html', context)

@login_required
@require_POST
def firmar_informe(request, informe_id):
    """Vista para procesar la firma de un informe"""
    informe = get_object_or_404(Informe, id=informe_id)
    medico = request.user.medico
    
    # Verificar que el médico puede firmar
    if informe.estado == 'FIRMADO':
        messages.error(request, "Este informe ya está firmado")
        return redirect('informes:ver_informe', informe_id=informe.id)
    
    # Obtener firma digital
    try:
        firma_digital = medico.firmadigital
    except FirmaDigital.DoesNotExist:
        messages.error(request, "No tienes una firma digital configurada")
        return redirect('informes:ver_informe', informe_id=informe.id)
    
    # Verificar PIN
    pin = request.POST.get('pin')
    verificado, mensaje = firma_digital.verificar_pin(pin)
    if not verificado:
        messages.error(request, mensaje)
        return redirect('informes:ver_informe', informe_id=informe.id)
    
    # Determinar rol de firma
    if informe.medico == medico:
        rol = 'PRINCIPAL'
    else:
        rol = 'REVISOR'
    
    # Crear firma
    try:
        FirmaInforme.objects.create(
            informe=informe,
            version=informe.versiones.last(),
            medico=medico,
            firma_digital=firma_digital,
            rol=rol,
            ip_firma=request.META.get('REMOTE_ADDR'),
            dispositivo=request.META.get('HTTP_USER_AGENT', '')
        )
        messages.success(request, "Informe firmado correctamente")
    except Exception as e:
        messages.error(request, f"Error al firmar el informe: {str(e)}")
    
    return redirect('informes:ver_informe', informe_id=informe.id)

@login_required
def verificar_firma(request, firma_id):
    """Vista para verificar la integridad de una firma"""
    firma = get_object_or_404(FirmaInforme, id=firma_id)
    
    # Verificar permisos
    if not (firma.informe.medico == request.user.medico or 
            firma.informe.operacion.medicos.filter(id=request.user.medico.id).exists()):
        raise PermissionDenied("No tienes permiso para verificar esta firma")
    
    verificacion = {
        'integridad': firma.verificar_integridad(),
        'fecha_firma': firma.fecha_firma,
        'medico': firma.medico.nombre_completo,
        'rol': firma.get_rol_display(),
        'dispositivo': firma.dispositivo,
        'ip': firma.ip_firma
    }
    
    return JsonResponse({'verificacion': verificacion})

@login_required
def verificar_integridad_firmas(request, informe_id):
    """Vista para verificar la integridad de todas las firmas de un informe"""
    informe = get_object_or_404(Informe, id=informe_id)
    
    # Verificar permisos
    if not (informe.medico == request.user.medico or 
            informe.operacion.medicos.filter(id=request.user.medico.id).exists()):
        raise PermissionDenied("No tienes permiso para verificar este informe")
    
    verificaciones = []
    for firma in informe.firmas.all():
        verificacion = {
            'medico': firma.medico.nombre_completo,
            'rol': firma.get_rol_display(),
            'fecha': firma.fecha_firma,
            'version': firma.version.version if firma.version else 'Original',
            'integridad': firma.verificar_integridad(),
            'dispositivo': firma.dispositivo,
            'ip': firma.ip_firma
        }
        verificaciones.append(verificacion)
    
    return JsonResponse({
        'estado_informe': informe.estado,
        'verificaciones': verificaciones,
        'ultima_modificacion': informe.versiones.last().fecha_modificacion if informe.versiones.exists() else informe.fecha_creacion
    })

@login_required
def exportar_registro_firmas(request, informe_id):
    """Vista para exportar el registro de firmas y verificaciones a PDF"""
    informe = get_object_or_404(Informe, id=informe_id)
    
    # Verificar permisos
    if not (informe.medico == request.user.medico or 
            informe.operacion.medicos.filter(id=request.user.medico.id).exists()):
        raise PermissionDenied("No tienes permiso para exportar este registro")
    
    # Generar el PDF usando el GeneradorPDF
    # Preparar contexto para el template
    context = {
        'informe': informe,
        'firmas': informe.firmas.all().select_related('medico', 'version'),
        'versiones': informe.versiones.all().select_related('medico_modificacion'),
        'fecha_generacion': timezone.now(),
        'generado_por': request.user.medico
    }
    
    # Crear respuesta HTTP con el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="registro_firmas_{informe.id}.pdf"'
    
    # Generar PDF
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Título del documento
    elements.append(Paragraph(f"Registro de Firmas: {informe.titulo}", styles['Title']))

    # Tabla de firmas
    data = [['Médico', 'Rol', 'Fecha', 'Versión', 'Integridad', 'Dispositivo', 'IP']]
    for firma in informe.firmas.all():
        data.append([
            firma.medico.nombre_completo,
            firma.get_rol_display(),
            firma.fecha_firma.strftime('%d/%m/%Y %H:%M'),
            firma.version.version if firma.version else 'Original',
            'Válida' if firma.verificar_integridad() else 'Inválida',
            firma.dispositivo,
            firma.ip_firma
        ])
    table = Table(data)
    table.setStyle(TableStyle([
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
    ]))
    elements.append(table)

    # Generar el PDF
    doc.build(elements)
    return response

@login_required
def generar_pdf_registro_firmas(request, informe_id):
    """
    Genera un PDF con el registro de firmas de un informe usando ReportLab.
    """
    try:
        # Obtener el informe
        informe = Informe.objects.get(id=informe_id)
        
        # Verificar permisos
        if not request.user.has_perm('informes.ver_informe'):
            return HttpResponseForbidden('No tiene permisos para ver este registro')
            
        # Obtener firmas y versiones
        firmas = FirmaInforme.objects.filter(informe=informe).order_by('-fecha_firma')
        versiones = VersionInforme.objects.filter(informe=informe).order_by('-fecha_creacion')
        
        # Crear un buffer para el PDF
        buffer = BytesIO()
        
        # Crear el objeto PDF
        pdf = canvas.Canvas(buffer, pagesize=letter)
        
        # Configurar el título del PDF
        pdf.setTitle(f"Registro de Firmas - Informe {informe_id}")
        
        # Agregar contenido al PDF
        pdf.drawString(100, 750, f"Registro de Firmas - Informe {informe_id}")
        pdf.drawString(100, 730, f"Fecha de generación: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        pdf.drawString(100, 710, f"Generado por: {request.user.get_full_name()}")
        
        # Espacio entre secciones
        y_position = 690
        
        # Agregar información del informe
        pdf.drawString(100, y_position, f"Informe: {informe.titulo}")
        y_position -= 20
        pdf.drawString(100, y_position, f"Descripción: {informe.descripcion}")
        y_position -= 30
        
        # Agregar firmas
        pdf.drawString(100, y_position, "Firmas:")
        y_position -= 20
        for firma in firmas:
            pdf.drawString(120, y_position, f"{firma.medico.nombre_completo} - {firma.fecha_firma.strftime('%Y-%m-%d %H:%M:%S')}")
            y_position -= 15
        
        # Agregar versiones
        pdf.drawString(100, y_position, "Versiones:")
        y_position -= 20
        for version in versiones:
            pdf.drawString(120, y_position, f"Versión {version.version} - {version.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')}")
            y_position -= 15
        
        # Finalizar el PDF
        pdf.showPage()
        pdf.save()
        
        # Obtener el contenido del buffer
        pdf_file = buffer.getvalue()
        buffer.close()
        
        # Generar respuesta HTTP con el PDF
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="registro_firmas_{informe_id}.pdf"'
        
        return response
        
    except Informe.DoesNotExist:
        return HttpResponseNotFound('Informe no encontrado')
    except Exception as e:
        return HttpResponseServerError(f'Error al generar el PDF: {str(e)}')

def generar_informe_pdf(request, pk):
    informe = get_object_or_404(Informe, pk=pk)
    generador = GeneradorPDF(informe)
    return generador.generar()

