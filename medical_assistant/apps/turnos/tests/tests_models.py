import pytest
from apps.turnos.models import Turno
from apps.pacientes.models import Paciente
from apps.usuarios.models import Medico

@pytest.mark.django_db
def test_turno_creation():
    paciente = Paciente.objects.create(nombre="Juan", apellido="Pérez")
    medico = Medico.objects.create(nombre="Dr. López")
    turno = Turno.objects.create(
        paciente=paciente,
        medico=medico,
        fecha="2023-10-01",
        hora="10:00"
    )
    assert turno.paciente.nombre == "Juan"
    assert turno.medico.nombre == "Dr. López"