from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import MaterialQuirurgico, MedicamentoQuirurgico, UsoMaterial, UsoMedicamento

@admin.register(MaterialQuirurgico)
class MaterialQuirurgicoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'stock', 'unidad_medida', 'precio_unitario', 'activo')
    list_filter = ('tipo', 'activo')
    search_fields = ('nombre', 'descripcion', 'proveedor')
    list_editable = ('stock', 'precio_unitario')

@admin.register(MedicamentoQuirurgico)
class MedicamentoQuirurgicoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'principio_activo', 'concentracion', 'presentacion', 'stock', 'activo')
    list_filter = ('activo', 'via_administracion')
    search_fields = ('nombre', 'principio_activo', 'laboratorio')
    list_editable = ('stock',)

@admin.register(UsoMaterial)
class UsoMaterialAdmin(admin.ModelAdmin):
    list_display = ('operacion', 'material', 'cantidad_usada', 'fecha_uso')
    list_filter = ('fecha_uso', 'material')
    search_fields = ('operacion__id', 'material__nombre')

@admin.register(UsoMedicamento)
class UsoMedicamentoAdmin(admin.ModelAdmin):
    list_display = ('operacion', 'medicamento', 'dosis_aplicada', 'fecha_aplicacion')
    list_filter = ('fecha_aplicacion', 'medicamento')
    search_fields = ('operacion__id', 'medicamento__nombre')
