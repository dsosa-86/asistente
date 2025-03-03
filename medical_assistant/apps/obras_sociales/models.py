from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class ObraSocial(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único de la obra social")
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    sitio_web = models.URLField(blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Obra Social"
        verbose_name_plural = "Obras Sociales"
        ordering = ['nombre']

class Plan(models.Model):
    obra_social = models.ForeignKey(ObraSocial, on_delete=models.CASCADE, related_name='planes')
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    requiere_autorizacion = models.BooleanField(default=True, help_text="¿Requiere autorización previa para procedimientos?")
    
    class Meta:
        unique_together = ['obra_social', 'codigo']
        ordering = ['obra_social', 'nombre']

    def __str__(self):
        return f"{self.obra_social.nombre} - {self.nombre}"

class Cobertura(models.Model):
    TIPO_PROCEDIMIENTO = [
        ('CONSULTA', 'Consulta Médica'),
        ('CIRUGIA', 'Cirugía'),
        ('PRACTICA', 'Práctica Médica'),
        ('ESTUDIO', 'Estudio Médico'),
    ]

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='coberturas')
    tipo_procedimiento = models.CharField(max_length=20, choices=TIPO_PROCEDIMIENTO)
    procedimiento = models.CharField(max_length=100)
    codigo_nomenclador = models.CharField(max_length=20, blank=True, null=True)
    porcentaje_cobertura = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    monto_maximo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cubre_medicamentos = models.BooleanField(default=False)
    porcentaje_medicamentos = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True
    )
    observaciones = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)

    class Meta:
        unique_together = ['plan', 'procedimiento']
        ordering = ['plan', 'tipo_procedimiento', 'procedimiento']

    def __str__(self):
        return f"{self.plan} - {self.procedimiento} ({self.porcentaje_cobertura}%)"

class Autorizacion(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
        ('VENCIDA', 'Vencida'),
    ]

    paciente = models.ForeignKey(
        'pacientes.Paciente',
        on_delete=models.CASCADE,
        related_name='autorizaciones_obra_social'
    )
    cobertura = models.ForeignKey(Cobertura, on_delete=models.CASCADE)
    numero_autorizacion = models.CharField(max_length=50, blank=True, null=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    documentacion_adjunta = models.FileField(upload_to='autorizaciones/', null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha_solicitud']
        verbose_name = "Autorización"
        verbose_name_plural = "Autorizaciones"

    def __str__(self):
        return f"Autorización {self.numero_autorizacion} - {self.paciente} - {self.cobertura}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.estado == 'APROBADA' and not self.numero_autorizacion:
            raise ValidationError('Una autorización aprobada debe tener número de autorización')