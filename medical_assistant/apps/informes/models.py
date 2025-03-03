from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.usuarios.models import Medico
from apps.pacientes.models import Paciente
from apps.consultas.models import Consulta
from apps.operaciones.models import Operacion
from apps.insumos_medicos.models import MaterialQuirurgico, MedicamentoQuirurgico

class PlantillaInforme(models.Model):
    TIPOS = [
        ('CONSULTA', 'Informe de Consulta'),
        ('PROTOCOLO_PRE', 'Protocolo Pre-Quirúrgico'),
        ('PROTOCOLO_POST', 'Protocolo Post-Quirúrgico'),
        ('CERTIFICADO', 'Certificado Médico'),
        ('RECETA', 'Receta Médica'),
        ('DERIVACION', 'Informe de Derivación'),
    ]

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    contenido = models.TextField(help_text="Utilice {variables} para campos dinámicos")
    variables = models.JSONField(help_text="Define las variables disponibles en el formato {'nombre': 'descripción'}")
    activa = models.BooleanField(default=True)
    creado_por = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nombre}"

    class Meta:
        verbose_name = "Plantilla de Informe"
        verbose_name_plural = "Plantillas de Informes"
        unique_together = ['nombre', 'tipo']

class Informe(models.Model):
    ESTADOS = [
        ('BORRADOR', 'Borrador'),
        ('PENDIENTE_FIRMA', 'Pendiente de Firma'),
        ('FIRMADO', 'Firmado'),
        ('ANULADO', 'Anulado'),
    ]

    plantilla = models.ForeignKey(PlantillaInforme, on_delete=models.PROTECT)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_firma = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='BORRADOR')
    contenido = models.TextField()
    consulta = models.ForeignKey(Consulta, on_delete=models.SET_NULL, null=True, blank=True)
    operacion = models.ForeignKey(Operacion, on_delete=models.SET_NULL, null=True, blank=True)
    variables_utilizadas = models.JSONField()
    archivo_generado = models.FileField(upload_to='informes/', null=True, blank=True)
    
    def clean(self):
        if self.estado == 'FIRMADO' and not self.fecha_firma:
            raise ValidationError('Un informe firmado debe tener fecha de firma')
        if self.plantilla.tipo in ['PROTOCOLO_PRE', 'PROTOCOLO_POST'] and not self.operacion:
            raise ValidationError('Los protocolos quirúrgicos deben estar asociados a una operación')
        if self.plantilla.tipo == 'CONSULTA' and not self.consulta:
            raise ValidationError('Los informes de consulta deben estar asociados a una consulta')

    def __str__(self):
        return f"{self.plantilla.get_tipo_display()} - {self.paciente} - {self.fecha_creacion.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Informe"
        verbose_name_plural = "Informes"
        ordering = ['-fecha_creacion']

    def actualizar_estado_firmas(self):
        """Actualiza el estado del informe basado en las firmas requeridas"""
        firmas_requeridas = {
            'PROTOCOLO_PRE': ['PRINCIPAL'],
            'PROTOCOLO_POST': ['PRINCIPAL', 'REVISOR'],
            'CERTIFICADO': ['PRINCIPAL'],
            'RECETA': ['PRINCIPAL'],
        }
        
        tipo_informe = self.plantilla.tipo
        if tipo_informe not in firmas_requeridas:
            return
        
        roles_requeridos = set(firmas_requeridas[tipo_informe])
        roles_firmados = set(self.firmas.values_list('rol', flat=True))
        
        if roles_requeridos.issubset(roles_firmados):
            self.estado = 'FIRMADO'
            self.fecha_firma = timezone.now()
            self.save()

