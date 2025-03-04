import pytest
from django.urls import reverse
from apps.consultas.models import Consulta
from apps.pacientes.models import Paciente
from apps.usuarios.models import Medico

@pytest.mark.django_db
def test_consulta_detail_view(client):
    paciente = Paciente.objects.create(nombre="Juan", apellido="Pérez")
    medico = Medico.objects.create(nombre="Dr. López")
    consulta = Consulta.objects.create(paciente=paciente, medico=medico, fecha="2023-10-01", diagnostico="Resfriado común")
    url = reverse('consultas:detalle_consulta', args=[consulta.id])
    response = client.get(url)
    assert response.status_code == 200
    assert "Resfriado común" in str(response.content)