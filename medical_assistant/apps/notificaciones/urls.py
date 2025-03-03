from django.urls import path
from . import views

app_name = 'notificaciones'

urlpatterns = [
    path('', views.lista_notificaciones, name='lista'),
    path('configuracion/', views.configuracion_notificaciones, name='configuracion'),
    path('marcar-leida/<int:notificacion_id>/', views.marcar_como_leida, name='marcar_leida'),
    path('marcar-todas-leidas/', views.marcar_todas_como_leidas, name='marcar_todas_leidas'),
    path('pendientes/', views.obtener_notificaciones_pendientes, name='pendientes'),
] 