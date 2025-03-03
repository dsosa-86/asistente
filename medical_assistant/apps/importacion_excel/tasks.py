from celery import shared_task
from django.core.cache import cache
from .models import ExcelImport
from .utils import ProcesadorExcel
import time
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

@shared_task(bind=True, max_retries=3)
def procesar_archivo_excel(self, import_id):
    """Tarea para procesar archivos Excel de forma asíncrona"""
    try:
        # Obtener la importación
        importacion = ExcelImport.objects.get(id=import_id)
        
        # Actualizar estado
        importacion.estado = 'EN_PROCESO'
        importacion.save()
        
        # Inicializar procesador
        procesador = ProcesadorExcel(import_id)
        
        # Procesar archivo
        exitoso = procesador.procesar_archivo()
        
        if exitoso:
            # Guardar datos procesados
            procesador.guardar_datos()
            
            # Generar reporte
            reporte = procesador.generar_reporte()
            
            # Actualizar estadísticas
            importacion.actualizar_estadisticas()
            
            # Notificar al usuario
            if importacion.usuario.email:
                enviar_notificacion_exito.delay(import_id)
        else:
            # Notificar errores
            if importacion.usuario.email:
                enviar_notificacion_error.delay(import_id)
        
        return exitoso

    except ExcelImport.DoesNotExist:
        return False
    except Exception as exc:
        # Reintentar en caso de error
        self.retry(exc=exc, countdown=60)  # Reintento en 1 minuto

@shared_task
def enviar_notificacion_exito(import_id):
    """Envía notificación de éxito por email"""
    try:
        importacion = ExcelImport.objects.get(id=import_id)
        
        # Renderizar template de email
        context = {
            'importacion': importacion,
            'url_resultados': reverse('importacion_excel:ver_resultados', args=[import_id])
        }
        html_message = render_to_string('importacion_excel/emails/importacion_exitosa.html', context)
        
        # Enviar email
        send_mail(
            subject='Importación Completada con Éxito',
            message='Su archivo ha sido procesado exitosamente.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[importacion.usuario.email],
            html_message=html_message
        )
    except ExcelImport.DoesNotExist:
        pass

@shared_task
def enviar_notificacion_error(import_id):
    """Envía notificación de error por email"""
    try:
        importacion = ExcelImport.objects.get(id=import_id)
        
        # Renderizar template de email
        context = {
            'importacion': importacion,
            'url_errores': reverse('importacion_excel:descargar_errores', args=[import_id])
        }
        html_message = render_to_string('importacion_excel/emails/importacion_error.html', context)
        
        # Enviar email
        send_mail(
            subject='Error en la Importación',
            message='Se encontraron errores al procesar su archivo.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[importacion.usuario.email],
            html_message=html_message
        )
    except ExcelImport.DoesNotExist:
        pass

@shared_task
def limpiar_archivos_temporales():
    """Limpia archivos temporales antiguos"""
    from django.utils import timezone
    from datetime import timedelta
    import os
    
    # Eliminar importaciones antiguas (más de 7 días)
    fecha_limite = timezone.now() - timedelta(days=7)
    importaciones_antiguas = ExcelImport.objects.filter(
        fecha_subida__lt=fecha_limite,
        estado__in=['ERROR', 'IMPORTADO']
    )
    
    for importacion in importaciones_antiguas:
        # Eliminar archivo físico
        if importacion.archivo and os.path.exists(importacion.archivo.path):
            os.remove(importacion.archivo.path)
        
        # Eliminar registro
        importacion.delete()

@shared_task
def actualizar_cache_validaciones():
    """Actualiza el caché de validaciones"""
    from .validators import ValidadorExcel
    
    validador = ValidadorExcel()
    validador._inicializar_cache()
    
    # Guardar en cache por 1 hora
    cache.set('validaciones_excel', {
        'dnis_existentes': list(validador.cache['dnis_existentes']),
        'medicos': validador.cache['medicos'],
        'obras_sociales': validador.cache['obras_sociales'],
        'centros_medicos': validador.cache['centros_medicos']
    }, timeout=3600) 