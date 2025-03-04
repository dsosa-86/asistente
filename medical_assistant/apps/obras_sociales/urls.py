from django.urls import path
from . import views

app_name = 'obras_sociales'

urlpatterns = [
    # Definir las rutas aquí
    path('', views.lista_obras_sociales, name='lista_obras_sociales'),
    path('crear/', views.crear_obra_social, name='crear_obra_social'),
    path('<int:pk>/editar/', views.editar_obra_social, name='editar_obra_social'),
    path('<int:pk>/eliminar/', views.eliminar_obra_social, name='eliminar_obra_social'),
]