class VariablePersonalizada(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    valor_predeterminado = models.TextField()
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - Dr. {self.medico}"

    class Meta:
        verbose_name = "Variable Personalizada"
        verbose_name_plural = "Variables Personalizadas"
        unique_together = ['medico', 'nombre']

class FirmaDigital(models.Model):
    medico = models.OneToOneField(Medico, on_delete=models.CASCADE)
    firma_imagen = models.ImageField(upload_to='firmas/')
    certificado_digital = models.FileField(upload_to='certificados/', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    pin = models.CharField(max_length=128, help_text="PIN encriptado para validación de firma")
    intentos_fallidos = models.PositiveSmallIntegerField(default=0)
    bloqueada = models.BooleanField(default=False)
    ultima_actividad = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Firma Digital - Dr. {self.medico}"

    def verificar_pin(self, pin_ingresado):
        """Verifica el PIN ingresado y maneja los intentos fallidos"""
        from django.contrib.auth.hashers import check_password
        
        if self.bloqueada:
            return False, "Firma bloqueada por múltiples intentos fallidos"
        
        if check_password(pin_ingresado, self.pin):
            self.intentos_fallidos = 0
            self.save()
            return True, "PIN verificado correctamente"
        
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= 3:
            self.bloqueada = True
        self.save()
        return False, f"PIN incorrecto. Intentos restantes: {3 - self.intentos_fallidos}"

    def set_pin(self, pin):
        """Establece un nuevo PIN encriptado"""
        from django.contrib.auth.hashers import make_password
        self.pin = make_password(pin)
        self.intentos_fallidos = 0
        self.bloqueada = False
        self.save()

    class Meta:
        verbose_name = "Firma Digital"
        verbose_name_plural = "Firmas Digitales"

class VersionInforme(models.Model):
    """
    Mantiene un historial de versiones de los informes modificados.
    """
    informe = models.ForeignKey(Informe, on_delete=models.CASCADE, related_name='versiones')
    contenido = models.TextField()
    variables_utilizadas = models.JSONField()
    archivo_generado = models.FileField(upload_to='informes/versiones/', null=True, blank=True)
    medico_modificacion = models.ForeignKey(Medico, on_delete=models.PROTECT)
    fecha_modificacion = models.DateTimeField(auto_now_add=True)
    motivo_modificacion = models.TextField()
    version = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['-fecha_modificacion']
        unique_together = ['informe', 'version']
        verbose_name = "Versión de Informe"
        verbose_name_plural = "Versiones de Informes"

    def __str__(self):
        return f"V{self.version} - {self.informe} - {self.fecha_modificacion.strftime('%d/%m/%Y %H:%M')}"

    def save(self, *args, **kwargs):
        if not self.version:
            # Asignar siguiente número de versión
            ultima_version = VersionInforme.objects.filter(informe=self.informe).order_by('-version').first()
            self.version = (ultima_version.version + 1) if ultima_version else 1
        super().save(*args, **kwargs)

class FirmaInforme(models.Model):
    """
    Registro de firmas en informes, incluyendo versiones específicas
    """
    ROLES = [
        ('PRINCIPAL', 'Médico Principal'),
        ('REVISOR', 'Médico Revisor'),
        ('SUPERVISOR', 'Supervisor'),
    ]

    informe = models.ForeignKey(Informe, on_delete=models.CASCADE, related_name='firmas')
    version = models.ForeignKey(VersionInforme, on_delete=models.CASCADE, null=True, blank=True)
    medico = models.ForeignKey(Medico, on_delete=models.PROTECT)
    firma_digital = models.ForeignKey(FirmaDigital, on_delete=models.PROTECT)
    rol = models.CharField(max_length=20, choices=ROLES)
    fecha_firma = models.DateTimeField(auto_now_add=True)
    ip_firma = models.GenericIPAddressField(help_text="Dirección IP desde donde se firmó")
    dispositivo = models.CharField(max_length=200, help_text="Información del dispositivo usado para firmar")
    hash_documento = models.CharField(max_length=64, help_text="Hash SHA-256 del contenido firmado")
    
    def save(self, *args, **kwargs):
        if not self.hash_documento:
            self.generar_hash()
        super().save(*args, **kwargs)
        
        # Actualizar estado del informe si todas las firmas requeridas están presentes
        self.informe.actualizar_estado_firmas()

    def generar_hash(self):
        """Genera un hash del contenido del informe para verificación"""
        import hashlib
        contenido = self.informe.contenido
        if self.version:
            contenido = self.version.contenido
        self.hash_documento = hashlib.sha256(contenido.encode()).hexdigest()

    def verificar_integridad(self):
        """Verifica que el contenido no haya sido modificado después de la firma"""
        import hashlib
        contenido = self.informe.contenido
        if self.version:
            contenido = self.version.contenido
        hash_actual = hashlib.sha256(contenido.encode()).hexdigest()
        return hash_actual == self.hash_documento

    class Meta:
        verbose_name = "Firma de Informe"
        verbose_name_plural = "Firmas de Informes"
        unique_together = ['informe', 'medico', 'rol']
        ordering = ['fecha_firma']

class ProtocoloProcedimiento(models.Model):
    TIPOS_GUIA = [
        ('TAC', 'Tomografía Computada'),
        ('RX', 'Radiografía'),
        ('ECO', 'Ecografía'),
        ('RMN', 'Resonancia Magnética'),
    ]
    
    TIPOS_PROCEDIMIENTO = [
        ('BLOQUEO_FINO', 'Bloqueo Fino'),
        ('TERMOLESION', 'Termolesión'),
        ('INFILTRACION', 'Infiltración Simple'),
    ]
    
    ESTADOS_PACIENTE = [
        ('BUENO', 'Bueno'),
        ('REGULAR', 'Regular'),
        ('INESTABLE', 'Inestable'),
    ]
    
    RESPUESTAS = [
        ('FAVORABLE', 'Favorable'),
        ('PARCIAL', 'Parcial'),
        ('SIN_CAMBIOS', 'Sin Cambios'),
        ('DESFAVORABLE', 'Desfavorable'),
    ]

    informe = models.OneToOneField(Informe, on_delete=models.CASCADE, related_name='protocolo_procedimiento')
    tipo_procedimiento = models.CharField(max_length=20, choices=TIPOS_PROCEDIMIENTO)
    tipo_guia = models.CharField(max_length=20, choices=TIPOS_GUIA)
    anestesiologo = models.ForeignKey(Medico, on_delete=models.PROTECT, related_name='procedimientos_anestesia')
    tipo_anestesia = models.CharField(max_length=50)
    tecnica_utilizada = models.TextField()
    materiales_utilizados = models.TextField()
    medicamentos_utilizados = models.TextField()
    complicaciones = models.TextField(blank=True, default="No se presentan complicaciones inherentes al método.")
    estado_paciente = models.CharField(max_length=20, choices=ESTADOS_PACIENTE)
    respuesta_procedimiento = models.CharField(max_length=20, choices=RESPUESTAS)
    requiere_recuperacion = models.BooleanField(default=True)
    indicaciones_postprocedimiento = models.TextField()
    imagenes_adjuntas = models.BooleanField(default=True, help_text="Indica si se envían registros obtenidos")
    imagenes_pre = models.FileField(upload_to='protocolos/imagenes/pre/', null=True, blank=True)
    imagenes_post = models.FileField(upload_to='protocolos/imagenes/post/', null=True, blank=True)
    plantilla_pdf = models.CharField(max_length=50, default='default_template.html',
        help_text="Plantilla HTML para generar el PDF")
    estilo_pdf = models.CharField(max_length=50, default='default_style.css',
        help_text="Hoja de estilos CSS para el PDF")

    def get_template_name(self):
        """
        Retorna el nombre de la plantilla según el tipo de procedimiento
        """
        return f"{self.tipo_procedimiento.lower()}.html"

    def get_style_name(self):
        """
        Retorna el nombre del archivo CSS según el tipo de procedimiento
        """
        return f"{self.tipo_procedimiento.lower()}.css"

    def __str__(self):
        return f"Protocolo {self.informe.plantilla.nombre} - {self.informe.paciente}"

    def generar_pdf(self):
        """
        Genera el PDF del protocolo usando la plantilla y estilos especificados.
        La implementación detallada estará en utils.py
        """
        from .utils import GeneradorPDF
        return GeneradorPDF(self).generar()

    def get_siguiente_control(self):
        """
        Obtiene la fecha del próximo control programado
        """
        return self.seguimientos.filter(
            estado='PROGRAMADO',
            fecha_programada__gt=timezone.now()
        ).first()

    class Meta:
        verbose_name = "Protocolo de Procedimiento"
        verbose_name_plural = "Protocolos de Procedimientos"

class ComponenteProcedimiento(models.Model):
    """
    Permite definir componentes específicos del procedimiento,
    como tipos de bloqueos, niveles vertebrales, etc.
    """
    protocolo = models.ForeignKey(ProtocoloProcedimiento, on_delete=models.CASCADE, related_name='componentes')
    tipo = models.CharField(max_length=100)  # Ej: "BLOQUEO LUMBAR"
    descripcion = models.CharField(max_length=200)  # Ej: "L3/4 Y L4/5 DER"
    diagnostico = models.CharField(max_length=100)  # Ej: "LUMBALGIA"
    orden = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['orden']
        verbose_name = "Componente de Procedimiento"
        verbose_name_plural = "Componentes de Procedimiento"

    def __str__(self):
        return f"{self.tipo}: {self.descripcion}"

class MaterialProcedimiento(models.Model):
    """
    Registro de materiales específicos usados en el procedimiento.
    Ejemplo: agujas espinales, jeringas, etc.
    """
    protocolo = models.ForeignKey(ProtocoloProcedimiento, on_delete=models.CASCADE, related_name='materiales')
    material = models.ForeignKey(MaterialQuirurgico, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=8, decimal_places=2)
    especificaciones = models.CharField(max_length=100, blank=True, help_text="Ej: Calibre 21G, longitud 8.9cm")
    lote = models.CharField(max_length=50, blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.material.nombre} - {self.especificaciones}"

class MedicamentoProcedimiento(models.Model):
    """
    Registro de medicamentos utilizados en el procedimiento.
    Ejemplo: anestésicos, corticoides, etc.
    """
    protocolo = models.ForeignKey(ProtocoloProcedimiento, on_delete=models.CASCADE, related_name='medicamentos')
    medicamento = models.ForeignKey(MedicamentoQuirurgico, on_delete=models.PROTECT)
    dosis = models.CharField(max_length=50)
    via_administracion = models.CharField(max_length=50)
    lote = models.CharField(max_length=50, blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.medicamento.nombre} - {self.dosis}"

class FirmaProtocolo(models.Model):
    """
    Sistema detallado de firmas para protocolos, incluyendo múltiples firmantes
    y roles específicos.
    """
    ROLES = [
        ('PRINCIPAL', 'Médico Principal'),
        ('ANESTESIOLOGO', 'Anestesiólogo'),
        ('ASISTENTE', 'Médico Asistente'),
        ('INSTRUMENTADOR', 'Instrumentador'),
    ]

    protocolo = models.ForeignKey(ProtocoloProcedimiento, on_delete=models.CASCADE, related_name='firmas')
    medico = models.ForeignKey(Medico, on_delete=models.PROTECT)
    rol = models.CharField(max_length=20, choices=ROLES)
    firma_digital = models.ForeignKey(FirmaDigital, on_delete=models.PROTECT)
    fecha_firma = models.DateTimeField(auto_now_add=True)
    ip_firma = models.GenericIPAddressField(help_text="Dirección IP desde donde se firmó")
    dispositivo = models.CharField(max_length=200, help_text="Información del dispositivo usado para firmar")
    
    class Meta:
        unique_together = ['protocolo', 'medico', 'rol']
        ordering = ['fecha_firma']

class SeguimientoPostProcedimiento(models.Model):
    """
    Seguimiento posterior al procedimiento, incluyendo evolución
    y cumplimiento de indicaciones.
    """
    ESTADOS = [
        ('PROGRAMADO', 'Control Programado'),
        ('REALIZADO', 'Control Realizado'),
        ('CANCELADO', 'Control Cancelado'),
    ]

    protocolo = models.ForeignKey(ProtocoloProcedimiento, on_delete=models.CASCADE, related_name='seguimientos')
    fecha_programada = models.DateTimeField()
    fecha_realizado = models.DateTimeField(null=True, blank=True)
    medico = models.ForeignKey(Medico, on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PROGRAMADO')
    evolucion = models.TextField(blank=True)
    cumplimiento_indicaciones = models.TextField(blank=True)
    efectos_adversos = models.TextField(blank=True)
    requiere_nuevo_control = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['fecha_programada']

    def clean(self):
        if self.estado == 'REALIZADO' and not self.fecha_realizado:
            raise ValidationError('Un control realizado debe tener fecha de realización')

