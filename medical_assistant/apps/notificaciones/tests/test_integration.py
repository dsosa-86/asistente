from django.test import TestCase
from django.contrib.auth.models import User
from apps.notificaciones.models import Notificacion, ConfiguracionNotificacion
from apps.notificaciones.services import ServicioNotificaciones

class NotificacionIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.config = ConfiguracionNotificacion.objects.create(
            usuario=self.user,
            email_activo=True,
            sms_activo=True,
            sistema_activo=True,
            whatsapp_activo=True
        )

    def test_crear_y_enviar_notificacion_email(self):
        notificacion = ServicioNotificaciones.crear_notificacion(
            usuario=self.user,
            tipo='EMAIL',
            titulo='Test Email',
            mensaje='Este es un mensaje de prueba por email.'
        )
        self.assertIsNotNone(notificacion)
        self.assertEqual(notificacion.tipo, 'EMAIL')
        self.assertEqual(notificacion.estado, 'ENVIADO')

    def test_crear_y_enviar_notificacion_whatsapp(self):
        notificacion = ServicioNotificaciones.crear_notificacion(
            usuario=self.user,
            tipo='WHATSAPP',
            titulo='Test WhatsApp',
            mensaje='Este es un mensaje de prueba por WhatsApp.'
        )
        self.assertIsNotNone(notificacion)
        self.assertEqual(notificacion.tipo, 'WHATSAPP')
        self.assertEqual(notificacion.estado, 'ENVIADO')
