from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import Medico

class MedicoAPITests(APITestCase):
    def setUp(self):
        self.medico_data = {
            'usuario': 'Medico Test',
            'nombre': 'Medico Test'
        }
        self.medico = Medico.objects.create(**self.medico_data)

    def test_listar_medicos(self):
        response = self.client.get(reverse('medico-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_crear_medico(self):
        response = self.client.post(reverse('medico-list'), self.medico_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_detalle_medico(self):
        response = self.client.get(reverse('medico-detail', kwargs={'pk': self.medico.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_editar_medico(self):
        nueva_data = {
            'usuario': 'Medico Editado',
            'nombre': 'Medico Editado'
        }
        response = self.client.put(reverse('medico-detail', kwargs={'pk': self.medico.pk}), nueva_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_eliminar_medico(self):
        response = self.client.delete(reverse('medico-detail', kwargs={'pk': self.medico.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
