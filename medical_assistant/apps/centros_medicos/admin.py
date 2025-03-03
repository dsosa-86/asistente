from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CentroMedico, Consultorio, HorarioAtencion, Quirofano, EquipamientoQuirofano, EquipamientoAlquilado, DisponibilidadQuirofano, ConvenioObraSocial

@admin.register(CentroMedico)
class CentroMedicoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'telefono', 'email', 'activo', 'horario_apertura', 'horario_cierre')
    search_fields = ('nombre', 'direccion')
    list_filter = ('activo',)
    ordering = ('nombre',)

@admin.register(ConvenioObraSocial)
class ConvenioObraSocialAdmin(admin.ModelAdmin):
    list_display = ('centro_medico', 'obra_social', 'codigo_prestador', 'fecha_inicio', 'fecha_fin', 'activo')
    search_fields = ('centro_medico__nombre', 'obra_social__nombre', 'codigo_prestador')
    list_filter = ('activo', 'obra_social')
    ordering = ('centro_medico', 'obra_social')

@admin.register(Consultorio)
class ConsultorioAdmin(admin.ModelAdmin):
    list_display = ('numero', 'centro_medico', 'piso', 'capacidad', 'activo')
    search_fields = ('numero', 'centro_medico__nombre')
    list_filter = ('centro_medico', 'activo')
    ordering = ('centro_medico', 'numero')

class HorarioAtencionInline(admin.TabularInline):
    model = HorarioAtencion
    extra = 1

@admin.register(Quirofano)
class QuirofanoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'centro_medico', 'tipo', 'piso', 'activo')
    search_fields = ('nombre', 'centro_medico__nombre')
    list_filter = ('tipo', 'centro_medico', 'activo')
    filter_horizontal = ('equipamiento_fijo',)
    ordering = ('centro_medico', 'nombre')

@admin.register(EquipamientoQuirofano)
class EquipamientoQuirofanoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'numero_serie', 'fecha_instalacion', 'fecha_proximo_mantenimiento', 'activo')
    search_fields = ('nombre', 'numero_serie')
    list_filter = ('activo',)
    ordering = ('nombre',)

@admin.register(EquipamientoAlquilado)
class EquipamientoAlquiladoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'quirofano', 'proveedor', 'fecha_inicio', 'fecha_fin', 'costo_diario')
    search_fields = ('nombre', 'proveedor', 'quirofano__nombre')
    list_filter = ('quirofano__centro_medico', 'quirofano')
    ordering = ('quirofano', 'nombre')

@admin.register(DisponibilidadQuirofano)
class DisponibilidadQuirofanoAdmin(admin.ModelAdmin):
    list_display = ('quirofano', 'dia_semana', 'hora_inicio', 'hora_fin')
    search_fields = ('quirofano__nombre',)
    list_filter = ('dia_semana', 'quirofano__centro_medico', 'quirofano')
    ordering = ('quirofano', 'dia_semana', 'hora_inicio')

# Agregar los horarios como inline en el admin de Consultorio
ConsultorioAdmin.inlines = [HorarioAtencionInline]

# apps/centros_medicos/admin.py
from django.contrib import admin
from .models import MedicoCentroMedico

@admin.register(MedicoCentroMedico)
class MedicoCentroMedicoAdmin(admin.ModelAdmin):
    list_display = ('medico', 'centro_medico', 'activo', 'fecha_inicio', 'fecha_fin')
    list_filter = ('activo', 'centro_medico', 'medico')
    search_fields = ('medico__usuario__first_name', 'medico__usuario__last_name', 'centro_medico__nombre')
    filter_horizontal = ('horarios',)
