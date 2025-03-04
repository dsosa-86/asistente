from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Definir las rutas aquí
    path('', views.lista_usuarios, name='lista_usuarios'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path('<int:pk>/editar/', views.editar_usuario, name='editar_usuario'),
    path('<int:pk>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
]
