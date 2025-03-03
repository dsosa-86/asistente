from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Notificacion, ConfiguracionNotificacion

class NotificacionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_notificacion_str(self):
        notificacion = Notificacion.objects.create(
            usuario=self.user,
            tipo='EMAIL',
            mensaje='Mensaje de prueba',
            estado='ENVIADO'
        )
        self.assertEqual(str(notificacion), 'Correo Electrónico - Mensaje de prueba (Enviado)')

    def test_configuracion_notificacion_str(self):
        config = ConfiguracionNotificacion.objects.create(
            usuario=self.user,
            email_activo=True,
            sms_activo=True,
            sistema_activo=True,
            whatsapp_activo=True
        )
        self.assertEqual(str(config), f'Configuración de notificaciones - {self.user}')
