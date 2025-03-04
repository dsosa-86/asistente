import pytest
from apps.pacientes.models import Paciente

@pytest.mark.django_db
def test_paciente_creation():
    paciente = Paciente.objects.create(
        nombre="Juan",
        apellido="Pérez",
        dni="12345678",
        telefono="123456789",
        email="juan@example.com"
    )
    assert paciente.nombre == "Juan"
    assert paciente.apellido == "Pérez"
    assert paciente.dni == "12345678"