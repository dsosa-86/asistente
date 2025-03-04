import pytest
from apps.consultas.models import Consulta
from apps.pacientes.models import Paciente
from apps.usuarios.models import Medico

@pytest.mark.django_db
def test_consulta_creation():
    paciente = Paciente.objects.create(nombre="Juan", apellido="Pérez")
    medico = Medico.objects.create(nombre="Dr. López")
    consulta = Consulta.objects.create(
        paciente=paciente,
        medico=medico,
        fecha="2023-10-01",
        diagnostico="Resfriado común"
    )
    assert consulta.paciente.nombre == "Juan"
    assert consulta.medico.nombre == "Dr. López"