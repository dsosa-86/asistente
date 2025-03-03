from django.urls import path, include
from .views import crear_consulta, listar_consultas, editar_consulta, eliminar_consulta

urlpatterns = [
    path('api/', include('apps.consultas.api.urls')),
    path('crear/', crear_consulta, name='crear_consulta'),
    path('listar/', listar_consultas, name='lista_consultas'),
    path('editar/<int:pk>/', editar_consulta, name='editar_consulta'),
    path('eliminar/<int:pk>/', eliminar_consulta, name='eliminar_consulta'),
]
