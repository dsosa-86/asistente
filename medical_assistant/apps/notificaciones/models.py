from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

class Notificacion(models.Model):
    TIPOS = [
        ('EMAIL', 'Correo Electrónico'),
        ('SMS', 'Mensaje de Texto'),
        ('SISTEMA', 'Notificación del Sistema'),
        ('WHATSAPP', 'Mensaje de WhatsApp'),
    ]
    
    ESTADOS = [
        ('PENDIENTE', 'Pendiente de Envío'),
        ('ENVIADO', 'Enviado'),
        ('ERROR', 'Error en el Envío'),
        ('LEIDO', 'Leído por el Usuario'),
    ]
    
    PRIORIDADES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50, choices=TIPOS)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='MEDIA')
    intentos = models.PositiveSmallIntegerField(default=0)
    error_mensaje = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.usuario} - {self.estado}"

    def marcar_como_enviado(self):
        self.estado = 'ENVIADO'
        self.fecha_envio = timezone.now()
        self.save()

    def marcar_como_leido(self):
        self.estado = 'LEIDO'
        self.fecha_lectura = timezone.now()
        self.save()

    def registrar_error(self, mensaje_error):
        self.estado = 'ERROR'
        self.error_mensaje = mensaje_error
        self.intentos += 1
        self.save()

class ConfiguracionNotificacion(models.Model):
    """
    Configuración de preferencias de notificaciones por usuario
    """
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='config_notificaciones')
    email_activo = models.BooleanField(default=True, help_text="Recibir notificaciones por correo")
    sms_activo = models.BooleanField(default=False, help_text="Recibir notificaciones por SMS")
    sistema_activo = models.BooleanField(default=True, help_text="Recibir notificaciones en el sistema")
    whatsapp_activo = models.BooleanField(default=False, help_text="Recibir notificaciones por WhatsApp")
    horario_inicio = models.TimeField(default='08:00', help_text="Hora de inicio para recibir notificaciones")
    horario_fin = models.TimeField(default='20:00', help_text="Hora de fin para recibir notificaciones")
    dias_habiles = models.BooleanField(default=True, help_text="Solo recibir notificaciones en días hábiles")

    class Meta:
        verbose_name = "Configuración de Notificaciones"
        verbose_name_plural = "Configuraciones de Notificaciones"

    def __str__(self):
        return f"Configuración de notificaciones - {self.usuario}"

class PlantillaNotificacion(models.Model):
    """
    Plantillas predefinidas para diferentes tipos de notificaciones
    """
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=Notificacion.TIPOS)
    asunto = models.CharField(max_length=200)
    contenido = models.TextField(help_text="Usa {{variable}} para campos dinámicos")
    variables = models.JSONField(help_text="Define las variables disponibles en formato {'nombre': 'descripción'}")
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Plantilla de Notificación"
        verbose_name_plural = "Plantillas de Notificaciones"

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"