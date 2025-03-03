from django.test import TestCase
from django.contrib.auth.models import User
from .models import Paciente
from apps.usuarios.models import Usuario
from datetime import datetime

class PacienteTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            password='12345',
            rol='paciente'
        )
        self.paciente = Paciente.objects.create(
            usuario=self.usuario,
            dni='12345678',
            nombre='Juan',
            apellido='Pérez',
            fecha_nacimiento='1990-01-01'
        )

    def test_calcular_edad(self):
        edad_esperada = datetime.date.today().year - 1990
        self.assertEqual(self.paciente.calcular_edad(), edad_esperada)

    def test_fecha_nacimiento_formateada(self):
        self.assertEqual(self.paciente.fecha_nacimiento_formateada(), '01-01-1990')
