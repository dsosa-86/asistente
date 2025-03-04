from django.test import TestCase
from django.contrib.auth.models import User
from apps.notificaciones.models import Notificacion
from apps.notificaciones.tasks import enviar_notificacion_email, enviar_notificacion_whatsapp

class NotificacionTasksTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_enviar_notificacion_email(self):
        notificacion = Notificacion.objects.create(
            usuario=self.user,
            tipo='EMAIL',
            mensaje='Mensaje de prueba',
            estado='PENDIENTE'
        )
        enviar_notificacion_email(notificacion.id)
        notificacion.refresh_from_db()
        self.assertEqual(notificacion.estado, 'ENVIADO')

    def test_enviar_notificacion_whatsapp(self):
        notificacion = Notificacion.objects.create(
            usuario=self.user,
            tipo='WHATSAPP',
            mensaje='Mensaje de prueba',
            estado='PENDIENTE'
        )
        enviar_notificacion_whatsapp(notificacion.id)
        notificacion.refresh_from_db()
        self.assertEqual(notificacion.estado, 'ENVIADO')
