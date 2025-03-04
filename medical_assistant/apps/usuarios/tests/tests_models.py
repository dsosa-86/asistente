import pytest
from apps.usuarios.models import Usuario

@pytest.mark.django_db
def test_usuario_creation():
    usuario = Usuario.objects.create_user(
        email="juan@example.com",
        password="password123",
        nombre="Juan",
        apellido="Pérez"
    )
    assert usuario.email == "juan@example.com"
    assert usuario.nombre == "Juan"