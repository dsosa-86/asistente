from django.apps import AppConfig

class NotificacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notificaciones'
    verbose_name = 'Notificaciones'

    def ready(self):
        """
        Método que se ejecuta cuando la aplicación está lista.
        Aquí podemos registrar señales y realizar otras inicializaciones.
        """
        pass 