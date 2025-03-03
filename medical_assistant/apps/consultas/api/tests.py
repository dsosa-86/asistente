from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.pacientes.models import Paciente
from apps.usuarios.models import Medico
from ..models import Consulta

class ConsultaAPITests(APITestCase):
    def setUp(self):
        self.paciente = Paciente.objects.create(nombre='Paciente Test')
        self.medico = Medico.objects.create(usuario='Medico Test')
        self.consulta_data = {
            'paciente': self.paciente.id,
            'medico': self.medico.id,
            'fecha_hora': '2023-10-10T10:00:00Z',
            'diagnostico': 'Diagnostico Test',
            'tratamiento': 'Tratamiento Test'
        }
        self.consulta = Consulta.objects.create(
            paciente=self.paciente,
            medico=self.medico,
            fecha_hora='2023-10-10T10:00:00Z',
            diagnostico='Diagnostico Test',
            tratamiento='Tratamiento Test'
        )

    def test_listar_consultas(self):
        response = self.client.get(reverse('consulta-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_crear_consulta(self):
        response = self.client.post(reverse('consulta-list'), self.consulta_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_detalle_consulta(self):
        response = self.client.get(reverse('consulta-detail', kwargs={'pk': self.consulta.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_editar_consulta(self):
        nueva_data = {
            'paciente': self.paciente.id,
            'medico': self.medico.id,
            'fecha_hora': '2023-10-11T10:00:00Z',
            'diagnostico': 'Diagnostico Editado',
            'tratamiento': 'Tratamiento Editado'
        }
        response = self.client.put(reverse('consulta-detail', kwargs={'pk': self.consulta.pk}), nueva_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_eliminar_consulta(self):
        response = self.client.delete(reverse('consulta-detail', kwargs={'pk': self.consulta.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
