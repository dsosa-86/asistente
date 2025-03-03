from django.conf import settings
from typing import Dict, Any, List
import os

class ImportacionConfig:
    """Configuración centralizada para la app de importación Excel."""

    # Configuraciones por defecto
    DEFAULTS = {
        'MAX_FILE_SIZE': 5 * 1024 * 1024,  # 5MB
        'ALLOWED_EXTENSIONS': ['.xlsx', '.xls'],
        'CHUNK_SIZE': 1000,  # Registros por chunk
        'TIMEOUT': 3600,  # 1 hora
        'RETRY_LIMIT': 3,
        'CACHE_TIMEOUT': 300,  # 5 minutos
        'UPLOAD_LIMIT_PER_HOUR': 10,
    }

    # Tipos de importación y sus configuraciones específicas
    TIPOS_IMPORTACION = {
        'AGENDA': {
            'columnas_requeridas': [
                'fecha', 'hora', 'paciente', 'medico',
                'procedimiento', 'obra_social'
            ],
            'validaciones_especificas': {
                'fecha': r'^\d{2}/\d{2}/\d{4}$',
                'hora': r'^\d{2}:\d{2}$',
                'dni': r'^\d{8}$'
            }
        },
        'HISTORICOS': {
            'columnas_requeridas': [
                'paciente', 'fecha', 'diagnostico',
                'tratamiento', 'medico'
            ],
            'validaciones_especificas': {
                'fecha': r'^\d{2}/\d{2}/\d{4}$',
                'dni': r'^\d{8}$'
            }
        }
    }

    # Configuraciones de exportación
    EXPORT_CONFIG = {
        'EXCEL': {
            'extension': '.xlsx',
            'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        },
        'CSV': {
            'extension': '.csv',
            'mime_type': 'text/csv',
            'delimiter': ','
        },
        'PDF': {
            'extension': '.pdf',
            'mime_type': 'application/pdf',
            'page_size': 'A4'
        }
    }

    def __init__(self):
        self.load_settings()

    def load_settings(self) -> None:
        """Carga configuraciones desde settings.py y variables de entorno."""
        # Cargar desde settings.py
        self.max_file_size = getattr(
            settings,
            'EXCEL_IMPORT_MAX_FILE_SIZE',
            self.DEFAULTS['MAX_FILE_SIZE']
        )
        
        self.allowed_extensions = getattr(
            settings,
            'EXCEL_IMPORT_ALLOWED_EXTENSIONS',
            self.DEFAULTS['ALLOWED_EXTENSIONS']
        )
        
        self.chunk_size = getattr(
            settings,
            'EXCEL_IMPORT_CHUNK_SIZE',
            self.DEFAULTS['CHUNK_SIZE']
        )
        
        self.timeout = getattr(
            settings,
            'EXCEL_IMPORT_TIMEOUT',
            self.DEFAULTS['TIMEOUT']
        )
        
        self.retry_limit = getattr(
            settings,
            'EXCEL_IMPORT_RETRY_LIMIT',
            self.DEFAULTS['RETRY_LIMIT']
        )
        
        self.cache_timeout = getattr(
            settings,
            'EXCEL_IMPORT_CACHE_TIMEOUT',
            self.DEFAULTS['CACHE_TIMEOUT']
        )
        
        self.upload_limit = getattr(
            settings,
            'EXCEL_IMPORT_UPLOAD_LIMIT',
            self.DEFAULTS['UPLOAD_LIMIT_PER_HOUR']
        )

        # Cargar desde variables de entorno
        self.load_env_settings()

    def load_env_settings(self) -> None:
        """Carga configuraciones desde variables de entorno."""
        self.max_file_size = int(
            os.getenv(
                'EXCEL_IMPORT_MAX_FILE_SIZE',
                self.max_file_size
            )
        )
        
        self.chunk_size = int(
            os.getenv(
                'EXCEL_IMPORT_CHUNK_SIZE',
                self.chunk_size
            )
        )
        
        self.timeout = int(
            os.getenv(
                'EXCEL_IMPORT_TIMEOUT',
                self.timeout
            )
        )

    def get_tipo_config(self, tipo: str) -> Dict[str, Any]:
        """Obtiene la configuración específica para un tipo de importación."""
        return self.TIPOS_IMPORTACION.get(tipo, {})

    def get_columnas_requeridas(self, tipo: str) -> List[str]:
        """Obtiene las columnas requeridas para un tipo de importación."""
        config = self.get_tipo_config(tipo)
        return config.get('columnas_requeridas', [])

    def get_validaciones(self, tipo: str) -> Dict[str, str]:
        """Obtiene las validaciones específicas para un tipo de importación."""
        config = self.get_tipo_config(tipo)
        return config.get('validaciones_especificas', {})

    def get_export_config(self, formato: str) -> Dict[str, Any]:
        """Obtiene la configuración para un formato de exportación."""
        return self.EXPORT_CONFIG.get(formato.upper(), {})

    def is_valid_extension(self, filename: str) -> bool:
        """Verifica si la extensión del archivo es válida."""
        ext = os.path.splitext(filename)[1].lower()
        return ext in self.allowed_extensions

    def get_timeout(self, tipo: str) -> int:
        """Obtiene el timeout específico para un tipo de importación."""
        config = self.get_tipo_config(tipo)
        return config.get('timeout', self.timeout)

    def get_chunk_size(self, tipo: str) -> int:
        """Obtiene el tamaño de chunk específico para un tipo de importación."""
        config = self.get_tipo_config(tipo)
        return config.get('chunk_size', self.chunk_size)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la configuración actual a un diccionario."""
        return {
            'max_file_size': self.max_file_size,
            'allowed_extensions': self.allowed_extensions,
            'chunk_size': self.chunk_size,
            'timeout': self.timeout,
            'retry_limit': self.retry_limit,
            'cache_timeout': self.cache_timeout,
            'upload_limit': self.upload_limit,
            'tipos_importacion': self.TIPOS_IMPORTACION,
            'export_config': self.EXPORT_CONFIG
        }

# Instancia global de configuración
config = ImportacionConfig() 