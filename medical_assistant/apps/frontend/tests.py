from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from apps.pacientes.models import Paciente
from apps.usuarios.models import Medico
from apps.consultas.models import Consulta

class FrontendTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.paciente = Paciente.objects.create(usuario=self.user, nombre='Paciente Test')
        self.medico = Medico.objects.create(usuario=self.user, nombre='Medico Test')
        self.consulta = Consulta.objects.create(paciente=self.paciente, medico=self.medico, fecha_hora='2023-10-10T10:00:00Z')

    def test_landing_page(self):
        response = self.client.get(reverse('landing_page'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_paciente(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('dashboard_paciente'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_administrativo(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('dashboard_administrativo'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_medico(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('dashboard_medico'))
        self.assertEqual(response.status_code, 200)
