from django.db import models
from apps.pacientes.models import Paciente
from apps.usuarios.models import Medico
from apps.centros_medicos.models import Consultorio

class Turno(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    consultorio = models.ForeignKey(Consultorio, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
    ])

    def __str__(self):
        return f"Turno de {self.paciente} con {self.medico} el {self.fecha_hora}"
