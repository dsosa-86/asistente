import pytest
from django.urls import reverse
from apps.turnos.models import Turno
from apps.pacientes.models import Paciente
from apps.usuarios.models import Medico

@pytest.mark.django_db
def test_turno_list_view(client):
    paciente = Paciente.objects.create(nombre="Juan", apellido="Pérez")
    medico = Medico.objects.create(nombre="Dr. López")
    Turno.objects.create(paciente=paciente, medico=medico, fecha="2023-10-01", hora="10:00")
    url = reverse('turnos:lista_turnos')
    response = client.get(url)
    assert response.status_code == 200
    assert "Juan" in str(response.content)