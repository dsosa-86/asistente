from celery import shared_task
from .models import Reporte, Estadistica
from django.utils import timezone

@shared_task
def generar_reporte(usuario_id, nombre, descripcion, datos):
    reporte = Reporte.objects.create(
        usuario_id=usuario_id,
        nombre=nombre,
        descripcion=descripcion,
        datos=datos
    )
    # Generar estadísticas de ejemplo
    for i in range(5):
        Estadistica.objects.create(
            reporte=reporte,
            nombre=f'Estadística {i+1}',
            valor=i * 10.0,
            fecha=timezone.now().date()
        )
    return reporte.id
