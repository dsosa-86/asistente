from django.urls import path
from . import views

app_name = 'insumos_medicos'

urlpatterns = [
    # Definir las rutas aquí
    path('', views.lista_insumos_medicos, name='lista_insumos_medicos'),
    path('crear/', views.crear_insumo_medico, name='crear_insumo_medico'),
    path('<int:pk>/editar/', views.editar_insumo_medico, name='editar_insumo_medico'),
    path('<int:pk>/eliminar/', views.eliminar_insumo_medico, name='eliminar_insumo_medico'),
]
