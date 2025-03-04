from django.db import models
from django.conf import settings

class Reporte(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    datos = models.JSONField()

    def __str__(self):
        return self.nombre

class Estadistica(models.Model):
    reporte = models.ForeignKey(Reporte, on_delete=models.CASCADE, related_name='estadisticas')
    nombre = models.CharField(max_length=100)
    valor = models.FloatField()
    fecha = models.DateField()

    def __str__(self):
        return f"{self.nombre} - {self.valor}"
