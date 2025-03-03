from django.core.cache import cache
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
import logging
from prometheus_client import Counter, Histogram, Gauge
import json
from typing import Dict, Any
from .models import ExcelImport

# Configuración de logging
logger = logging.getLogger(__name__)

# Métricas Prometheus
IMPORTACIONES_TOTAL = Counter(
    'excel_importaciones_total',
    'Total de importaciones realizadas',
    ['tipo', 'estado']
)

TIEMPO_PROCESAMIENTO = Histogram(
    'excel_tiempo_procesamiento_segundos',
    'Tiempo de procesamiento de importaciones',
    ['tipo']
)

REGISTROS_PROCESADOS = Counter(
    'excel_registros_procesados_total',
    'Total de registros procesados',
    ['tipo', 'resultado']
)

IMPORTACIONES_ACTIVAS = Gauge(
    'excel_importaciones_activas',
    'Número de importaciones actualmente en proceso'
)

class MonitoringManager:
    """Gestor de monitoreo para importaciones Excel."""

    def __init__(self):
        self.cache_timeout = 300  # 5 minutos

    def registrar_inicio_importacion(self, importacion_id: int) -> None:
        """Registra el inicio de una importación."""
        try:
            importacion = ExcelImport.objects.get(id=importacion_id)
            IMPORTACIONES_TOTAL.labels(
                tipo=importacion.tipo_importacion,
                estado='INICIADA'
            ).inc()
            
            IMPORTACIONES_ACTIVAS.inc()
            
            logger.info(f'Iniciada importación {importacion_id} - Tipo: {importacion.tipo_importacion}')
        except Exception as e:
            logger.error(f'Error al registrar inicio de importación {importacion_id}: {str(e)}')

    def registrar_fin_importacion(self, importacion_id: int, tiempo_proceso: float) -> None:
        """Registra la finalización de una importación."""
        try:
            importacion = ExcelImport.objects.get(id=importacion_id)
            
            IMPORTACIONES_TOTAL.labels(
                tipo=importacion.tipo_importacion,
                estado=importacion.estado
            ).inc()
            
            TIEMPO_PROCESAMIENTO.labels(
                tipo=importacion.tipo_importacion
            ).observe(tiempo_proceso)
            
            IMPORTACIONES_ACTIVAS.dec()
            
            self._actualizar_estadisticas_cache(importacion)
            
            logger.info(
                f'Finalizada importación {importacion_id} - '
                f'Estado: {importacion.estado} - '
                f'Tiempo: {tiempo_proceso:.2f}s'
            )
        except Exception as e:
            logger.error(f'Error al registrar fin de importación {importacion_id}: {str(e)}')

    def registrar_error(self, importacion_id: int, error: str) -> None:
        """Registra un error en la importación."""
        try:
            importacion = ExcelImport.objects.get(id=importacion_id)
            
            logger.error(
                f'Error en importación {importacion_id}: {error}',
                extra={
                    'importacion_id': importacion_id,
                    'tipo': importacion.tipo_importacion,
                    'usuario': importacion.usuario.username
                }
            )
            
            # Almacenar error en caché para análisis
            cache_key = f'import_error_{importacion_id}'
            errors = cache.get(cache_key, [])
            errors.append({
                'timestamp': timezone.now().isoformat(),
                'error': error
            })
            cache.set(cache_key, errors, timeout=86400)  # 24 horas
            
        except Exception as e:
            logger.error(f'Error al registrar error de importación {importacion_id}: {str(e)}')

    def obtener_metricas(self) -> Dict[str, Any]:
        """Obtiene métricas generales del sistema de importación."""
        try:
            ahora = timezone.now()
            hace_24h = ahora - timedelta(hours=24)
            
            # Obtener del caché si está disponible
            cache_key = 'import_metrics'
            metricas = cache.get(cache_key)
            
            if not metricas:
                # Calcular métricas
                metricas = {
                    'ultimas_24h': {
                        'total_importaciones': ExcelImport.objects.filter(
                            fecha_subida__gte=hace_24h
                        ).count(),
                        'exitosas': ExcelImport.objects.filter(
                            fecha_subida__gte=hace_24h,
                            estado='IMPORTADO'
                        ).count(),
                        'con_errores': ExcelImport.objects.filter(
                            fecha_subida__gte=hace_24h,
                            estado='ERROR'
                        ).count()
                    },
                    'tiempo_promedio': ExcelImport.objects.filter(
                        fecha_procesamiento__isnull=False
                    ).aggregate(
                        avg_time=Avg('tiempo_procesamiento')
                    )['avg_time'],
                    'por_tipo': ExcelImport.objects.values(
                        'tipo_importacion'
                    ).annotate(
                        total=Count('id')
                    )
                }
                
                cache.set(cache_key, metricas, timeout=self.cache_timeout)
            
            return metricas
            
        except Exception as e:
            logger.error(f'Error al obtener métricas: {str(e)}')
            return {}

    def _actualizar_estadisticas_cache(self, importacion: ExcelImport) -> None:
        """Actualiza las estadísticas en caché."""
        try:
            cache_key = f'import_stats_{importacion.tipo_importacion}'
            stats = cache.get(cache_key, {
                'total': 0,
                'exitosas': 0,
                'errores': 0,
                'registros_procesados': 0
            })
            
            stats['total'] += 1
            if importacion.estado == 'IMPORTADO':
                stats['exitosas'] += 1
            elif importacion.estado == 'ERROR':
                stats['errores'] += 1
            
            stats['registros_procesados'] += importacion.registros_procesados
            
            cache.set(cache_key, stats, timeout=self.cache_timeout)
            
        except Exception as e:
            logger.error(f'Error al actualizar estadísticas en caché: {str(e)}')

    def generar_reporte_rendimiento(self) -> Dict[str, Any]:
        """Genera un reporte detallado de rendimiento."""
        try:
            ahora = timezone.now()
            hace_7d = ahora - timedelta(days=7)
            
            return {
                'periodo': {
                    'inicio': hace_7d.isoformat(),
                    'fin': ahora.isoformat()
                },
                'metricas': self.obtener_metricas(),
                'errores_comunes': self._obtener_errores_comunes(),
                'tendencias': self._calcular_tendencias(hace_7d)
            }
            
        except Exception as e:
            logger.error(f'Error al generar reporte de rendimiento: {str(e)}')
            return {}

    def _obtener_errores_comunes(self) -> Dict[str, int]:
        """Obtiene los errores más comunes."""
        try:
            return ExcelImport.objects.filter(
                estado='ERROR'
            ).values(
                'log_procesamiento'
            ).annotate(
                total=Count('id')
            ).order_by('-total')[:5]
        except Exception as e:
            logger.error(f'Error al obtener errores comunes: {str(e)}')
            return {}

    def _calcular_tendencias(self, desde: timezone.datetime) -> Dict[str, Any]:
        """Calcula tendencias de importación."""
        try:
            return ExcelImport.objects.filter(
                fecha_subida__gte=desde
            ).values(
                'fecha_subida__date'
            ).annotate(
                total=Count('id'),
                exitosas=Count('id', filter=Q(estado='IMPORTADO')),
                errores=Count('id', filter=Q(estado='ERROR'))
            ).order_by('fecha_subida__date')
        except Exception as e:
            logger.error(f'Error al calcular tendencias: {str(e)}')
            return {} 