from django.db import models
from apps.pacientes.models import Paciente
from apps.usuarios.models import Medico

class Consulta(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    diagnostico = models.TextField()
    tratamiento = models.TextField()

    def __str__(self):
        return f'{self.paciente} - {self.medico} - {self.fecha_hora}'
