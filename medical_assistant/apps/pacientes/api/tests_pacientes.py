from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.pacientes.models import Paciente

class PacienteAPITests(APITestCase):
    def setUp(self):
        self.paciente_data = {
            'nombre': 'Paciente Test',
            'dni': '12345678',
            'obra_social': 'Obra Social Test'
        }
        self.paciente = Paciente.objects.create(**self.paciente_data)

    def test_listar_pacientes(self):
        response = self.client.get(reverse('paciente-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_crear_paciente(self):
        response = self.client.post(reverse('paciente-list'), self.paciente_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_detalle_paciente(self):
        response = self.client.get(reverse('paciente-detail', kwargs={'pk': self.paciente.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_editar_paciente(self):
        nueva_data = {
            'nombre': 'Paciente Editado',
            'dni': '87654321',
            'obra_social': 'Obra Social Editada'
        }
        response = self.client.put(reverse('paciente-detail', kwargs={'pk': self.paciente.pk}), nueva_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_eliminar_paciente(self):
        response = self.client.delete(reverse('paciente-detail', kwargs={'pk': self.paciente.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
