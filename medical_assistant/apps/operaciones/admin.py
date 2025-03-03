from django.contrib import admin
from .models import (
    Operacion, Protocolo, PlantillaProtocolo, 
    EquipoQuirurgico, Enfermero, TipoCirugia,
    ProcedimientoEspecifico, EstudioPrequirurgico,
    PrequirurgicoPaciente
)

@admin.register(Operacion)
class OperacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'cirujano_principal', 'fecha_programada', 'estado')
    list_filter = ('estado', 'tipo_cirugia', 'fecha_programada')
    search_fields = ('paciente__nombre', 'paciente__apellido', 'cirujano_principal__usuario__first_name')
    date_hierarchy = 'fecha_programada'
    fieldsets = (
        ('Información Principal', {
            'fields': ('paciente', 'tipo_cirugia', 'procedimiento_especifico')
        }),
        ('Personal Médico', {
            'fields': ('cirujano_principal', 'anestesiologo', 'instrumentador')
        }),
        ('Programación', {
            'fields': ('fecha_programada', 'duracion_estimada', 'estado', 'centro_medico', 'quirofano')
        }),
        ('Seguimiento', {
            'fields': ('fecha_inicio', 'fecha_fin', 'notas_preoperatorias', 'complicaciones')
        }),
    )

@admin.register(Protocolo)
class ProtocoloAdmin(admin.ModelAdmin):
    list_display = ('operacion', 'medico_responsable', 'fecha_creacion')
    search_fields = ('operacion__paciente__nombre', 'operacion__cirujano_principal__usuario__first_name')
    list_filter = ('fecha_creacion',)
    date_hierarchy = 'fecha_creacion'
    fields = ('operacion', 'medico_responsable', 'contenido', 'diagnostico', 'procedimiento', 'observaciones')

@admin.register(PlantillaProtocolo)
class PlantillaProtocoloAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_cirugia')
    search_fields = ('nombre', 'contenido')
    list_filter = ('tipo_cirugia',)
    fields = ('nombre', 'tipo_cirugia', 'contenido', 'variables')

@admin.register(EquipoQuirurgico)
class EquipoQuirurgicoAdmin(admin.ModelAdmin):
    list_display = ('operacion',)
    filter_horizontal = ('cirujanos_asistentes', 'enfermeros')

@admin.register(Enfermero)
class EnfermeroAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'matricula', 'especialidad')
    search_fields = ('nombre', 'apellido', 'matricula')

@admin.register(TipoCirugia)
class TipoCirugiaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'requiere_internacion', 'duracion_estimada')
    search_fields = ('nombre', 'descripcion')
    fields = ('nombre', 'descripcion', 'duracion_estimada', 'requiere_internacion')

@admin.register(ProcedimientoEspecifico)
class ProcedimientoEspecificoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_cirugia', 'descripcion')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('tipo_cirugia',)
    fields = ('nombre', 'descripcion', 'tipo_cirugia', 'pasos')

@admin.register(EstudioPrequirurgico)
class EstudioPrequirurgicoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'tipo_cirugia', 'es_obligatorio')
    list_filter = ('tipo', 'es_obligatorio', 'tipo_cirugia')
    search_fields = ('nombre', 'descripcion')
    fields = ('nombre', 'descripcion', 'tipo', 'tipo_cirugia', 'es_obligatorio')

@admin.register(PrequirurgicoPaciente)
class PrequirurgicoPacienteAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'estudio', 'estado', 'fecha_realizacion')
    list_filter = ('estado', 'estudio__tipo')
    search_fields = ('paciente__nombre', 'paciente__apellido', 'estudio__nombre')
    date_hierarchy = 'fecha_realizacion'
    fields = ('paciente', 'estudio', 'estado', 'fecha_realizacion', 'resultado', 'archivo')
