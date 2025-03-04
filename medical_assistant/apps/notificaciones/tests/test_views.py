from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from apps.notificaciones.models import Notificacion, ConfiguracionNotificacion

class NotificacionViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.config = ConfiguracionNotificacion.objects.create(
            usuario=self.user,
            email_activo=True,
            sms_activo=True,
            sistema_activo=True,
            whatsapp_activo=True
        )

    def test_lista_notificaciones(self):
        response = self.client.get(reverse('notificaciones:listar_notificaciones'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notificaciones/lista.html')

    def test_configuracion_notificaciones(self):
        response = self.client.get(reverse('notificaciones:configuracion'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notificaciones/configuracion.html')

    def test_marcar_como_leida(self):
        notificacion = Notificacion.objects.create(
            usuario=self.user,
            tipo='EMAIL',
            mensaje='Mensaje de prueba',
            estado='ENVIADO'
        )
        response = self.client.post(reverse('notificaciones:marcar_como_leida', args=[notificacion.id]))
        self.assertRedirects(response, reverse('notificaciones:listar_notificaciones'))
        notificacion.refresh_from_db()
        self.assertEqual(notificacion.estado, 'LEIDO')
