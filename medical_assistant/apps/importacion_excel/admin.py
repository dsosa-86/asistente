from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ExcelImport, MapeoColumnas, CorreccionDatos, ReglaCorreccion

@admin.register(ExcelImport)
class ExcelImportAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo_importacion', 'estado', 'usuario', 'fecha_subida', 
                   'registros_totales', 'registros_procesados', 'registros_con_error',
                   'acciones']
    list_filter = ['tipo_importacion', 'estado', 'fecha_subida']
    search_fields = ['usuario__username', 'usuario__email']
    readonly_fields = ['fecha_subida', 'fecha_procesamiento', 'registros_totales',
                      'registros_procesados', 'registros_con_error']
    
    def acciones(self, obj):
        """Botones de acción para cada importación"""
        botones = []
        
        # Botón para ver resultados
        if obj.estado != 'PENDIENTE':
            url_resultados = reverse('ver_resultados', args=[obj.pk])
            botones.append(f'<a class="button" href="{url_resultados}">Ver Resultados</a>')
        
        # Botón para descargar errores
        if obj.registros_con_error > 0:
            url_errores = reverse('descargar_errores', args=[obj.pk])
            botones.append(f'<a class="button" href="{url_errores}">Descargar Errores</a>')
        
        return format_html('&nbsp;'.join(botones))
    
    acciones.short_description = 'Acciones'

@admin.register(MapeoColumnas)
class MapeoColumnasAdmin(admin.ModelAdmin):
    list_display = ['nombre_columna_excel', 'campo_modelo', 'transformacion', 
                   'es_requerido']
    list_filter = ['transformacion', 'es_requerido']
    search_fields = ['nombre_columna_excel', 'campo_modelo']
    
    fieldsets = (
        (None, {
            'fields': ('nombre_columna_excel', 'campo_modelo', 'es_requerido')
        }),
        ('Transformación', {
            'fields': ('transformacion', 'funcion_transformacion'),
            'classes': ('collapse',)
        }),
        ('Validación', {
            'fields': ('validaciones', 'valor_defecto'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CorreccionDatos)
class CorreccionDatosAdmin(admin.ModelAdmin):
    list_display = ['importacion', 'campo', 'valor_original', 'valor_corregido', 
                   'usuario', 'fecha']
    list_filter = ['campo', 'fecha', 'usuario']
    search_fields = ['valor_original', 'valor_corregido', 'justificacion']
    readonly_fields = ['fecha']

@admin.register(ReglaCorreccion)
class ReglaCorreccionAdmin(admin.ModelAdmin):
    list_display = ['campo', 'patron_original', 'correccion', 'confianza', 
                   'veces_aplicada', 'activa']
    list_filter = ['campo', 'activa', 'fecha_creacion']
    search_fields = ['patron_original', 'correccion']
    readonly_fields = ['veces_aplicada', 'fecha_creacion', 'ultima_aplicacion']
    
    fieldsets = (
        (None, {
            'fields': ('campo', 'patron_original', 'correccion', 'activa')
        }),
        ('Estadísticas', {
            'fields': ('confianza', 'veces_aplicada', 'fecha_creacion', 
                      'ultima_aplicacion'),
            'classes': ('collapse',)
        }),
        ('Autoría', {
            'fields': ('creada_por',),
            'classes': ('collapse',)
        }),
    )
