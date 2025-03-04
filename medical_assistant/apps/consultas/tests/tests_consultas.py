from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.pacientes.models import Paciente
from apps.usuarios.models import Medico
from apps.consultas.models import Consulta
from apps.consultas.serializers import ConsultaSerializer

class ConsultaTests(TestCase):
    def setUp(self):
        self.client = APIClient()
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
        response = self.client.get(reverse('consultas:lista_consultas'))
        consultas = Consulta.objects.all()
        serializer = ConsultaSerializer(consultas, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_crear_consulta(self):
        response = self.client.post(reverse('consultas:crear_consulta'), self.consulta_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Consulta.objects.count(), 2)

    def test_detalle_consulta(self):
        response = self.client.get(reverse('consultas:detalle_consulta', kwargs={'pk': self.consulta.pk}))
        consulta = Consulta.objects.get(pk=self.consulta.pk)
        serializer = ConsultaSerializer(consulta)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_editar_consulta(self):
        nueva_data = {
            'paciente': self.paciente.id,
            'medico': self.medico.id,
            'fecha_hora': '2023-10-11T10:00:00Z',
            'diagnostico': 'Diagnostico Editado',
            'tratamiento': 'Tratamiento Editado'
        }
        response = self.client.post(reverse('consultas:editar_consulta', kwargs={'pk': self.consulta.pk}), nueva_data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.consulta.refresh_from_db()
        self.assertEqual(self.consulta.paciente.id, nueva_data['paciente'])
        self.assertEqual(self.consulta.medico.id, nueva_data['medico'])
        self.assertEqual(self.consulta.fecha_hora.isoformat(), nueva_data['fecha_hora'])
        self.assertEqual(self.consulta.diagnostico, nueva_data['diagnostico'])
        self.assertEqual(self.consulta.tratamiento, nueva_data['tratamiento'])

    def test_eliminar_consulta(self):
        response = self.client.delete(reverse('consultas:eliminar_consulta', kwargs={'pk': self.consulta.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Consulta.objects.count(), 0)
