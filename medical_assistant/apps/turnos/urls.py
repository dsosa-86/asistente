from django.urls import path
from . import views

app_name = 'turnos'

urlpatterns = [
    # Definir las rutas aquí
    path('', views.lista_turnos, name='lista_turnos'),
    path('crear/', views.crear_turno, name='crear_turno'),
    path('<int:pk>/editar/', views.editar_turno, name='editar_turno'),
    path('<int:pk>/eliminar/', views.eliminar_turno, name='eliminar_turno'),
]
