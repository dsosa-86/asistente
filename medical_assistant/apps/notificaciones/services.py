from django.conf import settings
from django.core.mail import send_mail
from django.template import Template, Context
from django.utils import timezone
from .models import Notificacion, ConfiguracionNotificacion, PlantillaNotificacion

class ServicioNotificaciones:
    @staticmethod
    def crear_notificacion(usuario, tipo, titulo, mensaje, prioridad='MEDIA', metadata=None):
        """
        Crea una nueva notificación y la envía según la configuración del usuario
        """
        # Verificar configuración del usuario
        config = ConfiguracionNotificacion.objects.get_or_create(usuario=usuario)[0]
        
        # Verificar si el usuario acepta este tipo de notificación
        if not ServicioNotificaciones._verificar_preferencias(config, tipo):
            return None
            
        # Verificar horario de envío
        if not ServicioNotificaciones._verificar_horario(config):
            return None
            
        # Crear la notificación
        notificacion = Notificacion.objects.create(
            usuario=usuario,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            prioridad=prioridad,
            metadata=metadata or {}
        )
        
        # Enviar la notificación según el tipo
        if tipo == 'EMAIL' and config.email_activo:
            ServicioNotificaciones._enviar_email(notificacion)
        elif tipo == 'SMS' and config.sms_activo:
            ServicioNotificaciones._enviar_sms(notificacion)
        elif tipo == 'SISTEMA' and config.sistema_activo:
            notificacion.marcar_como_enviado()
            
        return notificacion

    @staticmethod
    def crear_desde_plantilla(usuario, plantilla_nombre, contexto, prioridad='MEDIA'):
        """
        Crea una notificación usando una plantilla predefinida
        """
        try:
            plantilla = PlantillaNotificacion.objects.get(nombre=plantilla_nombre, activa=True)
            
            # Renderizar el contenido con el contexto
            template = Template(plantilla.contenido)
            context = Context(contexto)
            mensaje_renderizado = template.render(context)
            
            # Crear la notificación
            return ServicioNotificaciones.crear_notificacion(
                usuario=usuario,
                tipo=plantilla.tipo,
                titulo=plantilla.asunto,
                mensaje=mensaje_renderizado,
                prioridad=prioridad,
                metadata={'plantilla': plantilla_nombre, 'contexto': contexto}
            )
        except PlantillaNotificacion.DoesNotExist:
            return None

    @staticmethod
    def _verificar_preferencias(config, tipo):
        """Verifica si el usuario acepta este tipo de notificación"""
        if tipo == 'EMAIL':
            return config.email_activo
        elif tipo == 'SMS':
            return config.sms_activo
        elif tipo == 'SISTEMA':
            return config.sistema_activo
        return False

    @staticmethod
    def _verificar_horario(config):
        """Verifica si es un horario apropiado para enviar la notificación"""
        ahora = timezone.localtime()
        
        # Si solo días hábiles, verificar que no sea fin de semana
        if config.dias_habiles and ahora.weekday() >= 5:
            return False
            
        hora_actual = ahora.time()
        return config.horario_inicio <= hora_actual <= config.horario_fin

    @staticmethod
    def _enviar_email(notificacion):
        """Envía la notificación por correo electrónico"""
        try:
            send_mail(
                subject=notificacion.titulo,
                message=notificacion.mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notificacion.usuario.email],
                fail_silently=False,
            )
            notificacion.marcar_como_enviado()
        except Exception as e:
            notificacion.registrar_error(str(e))

    @staticmethod
    def _enviar_sms(notificacion):
        """
        Envía la notificación por SMS
        Implementar integración con servicio de SMS (por ejemplo, Twilio)
        """
        try:
            # Aquí iría la implementación del envío de SMS
            # Por ahora solo marcamos como enviado para testing
            notificacion.marcar_como_enviado()
        except Exception as e:
            notificacion.registrar_error(str(e))

    @staticmethod
    def obtener_notificaciones_pendientes(usuario):
        """Obtiene las notificaciones no leídas del usuario"""
        return Notificacion.objects.filter(
            usuario=usuario,
            estado__in=['ENVIADO', 'PENDIENTE']
        ).order_by('-prioridad', '-fecha_creacion')

    @staticmethod
    def marcar_como_leidas(usuario, notificacion_ids=None):
        """Marca como leídas las notificaciones especificadas o todas las del usuario"""
        queryset = Notificacion.objects.filter(usuario=usuario)
        if notificacion_ids:
            queryset = queryset.filter(id__in=notificacion_ids)
        queryset.update(
            estado='LEIDO',
            fecha_lectura=timezone.now()
        ) 