from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class ExcelImport(models.Model):
    TIPOS_IMPORTACION = [
        ('AGENDA', 'Importación de Agenda'),
        ('HISTORICOS', 'Datos Históricos'),
    ]
    
    ESTADOS = [
        ('PENDIENTE', 'Pendiente de Revisión'),
        ('EN_REVISION', 'En Revisión'),
        ('CORREGIDO', 'Datos Corregidos'),
        ('IMPORTADO', 'Importado'),
        ('ERROR', 'Error en Importación')
    ]

    archivo = models.FileField(
        upload_to='excel_imports/',
        help_text="Archivo Excel (.xlsx, .xls) con los datos a importar"
    )
    tipo_importacion = models.CharField(
        max_length=20, 
        choices=TIPOS_IMPORTACION,
        default='HISTORICOS',
        help_text="Tipo de datos que contiene el archivo"
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS, 
        default='PENDIENTE'
    )
    usuario = models.ForeignKey(
        'usuarios.Usuario', 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Usuario que realiza la importación"
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    fecha_procesamiento = models.DateTimeField(null=True, blank=True)
    registros_totales = models.IntegerField(default=0)
    registros_procesados = models.IntegerField(default=0)
    registros_con_error = models.IntegerField(default=0)
    log_procesamiento = models.JSONField(
        null=True, 
        blank=True,
        help_text="Registro detallado del proceso de importación"
    )
    datos_originales = models.JSONField(
        null=True, 
        blank=True,
        help_text="Datos originales del Excel"
    )
    datos_corregidos = models.JSONField(
        null=True, 
        blank=True,
        help_text="Datos después de las correcciones"
    )

    def clean(self):
        if self.archivo:
            if not self.archivo.name.endswith(('.xlsx', '.xls')):
                raise ValidationError('El archivo debe ser un Excel (.xlsx, .xls)')

    def iniciar_procesamiento(self):
        self.estado = 'EN_REVISION'
        self.fecha_procesamiento = timezone.now()
        self.save()

    def finalizar_procesamiento(self, exitoso=True):
        self.estado = 'IMPORTADO' if exitoso else 'ERROR'
        self.save()

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas de la importación"""
        if self.datos_originales:
            self.registros_totales = sum(len(hoja) for hoja in self.datos_originales.values())
        if self.log_procesamiento:
            self.registros_con_error = sum(1 for log in self.log_procesamiento if log.get('tipo') == 'ERROR')
        self.registros_procesados = self.registros_totales - self.registros_con_error
        self.save()

    def __str__(self):
        return f"Importación {self.get_tipo_importacion_display()} - {self.fecha_subida.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Importación de Excel"
        verbose_name_plural = "Importaciones de Excel"
        ordering = ['-fecha_subida']

class MapeoColumnas(models.Model):
    """Configuración del mapeo de columnas Excel a campos del modelo"""
    TIPOS_TRANSFORMACION = [
        ('NONE', 'Sin transformación'),
        ('UPPERCASE', 'Convertir a mayúsculas'),
        ('LOWERCASE', 'Convertir a minúsculas'),
        ('CAPITALIZE', 'Capitalizar'),
        ('STRIP', 'Eliminar espacios'),
        ('CUSTOM', 'Transformación personalizada')
    ]

    nombre_columna_excel = models.CharField(
        max_length=100,
        help_text="Nombre de la columna en el archivo Excel"
    )
    campo_modelo = models.CharField(
        max_length=100,
        help_text="Nombre del campo en el modelo de Django"
    )
    transformacion = models.CharField(
        max_length=20,
        choices=TIPOS_TRANSFORMACION,
        default='NONE',
        help_text="Tipo de transformación a aplicar"
    )
    funcion_transformacion = models.TextField(
        null=True,
        blank=True,
        help_text="Código Python para transformación personalizada"
    )
    validaciones = models.JSONField(
        default=list,
        help_text="Lista de validaciones a aplicar"
    )
    es_requerido = models.BooleanField(
        default=False,
        help_text="Indica si el campo es obligatorio"
    )
    valor_defecto = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Valor por defecto si el campo está vacío"
    )

    def __str__(self):
        return f"{self.nombre_columna_excel} → {self.campo_modelo}"

    class Meta:
        verbose_name = "Mapeo de Columna"
        verbose_name_plural = "Mapeo de Columnas"
        unique_together = ['nombre_columna_excel', 'campo_modelo']

class CorreccionDatos(models.Model):
    """Registro de correcciones realizadas durante la importación"""
    importacion = models.ForeignKey(
        ExcelImport,
        on_delete=models.CASCADE,
        related_name='correcciones'
    )
    campo = models.CharField(max_length=100)
    valor_original = models.CharField(max_length=200)
    valor_corregido = models.CharField(max_length=200)
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='correcciones_realizadas'
    )
    fecha = models.DateTimeField(auto_now_add=True)
    justificacion = models.TextField(
        blank=True,
        help_text="Razón de la corrección"
    )
    fila = models.IntegerField(
        help_text="Número de fila en el Excel"
    )
    hoja = models.CharField(
        max_length=100,
        help_text="Nombre de la hoja del Excel"
    )

    def __str__(self):
        return f"Corrección en {self.campo} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Corrección de Datos"
        verbose_name_plural = "Correcciones de Datos"
        ordering = ['-fecha']

class ReglaCorreccion(models.Model):
    """Reglas aprendidas para correcciones automáticas"""
    TIPOS_REGLA = [
        ('EXACTO', 'Coincidencia Exacta'),
        ('REGEX', 'Expresión Regular'),
        ('SIMILITUD', 'Similitud de Texto'),
        ('FUNCION', 'Función Personalizada')
    ]
    
    campo = models.CharField(max_length=100)
    tipo_regla = models.CharField(
        max_length=20,
        choices=TIPOS_REGLA,
        default='EXACTO',
        help_text="Tipo de comparación para aplicar la regla"
    )
    patron_original = models.CharField(
        max_length=200,
        help_text="Patrón a identificar (puede ser regex)"
    )
    correccion = models.CharField(
        max_length=200,
        help_text="Valor de reemplazo"
    )
    funcion_correccion = models.TextField(
        null=True,
        blank=True,
        help_text="Código Python para corrección personalizada"
    )
    umbral_similitud = models.FloatField(
        default=0.8,
        help_text="Umbral de similitud (0-1) para tipo SIMILITUD"
    )
    confianza = models.FloatField(
        default=0.0,
        help_text="Nivel de confianza de la regla (0-1)"
    )
    veces_aplicada = models.IntegerField(default=0)
    veces_rechazada = models.IntegerField(
        default=0,
        help_text="Número de veces que la corrección fue rechazada"
    )
    activa = models.BooleanField(default=True)
    creada_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_aplicacion = models.DateTimeField(null=True, blank=True)
    
    def aplicar(self, valor):
        """Aplica la regla de corrección a un valor"""
        import re
        import difflib
        
        if not self.activa:
            return valor
            
        valor_str = str(valor)
        
        try:
            if self.tipo_regla == 'EXACTO':
                if valor_str.lower() == self.patron_original.lower():
                    return self._registrar_aplicacion(self.correccion)
                    
            elif self.tipo_regla == 'REGEX':
                if re.match(self.patron_original, valor_str):
                    correccion = re.sub(self.patron_original, self.correccion, valor_str)
                    return self._registrar_aplicacion(correccion)
                    
            elif self.tipo_regla == 'SIMILITUD':
                ratio = difflib.SequenceMatcher(None, valor_str.lower(), 
                                              self.patron_original.lower()).ratio()
                if ratio >= self.umbral_similitud:
                    return self._registrar_aplicacion(self.correccion)
                    
            elif self.tipo_regla == 'FUNCION' and self.funcion_correccion:
                # Ejecutar función personalizada con seguridad
                namespace = {}
                exec(self.funcion_correccion, namespace)
                if 'corregir' in namespace:
                    resultado = namespace['corregir'](valor_str)
                    if resultado != valor_str:
                        return self._registrar_aplicacion(resultado)
                        
        except Exception as e:
            from django.core.exceptions import ValidationError
            raise ValidationError(f"Error al aplicar regla: {str(e)}")
            
        return valor

    def _registrar_aplicacion(self, valor_corregido):
        """Registra una aplicación exitosa de la regla"""
        self.veces_aplicada += 1
        self.ultima_aplicacion = timezone.now()
        
        # Actualizar confianza basada en el ratio de éxito
        total_usos = self.veces_aplicada + self.veces_rechazada
        self.confianza = self.veces_aplicada / total_usos if total_usos > 0 else 0.5
        
        self.save()
        return valor_corregido

    def registrar_rechazo(self):
        """Registra cuando una corrección es rechazada por el usuario"""
        self.veces_rechazada += 1
        
        # Actualizar confianza
        total_usos = self.veces_aplicada + self.veces_rechazada
        self.confianza = self.veces_aplicada / total_usos if total_usos > 0 else 0.5
        
        # Desactivar regla si la confianza es muy baja
        if total_usos > 10 and self.confianza < 0.3:
            self.activa = False
            
        self.save()

    def __str__(self):
        return f"Regla para {self.campo}: {self.patron_original} → {self.correccion}"

    class Meta:
        verbose_name = "Regla de Corrección"
        verbose_name_plural = "Reglas de Corrección"
        ordering = ['-confianza', '-veces_aplicada']
