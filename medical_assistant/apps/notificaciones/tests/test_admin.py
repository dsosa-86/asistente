from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from ..models import Notificacion, ConfiguracionNotificacion, PlantillaNotificacion

class NotificacionAdminTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='admin', password='admin', email='admin@example.com')
        self.client.login(username='admin', password='admin')

    def test_notificacion_list_view(self):
        response = self.client.get(reverse('admin:notificaciones_notificacion_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_configuracion_notificacion_list_view(self):
        response = self.client.get(reverse('admin:notificaciones_configuracionnotificacion_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_plantilla_notificacion_list_view(self):
        response = self.client.get(reverse('admin:notificaciones_plantillanotificacion_changelist'))
        self.assertEqual(response.status_code, 200)
