from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import PacienteViewSet, PrequirurgicoPacienteViewSet

router = DefaultRouter()
router.register(r'pacientes', PacienteViewSet)
router.register(r'estudios-prequirurgicos', PrequirurgicoPacienteViewSet, basename='estudio-prequirurgico')

urlpatterns = [
    path('', include(router.urls)),
]