from django.test import TestCase
from django.contrib.auth.models import User
from apps.usuarios.models import Usuario, Medico, Administrativo

class UsuarioTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            password='12345',
            rol='medico'
        )

    def test_crear_medico(self):
        medico = Medico.objects.create(
            usuario=self.usuario,
            tipo='CIRUJANO',
            especialidad='Cardiología',
            matricula='12345'
        )
        self.assertEqual(str(medico), f"Dr. {self.usuario.get_full_name()}")

    def test_crear_administrativo(self):
        administrativo = Administrativo.objects.create(
            usuario=self.usuario,
            departamento='Recepción'
        )
        self.assertEqual(str(administrativo), self.usuario.get_full_name())
