import pytest
from django.urls import reverse
from apps.usuarios.models import Usuario

@pytest.mark.django_db
def test_usuario_login_view(client):
    Usuario.objects.create_user(email="juan@example.com", password="password123")
    url = reverse('usuarios:login')
    response = client.post(url, {'email': 'juan@example.com', 'password': 'password123'})
    assert response.status_code == 302  # Redirección después del login