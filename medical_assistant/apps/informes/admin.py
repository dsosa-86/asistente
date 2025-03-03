from django.contrib import admin
from .models import PlantillaInforme, Informe, VariablePersonalizada, FirmaDigital, ProtocoloProcedimiento, ComponenteProcedimiento, VersionInforme

@admin.register(PlantillaInforme)
class PlantillaInformeAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'activa', 'creado_por', 'fecha_creacion')
    list_filter = ('tipo', 'activa', 'creado_por')
    search_fields = ('nombre', 'contenido')
    readonly_fields = ('fecha_creacion', 'ultima_modificacion')
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'tipo', 'activa', 'creado_por')
        }),
        ('Contenido', {
            'fields': ('contenido', 'variables')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'ultima_modificacion'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Informe)
class InformeAdmin(admin.ModelAdmin):
    list_display = ('plantilla', 'paciente', 'medico', 'estado', 'fecha_creacion', 'fecha_firma')
    list_filter = ('estado', 'plantilla__tipo', 'medico')
    search_fields = ('paciente__nombre', 'paciente__apellido', 'medico__usuario__first_name', 'contenido')
    readonly_fields = ('fecha_creacion',)
    date_hierarchy = 'fecha_creacion'
    fieldsets = (
        ('Información Básica', {
            'fields': ('plantilla', 'paciente', 'medico', 'estado')
        }),
        ('Contenido', {
            'fields': ('contenido', 'variables_utilizadas')
        }),
        ('Relaciones', {
            'fields': ('consulta', 'operacion')
        }),
        ('Documentación', {
            'fields': ('archivo_generado', 'fecha_firma')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Si es una nueva instancia
            obj.medico = request.user.medico  # Asigna el médico actual
        super().save_model(request, obj, form, change)

@admin.register(VariablePersonalizada)
class VariablePersonalizadaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'medico', 'activa')
    list_filter = ('activa', 'medico')
    search_fields = ('nombre', 'medico__usuario__first_name', 'valor_predeterminado')

@admin.register(FirmaDigital)
class FirmaDigitalAdmin(admin.ModelAdmin):
    list_display = ('medico', 'fecha_creacion', 'activa')
    list_filter = ('activa',)
    search_fields = ('medico__usuario__first_name', 'medico__usuario__last_name')
    readonly_fields = ('fecha_creacion',)
    fieldsets = (
        ('Médico', {
            'fields': ('medico', 'activa')
        }),
        ('Firma', {
            'fields': ('firma_imagen', 'certificado_digital')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )

class ComponenteProcedimientoInline(admin.TabularInline):
    model = ComponenteProcedimiento
    extra = 1
    fields = ('tipo', 'descripcion', 'diagnostico', 'orden')

@admin.register(ProtocoloProcedimiento)
class ProtocoloProcedimientoAdmin(admin.ModelAdmin):
    list_display = ('informe', 'tipo_guia', 'anestesiologo', 'estado_paciente', 'respuesta_procedimiento')
    list_filter = ('tipo_guia', 'estado_paciente', 'respuesta_procedimiento', 'requiere_recuperacion')
    search_fields = ('informe__paciente__nombre', 'informe__paciente__apellido', 'tecnica_utilizada')
    inlines = [ComponenteProcedimientoInline]
    fieldsets = (
        ('Información Básica', {
            'fields': ('informe', 'tipo_guia', 'anestesiologo', 'tipo_anestesia')
        }),
        ('Procedimiento', {
            'fields': ('tecnica_utilizada', 'materiales_utilizados', 'medicamentos_utilizados')
        }),
        ('Resultados', {
            'fields': ('complicaciones', 'estado_paciente', 'respuesta_procedimiento')
        }),
        ('Post-Procedimiento', {
            'fields': ('requiere_recuperacion', 'indicaciones_postprocedimiento', 'imagenes_adjuntas')
        }),
    )

@admin.register(VersionInforme)
class VersionInformeAdmin(admin.ModelAdmin):
    list_display = ('informe', 'version', 'medico_modificacion', 'fecha_modificacion')
    list_filter = ('medico_modificacion', 'fecha_modificacion')
    search_fields = ('informe__paciente__nombre', 'informe__paciente__apellido', 'motivo_modificacion')
    readonly_fields = ('version', 'fecha_modificacion')
    fieldsets = (
        ('Información Básica', {
            'fields': ('informe', 'medico_modificacion', 'version')
        }),
        ('Contenido', {
            'fields': ('contenido', 'variables_utilizadas')
        }),
        ('Detalles de Modificación', {
            'fields': ('motivo_modificacion', 'fecha_modificacion')
        }),
        ('Archivo', {
            'fields': ('archivo_generado',)
        }),
    )

    def has_add_permission(self, request):
        # Las versiones solo se deben crear a través de la interfaz de edición
        return False
