from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.consultas.api.views import ConsultaViewSet
from apps.pacientes.api.views import PacienteViewSet
from apps.usuarios.api.views import MedicoViewSet

router = DefaultRouter()
router.register(r'consultas', ConsultaViewSet)
router.register(r'pacientes', PacienteViewSet)
router.register(r'medicos', MedicoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
