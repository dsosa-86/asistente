from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import ObraSocial, Plan, Cobertura, Autorizacion

@admin.register(ObraSocial)
class ObraSocialAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'telefono', 'email', 'activa')
    search_fields = ('nombre', 'codigo', 'telefono')
    list_filter = ('activa',)
    ordering = ('nombre',)

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('obra_social', 'nombre', 'codigo', 'activo', 'requiere_autorizacion')
    search_fields = ('nombre', 'codigo', 'obra_social__nombre')
    list_filter = ('activo', 'requiere_autorizacion', 'obra_social')
    ordering = ('obra_social', 'nombre')

@admin.register(Cobertura)
class CoberturaAdmin(admin.ModelAdmin):
    list_display = ('plan', 'tipo_procedimiento', 'procedimiento', 'porcentaje_cobertura', 'activa')
    search_fields = ('procedimiento', 'plan__nombre', 'plan__obra_social__nombre')
    list_filter = ('tipo_procedimiento', 'activa', 'plan__obra_social', 'plan')
    ordering = ('plan', 'tipo_procedimiento', 'procedimiento')
    list_editable = ('porcentaje_cobertura', 'activa')

@admin.register(Autorizacion)
class AutorizacionAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'cobertura', 'numero_autorizacion', 'estado', 'fecha_solicitud', 'fecha_vencimiento')
    search_fields = ('paciente__nombre', 'paciente__apellido', 'numero_autorizacion')
    list_filter = ('estado', 'cobertura__plan__obra_social', 'fecha_solicitud')
    ordering = ('-fecha_solicitud',)
    readonly_fields = ('fecha_solicitud',)
    date_hierarchy = 'fecha_solicitud'