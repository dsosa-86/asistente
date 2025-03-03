from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from datetime import date
from apps.obras_sociales.models import ObraSocial
from apps.centros_medicos.models import CentroMedico
from apps.usuarios.models import Medico, Usuario
from django.utils.translation import gettext_lazy as _

def validar_dni(value):
    if not value.isdigit():
        raise ValidationError("El DNI debe contener solo números.")

def validar_telefono(value):
    if not value.replace('+', '').replace('-', '').isdigit():
        raise ValidationError("El teléfono debe contener solo números, '+' y '-'.")

class Paciente(models.Model):
    # Campos básicos
    usuario = models.OneToOneField('usuarios.Usuario', on_delete=models.CASCADE)
    dni = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    fecha_hora_ingreso = models.DateTimeField(auto_now_add=True)
    
    # Relaciones con otras entidades usando lazy relationships
    medico = models.ForeignKey(
        'usuarios.Medico',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pacientes'
    )
    obra_social = models.ForeignKey(
        'obras_sociales.ObraSocial',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pacientes'
    )
    sanatorio = models.ForeignKey(
        'centros_medicos.CentroMedico',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pacientes'
    )
    derivado = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derivados'
    )
    
    # Campos de estado y seguimiento
    activo = models.BooleanField(default=True)
    notas = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _("Paciente")
        verbose_name_plural = _("Pacientes")
        indexes = [
            models.Index(fields=['dni']),
            models.Index(fields=['apellido']),
            models.Index(fields=['fecha_hora_ingreso']),
        ]

    def __str__(self):
        return f"{self.apellido}, {self.nombre} (DNI: {self.dni})"

    def clean(self):
        if not self.dni:
            raise ValidationError(_('El DNI es obligatorio'))
        if not self.nombre or not self.apellido:
            raise ValidationError(_('El nombre y apellido son obligatorios'))

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('pacientes:detalle', args=[str(self.id)])

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def tiene_obra_social(self):
        return bool(self.obra_social)

    def esta_derivado(self):
        return bool(self.derivado)

    def get_historial_medico(self):
        return {
            'consultas': self.consultas.all(),
            'operaciones': self.operaciones.all(),
            'turnos': self.turnos.all(),
        }

    def calcular_edad(self):
        today = date.today()
        return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))

    def fecha_nacimiento_formateada(self):
        return self.fecha_nacimiento.strftime("%d-%m-%Y")
