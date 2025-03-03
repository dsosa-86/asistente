from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Consulta

@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'medico', 'fecha_hora', 'diagnostico')
    search_fields = ('paciente__nombre', 'medico__usuario__first_name')
    list_filter = ('fecha_hora', 'medico')
    date_hierarchy = 'fecha_hora'