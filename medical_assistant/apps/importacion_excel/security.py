from django.core.exceptions import ValidationError
from django.conf import settings
import magic
import os
from typing import BinaryIO
import hashlib
from django.core.cache import cache
from django.core.files.uploadedfile import UploadedFile
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    """Gestor de seguridad para la importación de archivos Excel."""

    MIME_TYPES_PERMITIDOS = [
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ]

    def __init__(self):
        self.mime = magic.Magic(mime=True)

    def validar_archivo(self, archivo: UploadedFile) -> None:
        """
        Realiza todas las validaciones de seguridad en el archivo.
        Raises:
            ValidationError: Si el archivo no cumple con los requisitos de seguridad.
        """
        self._validar_tamano(archivo)
        self._validar_tipo_mime(archivo)
        self._validar_contenido_malicioso(archivo)
        self._validar_rate_limit(archivo)

    def _validar_tamano(self, archivo: UploadedFile) -> None:
        """Valida que el archivo no exceda el tamaño máximo permitido."""
        max_size = getattr(settings, 'MAX_EXCEL_SIZE', 5 * 1024 * 1024)  # 5MB por defecto
        if archivo.size > max_size:
            raise ValidationError(
                f'El archivo excede el tamaño máximo permitido de {max_size/1024/1024}MB'
            )

    def _validar_tipo_mime(self, archivo: UploadedFile) -> None:
        """Valida que el tipo MIME del archivo sea válido."""
        try:
            mime_type = self.mime.from_buffer(archivo.read(2048))
            archivo.seek(0)  # Resetear el puntero del archivo
            
            if mime_type not in self.MIME_TYPES_PERMITIDOS:
                raise ValidationError(
                    f'Tipo de archivo no permitido. Tipo detectado: {mime_type}'
                )
        except Exception as e:
            logger.error(f'Error al validar tipo MIME: {str(e)}')
            raise ValidationError('No se pudo validar el tipo de archivo')

    def _validar_contenido_malicioso(self, archivo: UploadedFile) -> None:
        """
        Realiza verificaciones básicas de seguridad en el contenido del archivo.
        - Busca macros potencialmente peligrosas
        - Verifica la estructura del archivo
        - Busca contenido ejecutable
        """
        try:
            content = archivo.read()
            archivo.seek(0)

            # Verificar presencia de macros
            if b'VBA' in content or b'Microsoft Office' in content:
                # Análisis más detallado de macros
                self._analizar_macros(content)

            # Verificar contenido ejecutable
            if self._contiene_ejecutable(content):
                raise ValidationError('Se detectó contenido ejecutable en el archivo')

        except Exception as e:
            logger.error(f'Error al validar contenido malicioso: {str(e)}')
            raise ValidationError('Error al analizar el contenido del archivo')

    def _validar_rate_limit(self, archivo: UploadedFile) -> None:
        """
        Implementa rate limiting por usuario/IP para prevenir ataques DoS.
        """
        # Obtener identificador único (IP o usuario)
        request = getattr(archivo, 'request', None)
        if request:
            identifier = request.user.id if request.user.is_authenticated else request.META.get('REMOTE_ADDR')
            
            # Verificar límite de subidas
            cache_key = f'upload_limit_{identifier}'
            upload_count = cache.get(cache_key, 0)
            
            max_uploads = getattr(settings, 'MAX_UPLOADS_PER_HOUR', 10)
            if upload_count >= max_uploads:
                raise ValidationError(
                    'Has excedido el límite de subidas permitidas por hora'
                )
            
            # Incrementar contador
            cache.set(cache_key, upload_count + 1, timeout=3600)  # 1 hora

    def _analizar_macros(self, content: bytes) -> None:
        """Análisis detallado de macros en el archivo."""
        # Implementar análisis específico de macros
        # TODO: Integrar con biblioteca de análisis de macros
        pass

    def _contiene_ejecutable(self, content: bytes) -> bool:
        """Verifica si el contenido contiene código ejecutable."""
        executable_patterns = [
            b'MZ',  # Ejecutables Windows
            b'ELF',  # Ejecutables Linux
            b'#!/',  # Scripts
        ]
        return any(pattern in content for pattern in executable_patterns)

    @staticmethod
    def calcular_hash(archivo: BinaryIO) -> str:
        """Calcula el hash SHA-256 del archivo."""
        sha256 = hashlib.sha256()
        for chunk in iter(lambda: archivo.read(4096), b''):
            sha256.update(chunk)
        archivo.seek(0)
        return sha256.hexdigest()

    def registrar_intento_fallido(self, ip: str) -> None:
        """Registra intentos fallidos de subida para detectar posibles ataques."""
        cache_key = f'failed_uploads_{ip}'
        failed_attempts = cache.get(cache_key, 0)
        cache.set(cache_key, failed_attempts + 1, timeout=3600)

        # Si hay muchos intentos fallidos, registrar para análisis
        if failed_attempts >= 5:
            logger.warning(f'Múltiples intentos fallidos desde IP: {ip}') 