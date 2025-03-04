from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

from django.core.exceptions import ValidationError
from django.db.models import Q



class Usuario(AbstractUser):
    ROLES = [
        ('paciente', 'Paciente'),
        ('medico', 'Médico'),
        ('administrativo', 'Administrativo'),
    ]
    rol = models.CharField(max_length=20, choices=ROLES)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=255, blank=True)

    # Definir related_name únicos para evitar conflictos
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='usuarios_usuario_set',  # Nombre único
        related_query_name='usuario',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='usuarios_usuario_set',  # Nombre único
        related_query_name='usuario',
    )

    def __str__(self):
        return self.username

class Medico(models.Model):
    TIPOS = [
        ('CIRUJANO', 'Cirujano'),
        ('ANESTESIOLOGO', 'Anestesiólogo'),
        ('INSTRUMENTADOR', 'Instrumentador'),
    ]
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)
    especialidad = models.CharField(max_length=100)
    matricula = models.CharField(max_length=50)

    def __str__(self):
        return f"Dr. {self.usuario.get_full_name()}"

class Administrativo(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    departamento = models.CharField(max_length=100)

    def __str__(self):
        return self.usuario.get_full_name()
    
# apps/usuarios/models.py
class GestionAdministrativa(models.Model):
    TIPOS_GESTION = [
        ('MEDICO', 'Gestión para Médico'),
        ('CENTRO', 'Gestión para Centro Médico')
    ]
    
    administrativo = models.ForeignKey(Administrativo, on_delete=models.CASCADE, related_name='gestiones')
    tipo_gestion = models.CharField(max_length=20, choices=TIPOS_GESTION)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, null=True, blank=True, related_name='administrativos')
    centro_medico = models.ForeignKey('centros_medicos.CentroMedico', on_delete=models.CASCADE, null=True, blank=True, related_name='administrativos')
    activo = models.BooleanField(default=True)
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_fin = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Gestión Administrativa"
        verbose_name_plural = "Gestiones Administrativas"
        constraints = [
            models.CheckConstraint(
                condition=Q(
                    (Q(tipo_gestion='MEDICO') & Q(centro_medico__isnull=True) & Q(medico__isnull=False)) |
                    (Q(tipo_gestion='CENTRO') & Q(medico__isnull=True) & Q(centro_medico__isnull=False))
                ),
                name='gestion_tipo_valido'
            )
        ]

    def clean(self):
        if self.tipo_gestion == 'MEDICO' and not self.medico:
            raise ValidationError('Debe especificar un médico para la gestión de tipo Médico')
        if self.tipo_gestion == 'CENTRO' and not self.centro_medico:
            raise ValidationError('Debe especificar un centro médico para la gestión de tipo Centro')

    def __str__(self):
        return f"{self.administrativo} - {self.tipo_gestion}"
