from django.urls import path
from .views import listar_notificaciones, marcar_como_leida, configuracion_notificaciones

app_name = 'notificaciones'

urlpatterns = [
    path('', listar_notificaciones, name='listar_notificaciones'),
    path('configuracion/', configuracion_notificaciones, name='configuracion'),
    path('marcar_como_leida/<int:pk>/', marcar_como_leida, name='marcar_como_leida'),
]