from django.db import models
from django.core.exceptions import ValidationError
from apps.usuarios.models import Medico
from apps.obras_sociales.models import ObraSocial

class CentroMedico(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    obras_sociales = models.ManyToManyField(ObraSocial, through='ConvenioObraSocial')
    activo = models.BooleanField(default=True)
    horario_apertura = models.TimeField()
    horario_cierre = models.TimeField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Centro Médico"
        verbose_name_plural = "Centros Médicos"
        ordering = ['nombre']

class ConvenioObraSocial(models.Model):
    centro_medico = models.ForeignKey(CentroMedico, on_delete=models.CASCADE)
    obra_social = models.ForeignKey(ObraSocial, on_delete=models.CASCADE)
    codigo_prestador = models.CharField(max_length=50)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ['centro_medico', 'obra_social']
        verbose_name = "Convenio con Obra Social"
        verbose_name_plural = "Convenios con Obras Sociales"

    def __str__(self):
        return f"{self.centro_medico} - {self.obra_social}"

class Consultorio(models.Model):
    centro_medico = models.ForeignKey(CentroMedico, on_delete=models.CASCADE, related_name='consultorios')
    numero = models.CharField(max_length=10)
    descripcion = models.TextField(blank=True, null=True)
    piso = models.CharField(max_length=10, blank=True, null=True)
    capacidad = models.IntegerField(default=1)
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ['centro_medico', 'numero']
        ordering = ['centro_medico', 'numero']

    def __str__(self):
        return f"Consultorio {self.numero} - {self.centro_medico.nombre}"

class Quirofano(models.Model):
    TIPOS_QUIROFANO = [
        ('GENERAL', 'Quirófano General'),
        ('ESPECIALIZADO', 'Quirófano Especializado'),
        ('AMBULATORIO', 'Quirófano Ambulatorio'),
    ]

    centro_medico = models.ForeignKey(CentroMedico, on_delete=models.CASCADE, related_name='quirofanos')
    nombre = models.CharField(max_length=50)
    tipo = models.CharField(max_length=20, choices=TIPOS_QUIROFANO)
    descripcion = models.TextField(blank=True, null=True)
    piso = models.CharField(max_length=10)
    superficie = models.DecimalField(max_digits=6, decimal_places=2, help_text="Superficie en metros cuadrados")
    activo = models.BooleanField(default=True)
    equipamiento_fijo = models.ManyToManyField('EquipamientoQuirofano', blank=True)

    class Meta:
        verbose_name = "Quirófano"
        verbose_name_plural = "Quirófanos"
        ordering = ['centro_medico', 'nombre']

    def __str__(self):
        return f"Quirófano {self.nombre} - {self.centro_medico.nombre}"

class EquipamientoQuirofano(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    numero_serie = models.CharField(max_length=50, unique=True)
    fecha_instalacion = models.DateField()
    fecha_ultimo_mantenimiento = models.DateField()
    fecha_proximo_mantenimiento = models.DateField()
    activo = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Equipamiento de Quirófano"
        verbose_name_plural = "Equipamientos de Quirófano"

    def __str__(self):
        return f"{self.nombre} - {self.numero_serie}"

class EquipamientoAlquilado(models.Model):
    quirofano = models.ForeignKey(Quirofano, on_delete=models.CASCADE, related_name='equipamiento_alquilado')
    nombre = models.CharField(max_length=100)
    proveedor = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    costo_diario = models.DecimalField(max_digits=10, decimal_places=2)
    numero_contrato = models.CharField(max_length=50)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Equipamiento Alquilado"
        verbose_name_plural = "Equipamientos Alquilados"

    def __str__(self):
        return f"{self.nombre} - {self.quirofano}"

class HorarioAtencion(models.Model):
    consultorio = models.ForeignKey(Consultorio, on_delete=models.CASCADE)
    dia_semana = models.CharField(max_length=10, choices=[
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sábado', 'Sábado'),
        ('Domingo', 'Domingo'),
    ])
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def clean(self):
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError('La hora de inicio debe ser anterior a la hora de fin')
        if self.consultorio.centro_medico.horario_apertura > self.hora_inicio or \
           self.consultorio.centro_medico.horario_cierre < self.hora_fin:
            raise ValidationError('El horario debe estar dentro del horario del centro médico')

    def __str__(self):
        return f"{self.consultorio} - {self.dia_semana} ({self.hora_inicio} - {self.hora_fin})"

class DisponibilidadQuirofano(models.Model):
    quirofano = models.ForeignKey(Quirofano, on_delete=models.CASCADE, related_name='disponibilidades')
    dia_semana = models.CharField(max_length=10, choices=[
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sábado', 'Sábado'),
        ('Domingo', 'Domingo'),
    ])
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def clean(self):
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError('La hora de inicio debe ser anterior a la hora de fin')
        if self.quirofano.centro_medico.horario_apertura > self.hora_inicio or \
           self.quirofano.centro_medico.horario_cierre < self.hora_fin:
            raise ValidationError('El horario debe estar dentro del horario del centro médico')

    class Meta:
        verbose_name = "Disponibilidad de Quirófano"
        verbose_name_plural = "Disponibilidades de Quirófano"

    def __str__(self):
        return f"{self.quirofano} - {self.dia_semana} ({self.hora_inicio} - {self.hora_fin})"

# apps/centros_medicos/models.py
from django.db import models
from apps.usuarios.models import Medico

class MedicoCentroMedico(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='centros_medicos')
    centro_medico = models.ForeignKey(CentroMedico, on_delete=models.CASCADE, related_name='medicos')
    horarios = models.ManyToManyField(HorarioAtencion)
    activo = models.BooleanField(default=True)
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_fin = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Relación Médico-Centro Médico"
        verbose_name_plural = "Relaciones Médico-Centro Médico"
        unique_together = ['medico', 'centro_medico']  # Evita duplicados

    def __str__(self):
        return f"{self.medico} en {self.centro_medico}"
