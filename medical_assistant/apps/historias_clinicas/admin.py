from django.contrib import admin
from .models import HistoriaClinica, Antecedente, EvolucionClinica, DocumentoClinico

class AntecedenteInline(admin.TabularInline):
    model = Antecedente
    extra = 1

class EvolucionClinicaInline(admin.StackedInline):
    model = EvolucionClinica
    extra = 0
    readonly_fields = ('fecha',)
    fields = ('tipo', 'medico', 'descripcion', 'consulta', 'operacion', 'proxima_revision')

class DocumentoClinicoInline(admin.TabularInline):
    model = DocumentoClinico
    extra = 1
    fields = ('tipo', 'titulo', 'fecha', 'archivo', 'medico', 'observaciones')

@admin.register(HistoriaClinica)
class HistoriaClinicaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'fecha_creacion', 'ultima_actualizacion', 'grupo_sanguineo')
    search_fields = ('paciente__nombre', 'paciente__apellido', 'paciente__dni')
    readonly_fields = ('fecha_creacion', 'ultima_actualizacion')
    inlines = [AntecedenteInline, EvolucionClinicaInline, DocumentoClinicoInline]
    fieldsets = (
        ('Información Básica', {
            'fields': ('paciente', 'grupo_sanguineo')
        }),
        ('Información Médica', {
            'fields': ('alergias', 'antecedentes_familiares', 'medicacion_actual')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'ultima_actualizacion'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Antecedente)
class AntecedenteAdmin(admin.ModelAdmin):
    list_display = ('historia_clinica', 'tipo', 'fecha', 'medico')
    list_filter = ('tipo', 'fecha', 'medico')
    search_fields = ('historia_clinica__paciente__nombre', 'historia_clinica__paciente__apellido', 'descripcion')
    date_hierarchy = 'fecha'

@admin.register(EvolucionClinica)
class EvolucionClinicaAdmin(admin.ModelAdmin):
    list_display = ('historia_clinica', 'tipo', 'fecha', 'medico', 'proxima_revision')
    list_filter = ('tipo', 'fecha', 'medico')
    search_fields = ('historia_clinica__paciente__nombre', 'historia_clinica__paciente__apellido', 'descripcion')
    date_hierarchy = 'fecha'
    readonly_fields = ('fecha',)

@admin.register(DocumentoClinico)
class DocumentoClinicoAdmin(admin.ModelAdmin):
    list_display = ('historia_clinica', 'tipo', 'titulo', 'fecha', 'medico')
    list_filter = ('tipo', 'fecha', 'medico')
    search_fields = ('historia_clinica__paciente__nombre', 'historia_clinica__paciente__apellido', 'titulo')
    date_hierarchy = 'fecha'
