from django.db import models
from django.core.exceptions import ValidationError
from apps.pacientes.models import Paciente
from apps.usuarios.models import Medico
from apps.consultas.models import Consulta
from apps.operaciones.models import Operacion

class HistoriaClinica(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, related_name='historia_clinica')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    grupo_sanguineo = models.CharField(max_length=10, choices=[
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ], null=True, blank=True)
    alergias = models.TextField(blank=True, default="No reporta alergias")
    antecedentes_familiares = models.TextField(blank=True, default="Sin antecedentes relevantes")
    medicacion_actual = models.TextField(blank=True, default="No reporta medicación actual")
    
    def __str__(self):
        return f"Historia Clínica - {self.paciente}"

    class Meta:
        verbose_name = "Historia Clínica"
        verbose_name_plural = "Historias Clínicas"

class Antecedente(models.Model):
    TIPOS = [
        ('QUIRURGICO', 'Quirúrgico'),
        ('PATOLOGICO', 'Patológico'),
        ('TRAUMATOLOGICO', 'Traumatológico'),
        ('OTRO', 'Otro')
    ]
    
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE, related_name='antecedentes')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    descripcion = models.TextField()
    fecha = models.DateField()
    medico = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True, blank=True)
    documentacion_adjunta = models.FileField(upload_to='antecedentes/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.historia_clinica.paciente}"

class EvolucionClinica(models.Model):
    TIPOS = [
        ('CONSULTA', 'Evolución de Consulta'),
        ('OPERACION', 'Evolución Post-Quirúrgica'),
        ('SEGUIMIENTO', 'Seguimiento'),
    ]
    
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE, related_name='evoluciones')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    fecha = models.DateTimeField(auto_now_add=True)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    descripcion = models.TextField()
    consulta = models.ForeignKey(Consulta, on_delete=models.SET_NULL, null=True, blank=True)
    operacion = models.ForeignKey(Operacion, on_delete=models.SET_NULL, null=True, blank=True)
    proxima_revision = models.DateField(null=True, blank=True)
    
    def clean(self):
        if self.tipo == 'CONSULTA' and not self.consulta:
            raise ValidationError('Debe especificar la consulta relacionada')
        if self.tipo == 'OPERACION' and not self.operacion:
            raise ValidationError('Debe especificar la operación relacionada')
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.historia_clinica.paciente} - {self.fecha.strftime('%d/%m/%Y')}"

    class Meta:
        ordering = ['-fecha']

class DocumentoClinico(models.Model):
    TIPOS = [
        ('ESTUDIO', 'Estudio Médico'),
        ('INFORME', 'Informe'),
        ('RECETA', 'Receta'),
        ('CERTIFICADO', 'Certificado'),
        ('OTRO', 'Otro')
    ]
    
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    titulo = models.CharField(max_length=200)
    fecha = models.DateField()
    archivo = models.FileField(upload_to='documentos_clinicos/')
    medico = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True)
    observaciones = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.titulo} - {self.historia_clinica.paciente}"

    class Meta:
        ordering = ['-fecha']
