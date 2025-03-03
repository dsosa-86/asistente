from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Turno

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'medico', 'consultorio', 'fecha_hora', 'estado')
    search_fields = ('paciente__nombre', 'medico__usuario__first_name', 'consultorio__numero')
    list_filter = ('estado', 'fecha_hora', 'medico', 'consultorio__centro_medico')
    date_hierarchy = 'fecha_hora'