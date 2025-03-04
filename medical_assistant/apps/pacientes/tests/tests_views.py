import pytest
from django.urls import reverse
from apps.pacientes.models import Paciente

@pytest.mark.django_db
def test_paciente_list_view(client):
    Paciente.objects.create(nombre="Juan", apellido="Pérez", dni="12345678")
    url = reverse('pacientes:lista_pacientes')
    response = client.get(url)
    assert response.status_code == 200
    assert "Juan" in str(response.content)