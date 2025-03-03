from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Medico, Administrativo

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('rol', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'rol', 'telefono', 'direccion')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'especialidad', 'matricula')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'especialidad')
    list_filter = ('especialidad',)

@admin.register(Administrativo)
class AdministrativoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'departamento')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'departamento')
    list_filter = ('departamento',)

# apps/usuarios/admin.py
from django.contrib import admin
from .models import GestionAdministrativa

@admin.register(GestionAdministrativa)
class GestionAdministrativaAdmin(admin.ModelAdmin):
    list_display = ('administrativo', 'tipo_gestion', 'get_gestionado', 'activo')
    list_filter = ('tipo_gestion', 'activo')
    search_fields = ('administrativo__usuario__first_name', 'medico__usuario__first_name', 'centro_medico__nombre')

    def get_gestionado(self, obj):
        return obj.medico if obj.tipo_gestion == 'MEDICO' else obj.centro_medico
    get_gestionado.short_description = 'Gestiona a'
