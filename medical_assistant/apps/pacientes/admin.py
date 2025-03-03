from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Q
from .models import Paciente

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'dni', 'fecha_nacimiento_formateada', 'edad', 'obra_social', 'telefono', 'email', 'fecha_hora_ingreso', 'activo')
    search_fields = ('nombre', 'apellido', 'dni', 'email')
    list_filter = ('activo', 'obra_social', 'sanatorio')
    autocomplete_fields = ['obra_social', 'sanatorio', 'medico', 'derivado']
    readonly_fields = ('fecha_nacimiento_formateada', 'edad', 'fecha_hora_ingreso')

    fieldsets = (
        ('Información Personal', {
            'fields': ('usuario', 'nombre', 'apellido', 'dni', 'fecha_nacimiento')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email')
        }),
        ('Información Médica', {
            'fields': ('obra_social', 'medico', 'sanatorio', 'derivado', 'activo', 'notas')
        }),
    )

    def nombre_completo(self, obj):
        return f"{obj.apellido}, {obj.nombre}"
    nombre_completo.short_description = 'Nombre Completo'

    def fecha_nacimiento_formateada(self, obj):
        if obj.fecha_nacimiento:
            return obj.fecha_nacimiento.strftime("%d-%m-%Y")
        return '-'
    fecha_nacimiento_formateada.short_description = 'Fecha de Nacimiento'

    def edad(self, obj):
        if obj.fecha_nacimiento:
            return obj.calcular_edad()
        return '-'
    edad.short_description = 'Edad'

    def estado_autorizacion(self, obj):
        if obj.autorizacion:
            return format_html('<span style="color: green;">✔ Autorizado</span>')
        return format_html('<span style="color: red;">✘ Pendiente</span>')
    estado_autorizacion.short_description = 'Autorización'
