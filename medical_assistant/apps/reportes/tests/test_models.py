from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Reporte, Estadistica

class ReporteModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_crear_reporte(self):
        reporte = Reporte.objects.create(
            usuario=self.user,
            nombre='Reporte de Prueba',
            descripcion='Descripción del reporte de prueba',
            datos={}
        )
        self.assertEqual(str(reporte), 'Reporte de Prueba')

    def test_crear_estadistica(self):
        reporte = Reporte.objects.create(
            usuario=self.user,
            nombre='Reporte de Prueba',
            descripcion='Descripción del reporte de prueba',
            datos={}
        )
        estadistica = Estadistica.objects.create(
            reporte=reporte,
            nombre='Estadística de Prueba',
            valor=100.0,
            fecha='2023-10-10'
        )
        self.assertEqual(str(estadistica), 'Estadística de Prueba - 100.0')
