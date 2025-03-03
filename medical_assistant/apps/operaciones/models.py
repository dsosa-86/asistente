from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

# Create your models here.
from django.db import models
#from apps.pacientes.models import Paciente
from apps.usuarios.models import Medico
from apps.centros_medicos.models import CentroMedico


class TipoCirugia(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    duracion_estimada = models.DurationField()
    requiere_internacion = models.BooleanField(default=False)
    
    def __str__(self):
        return self.nombre

class ProcedimientoEspecifico(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo_cirugia = models.ForeignKey(TipoCirugia, on_delete=models.CASCADE)
    pasos = models.JSONField(default=list)
    
    def __str__(self):
        return f"{self.nombre} ({self.tipo_cirugia})"




class Operacion(models.Model):
    ESTADOS = [
        ('PROGRAMADA', 'Programada'),
        ('EN_CURSO', 'En Curso'),
        ('FINALIZADA', 'Finalizada'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    # Relaciones principales usando lazy relationships
    paciente = models.ForeignKey(
        'pacientes.Paciente',
        on_delete=models.PROTECT,
        related_name='operaciones'
    )
    tipo_cirugia = models.ForeignKey(
        TipoCirugia,
        on_delete=models.PROTECT
    )
    procedimiento_especifico = models.ForeignKey(
        ProcedimientoEspecifico,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Personal médico
    cirujano_principal = models.ForeignKey(
        'usuarios.Medico',
        on_delete=models.PROTECT,
        related_name='operaciones_como_cirujano'
    )
    anestesiologo = models.ForeignKey(
        'usuarios.Medico',
        on_delete=models.SET_NULL,
        null=True,
        related_name='operaciones_como_anestesiologo'
    )
    instrumentador = models.ForeignKey(
        'usuarios.Medico',
        on_delete=models.SET_NULL,
        null=True,
        related_name='operaciones_como_instrumentador'
    )
    
    # Información de la operación
    fecha_programada = models.DateTimeField()
    duracion_estimada = models.DurationField()
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='PROGRAMADA'
    )
    centro_medico = models.ForeignKey(
        'centros_medicos.CentroMedico',
        on_delete=models.PROTECT
    )
    quirofano = models.ForeignKey(
        'centros_medicos.Quirofano',
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Campos de seguimiento
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    notas_preoperatorias = models.TextField(blank=True)
    complicaciones = models.TextField(blank=True)
    
    def __str__(self):
        return f"Operación de {self.paciente} - {self.tipo_cirugia}"

    @property
    def fecha_operacion(self):
        return self.fecha_programada.date()

    @property
    def tipo_operacion(self):
        return self.tipo_cirugia.nombre


class Protocolo(models.Model):
    operacion = models.OneToOneField(
        Operacion,
        on_delete=models.CASCADE,
        related_name='protocolo'
    )
    medico_responsable = models.ForeignKey(
        'usuarios.Medico',
        on_delete=models.PROTECT
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    contenido = models.TextField()
    diagnostico = models.TextField()
    procedimiento = models.TextField()
    observaciones = models.TextField(blank=True)
    
    def __str__(self):
        return f"Protocolo - {self.operacion}"

class EquipoQuirurgico(models.Model):
    operacion = models.OneToOneField(
        Operacion,
        on_delete=models.CASCADE,
        related_name='equipo'
    )
    cirujanos_asistentes = models.ManyToManyField(
        'usuarios.Medico',
        related_name='asistencias_quirurgicas'
    )
    enfermeros = models.ManyToManyField(
        'Enfermero',
        related_name='operaciones'
    )
    
    def __str__(self):
        return f"Equipo - {self.operacion}"

class Enfermero(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    matricula = models.CharField(max_length=20)
    especialidad = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.apellido}, {self.nombre}"


class EstudioPrequirurgico(models.Model):
    TIPOS = [
        ('LABORATORIO', 'Laboratorio'),
        ('IMAGEN', 'Imagen'),
        ('CARDIOLOGIA', 'Cardiología'),
        ('OTROS', 'Otros')
    ]
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS)
    tipo_cirugia = models.ForeignKey(
        TipoCirugia,
        on_delete=models.CASCADE,
        related_name='estudios_requeridos'
    )
    es_obligatorio = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre

class PrequirurgicoPaciente(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('SOLICITADO', 'Solicitado'),
        ('REALIZADO', 'Realizado'),
        ('VENCIDO', 'Vencido'),
        ('CANCELADO', 'Cancelado')
    ]
    
    paciente = models.ForeignKey(
        'pacientes.Paciente',
        on_delete=models.CASCADE,
        related_name='estudios_prequirurgicos'
    )
    estudio = models.ForeignKey(
        EstudioPrequirurgico,
        on_delete=models.CASCADE
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='PENDIENTE'
    )
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_realizacion = models.DateField(null=True, blank=True)
    resultado = models.TextField(blank=True)
    archivo = models.FileField(
        upload_to='estudios_prequirurgicos/',
        null=True,
        blank=True
    )
    
    def __str__(self):
        return f"{self.estudio} - {self.paciente}"




"""
class Operacion(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    centro_medico = models.ForeignKey(CentroMedico, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    tipo_procedimiento = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Operación de {self.paciente} con {self.medico} el {self.fecha_hora}"

class Protocolo(models.Model):
    operacion = models.OneToOneField(Operacion, on_delete=models.CASCADE)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Protocolo para {self.operacion}"
"""

class PlantillaProtocolo(models.Model):
    nombre = models.CharField(max_length=100)
    tipo_cirugia = models.ForeignKey(
        TipoCirugia,
        on_delete=models.CASCADE,
        related_name='plantillas'
    )
    contenido = models.TextField()
    variables = models.JSONField(default=dict)
    
    def __str__(self):
        return f"Plantilla - {self.nombre}"