from django.contrib import admin
from .models import Notificacion, ConfiguracionNotificacion, PlantillaNotificacion

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'estado', 'fecha_creacion', 'prioridad')
    list_filter = ('tipo', 'estado', 'prioridad')
    search_fields = ('usuario__username', 'mensaje')

@admin.register(ConfiguracionNotificacion)
class ConfiguracionNotificacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'email_activo', 'sms_activo', 'sistema_activo', 'whatsapp_activo')
    search_fields = ('usuario__username',)

@admin.register(PlantillaNotificacion)
class PlantillaNotificacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'activa')
    list_filter = ('tipo', 'activa')
    search_fields = ('nombre', 'asunto')
