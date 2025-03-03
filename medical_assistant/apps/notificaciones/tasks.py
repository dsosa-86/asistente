from celery import shared_task
from django.core.mail import send_mail
from .models import Notificacion
from .services import ServicioNotificaciones

@shared_task(bind=True, max_retries=3)
def enviar_notificacion_email(self, notificacion_id):
    try:
        notificacion = Notificacion.objects.get(id=notificacion_id)
        send_mail(
            'Nueva Notificación',
            notificacion.mensaje,
            'from@example.com',
            [notificacion.usuario.email],
            fail_silently=False,
        )
        notificacion.marcar_como_enviado()
    except Exception as exc:
        notificacion.registrar_error(str(exc))
        self.retry(exc=exc)

@shared_task(bind=True, max_retries=3)
def enviar_notificacion_whatsapp(self, notificacion_id):
    try:
        notificacion = Notificacion.objects.get(id=notificacion_id)
        ServicioNotificaciones._enviar_whatsapp(notificacion)
    except Exception as exc:
        notificacion.registrar_error(str(exc))
        self.retry(exc=exc)
