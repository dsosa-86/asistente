from django.urls import path
from .views import cargar_excel, crear_paciente, listar_pacientes, editar_paciente

urlpatterns = [
    path('cargar-excel/', cargar_excel, name='cargar_excel'),
]