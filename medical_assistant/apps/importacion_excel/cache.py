from django.core.cache import cache
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from typing import Dict, Any, Optional
from .models import ExcelImport, CorreccionDatos, ReglaCorreccion

class CacheManager:
    """Gestor de caché para la app de importación"""
    
    # Prefijos para las claves de caché
    PREFIJO_ESTADISTICAS = 'importacion_excel:estadisticas'
    PREFIJO_VALIDACIONES = 'importacion_excel:validaciones'
    PREFIJO_REGLAS = 'importacion_excel:reglas'
    
    def __init__(self):
        self.timeout_estadisticas = 3600  # 1 hora
        self.timeout_validaciones = 86400  # 24 horas
        self.timeout_reglas = 1800  # 30 minutos

    def get_estadisticas(self, periodo: int = 30, tipo: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene estadísticas cacheadas o las calcula si no existen"""
        key = f"{self.PREFIJO_ESTADISTICAS}:{periodo}:{tipo or 'all'}"
        estadisticas = cache.get(key)
        
        if estadisticas is None:
            estadisticas = self._calcular_estadisticas(periodo, tipo)
            cache.set(key, estadisticas, self.timeout_estadisticas)
        
        return estadisticas

    def _calcular_estadisticas(self, periodo: int, tipo: Optional[str]) -> Dict[str, Any]:
        """Calcula las estadísticas de importación"""
        fecha_inicio = timezone.now() - timedelta(days=periodo)
        query = ExcelImport.objects.filter(fecha_subida__gte=fecha_inicio)
        
        if tipo:
            query = query.filter(tipo_importacion=tipo)
        
        # Estadísticas generales
        stats = {
            'total_importaciones': query.count(),
            'importaciones_exitosas': query.filter(estado='IMPORTADO').count(),
            'promedio_registros': query.aggregate(Avg('registros_totales'))['registros_totales__avg'] or 0,
            'total_errores': query.aggregate(total_errores=Sum('registros_con_error'))['total_errores'] or 0,
            
            # Distribución por estado
            'distribucion_estados': dict(
                query.values('estado').annotate(total=Count('id')).values_list('estado', 'total')
            ),
            
            # Tendencia diaria
            'tendencia': self._calcular_tendencia(query),
            
            # Errores comunes
            'errores_comunes': self._obtener_errores_comunes(query),
            
            # Tasa de corrección
            'tasa_correccion': self._calcular_tasa_correccion(query)
        }
        
        return stats

    def _calcular_tendencia(self, query):
        """Calcula la tendencia de importaciones por día"""
        return (
            query
            .annotate(fecha=TruncDate('fecha_subida'))
            .values('fecha')
            .annotate(total=Count('id'))
            .order_by('fecha')
            .values_list('fecha', 'total')
        )

    def _obtener_errores_comunes(self, query):
        """Obtiene los errores más comunes"""
        return (
            CorreccionDatos.objects.filter(importacion__in=query)
            .values('campo')
            .annotate(total=Count('id'))
            .order_by('-total')[:5]
        )

    def _calcular_tasa_correccion(self, query):
        """Calcula la tasa de corrección por tipo de importación"""
        return (
            query
            .values('tipo_importacion')
            .annotate(
                total=Count('id'),
                corregidos=Count('id', filter=Q(estado='CORREGIDO'))
            )
            .annotate(
                tasa=ExpressionWrapper(
                    F('corregidos') * 100.0 / F('total'),
                    output_field=FloatField()
                )
            )
        )

    def get_validaciones(self, campo: str) -> Dict[str, Any]:
        """Obtiene datos de validación cacheados"""
        key = f"{self.PREFIJO_VALIDACIONES}:{campo}"
        validaciones = cache.get(key)
        
        if validaciones is None:
            validaciones = self._cargar_validaciones(campo)
            cache.set(key, validaciones, self.timeout_validaciones)
        
        return validaciones

    def _cargar_validaciones(self, campo: str) -> Dict[str, Any]:
        """Carga datos de validación para un campo específico"""
        from .validators import ValidadorExcel
        validador = ValidadorExcel()
        return validador.cache.get(campo, {})

    def get_reglas_correccion(self, campo: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene reglas de corrección cacheadas"""
        key = f"{self.PREFIJO_REGLAS}:{campo or 'all'}"
        reglas = cache.get(key)
        
        if reglas is None:
            reglas = self._cargar_reglas(campo)
            cache.set(key, reglas, self.timeout_reglas)
        
        return reglas

    def _cargar_reglas(self, campo: Optional[str]) -> Dict[str, Any]:
        """Carga reglas de corrección activas"""
        query = ReglaCorreccion.objects.filter(activa=True)
        if campo:
            query = query.filter(campo=campo)
        
        return {
            regla.campo: {
                'tipo': regla.tipo_regla,
                'patron': regla.patron_original,
                'correccion': regla.correccion,
                'confianza': regla.confianza
            }
            for regla in query
        }

    def invalidar_cache_estadisticas(self):
        """Invalida la caché de estadísticas"""
        cache.delete_pattern(f"{self.PREFIJO_ESTADISTICAS}:*")

    def invalidar_cache_validaciones(self, campo: Optional[str] = None):
        """Invalida la caché de validaciones"""
        if campo:
            cache.delete(f"{self.PREFIJO_VALIDACIONES}:{campo}")
        else:
            cache.delete_pattern(f"{self.PREFIJO_VALIDACIONES}:*")

    def invalidar_cache_reglas(self, campo: Optional[str] = None):
        """Invalida la caché de reglas"""
        if campo:
            cache.delete(f"{self.PREFIJO_REGLAS}:{campo}")
        else:
            cache.delete_pattern(f"{self.PREFIJO_REGLAS}:*")

    def actualizar_cache_periodicamente(self):
        """Actualiza la caché periódicamente"""
        self.invalidar_cache_estadisticas()
        self.invalidar_cache_validaciones()
        self.invalidar_cache_reglas()
        
        # Precarga las estadísticas más comunes
        self.get_estadisticas(30)  # Último mes
        self.get_estadisticas(7)   # Última semana
        
        # Precarga validaciones comunes
        campos_comunes = ['dni', 'email', 'telefono']
        for campo in campos_comunes:
            self.get_validaciones(campo)
        
        # Precarga reglas
        self.get_reglas_correccion() 