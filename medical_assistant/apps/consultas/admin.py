from django.contrib import admin
from .models import Consulta

@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'medico', 'fecha_hora', 'diagnostico')
    search_fields = ('paciente', 'medico')
    list_filter = ('fecha_hora', 'medico')
    date_hierarchy = 'fecha_hora'