import pytest
from django.contrib.auth import get_user_model
from medical_assistant.apps.pacientes.models import Paciente

@pytest.mark.django_db
def test_crear_paciente():
    User = get_user_model()
    usuario = User.objects.create_user(username='testuser', password='testpass')
    paciente = Paciente.objects.create(
        usuario=usuario,
        dni='12345678',
        nombre='Juan',
        apellido='Perez',
        fecha_nacimiento='1980-01-01'
    )
    assert paciente.dni == '12345678'
    assert paciente.nombre == 'Juan'
    assert paciente.apellido == 'Perez'
    assert paciente.fecha_nacimiento == '1980-01-01'
