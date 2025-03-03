from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import ExcelImport, MapeoColumnas
from .serializers import (
    ExcelImportSerializer,
    MapeoColumnasSerializer,
    EstadisticasSerializer
)
from ..tasks import procesar_archivo_excel
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ExcelImportViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar importaciones de Excel.
    
    * Requiere autenticación.
    * Solo usuarios autorizados pueden acceder.
    """
    queryset = ExcelImport.objects.all()
    serializer_class = ExcelImportSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Inicia el procesamiento de un archivo Excel",
        responses={
            200: openapi.Response('Procesamiento iniciado correctamente'),
            400: 'Solicitud inválida',
            404: 'Importación no encontrada'
        }
    )
    @action(detail=True, methods=['post'])
    def procesar(self, request, pk=None):
        """Inicia el procesamiento asíncrono del archivo."""
        importacion = self.get_object()
        task = procesar_archivo_excel.delay(importacion.id)
        return Response({
            'task_id': task.id,
            'status': 'Procesamiento iniciado'
        })

    @swagger_auto_schema(
        operation_description="Obtiene el estado actual del procesamiento",
        responses={
            200: openapi.Response('Estado del procesamiento'),
            404: 'Importación no encontrada'
        }
    )
    @action(detail=True, methods=['get'])
    def estado(self, request, pk=None):
        """Obtiene el estado actual de la importación."""
        importacion = self.get_object()
        return Response({
            'estado': importacion.estado,
            'registros_procesados': importacion.registros_procesados,
            'registros_con_error': importacion.registros_con_error
        })

    @swagger_auto_schema(
        operation_description="Obtiene estadísticas de la importación",
        responses={
            200: EstadisticasSerializer,
            404: 'Importación no encontrada'
        }
    )
    @action(detail=True, methods=['get'])
    def estadisticas(self, request, pk=None):
        """Obtiene estadísticas detalladas de la importación."""
        importacion = self.get_object()
        cache_key = f'estadisticas_importacion_{pk}'
        
        # Intentar obtener del cache
        stats = cache.get(cache_key)
        if not stats:
            stats = {
                'total_registros': importacion.registros_totales,
                'procesados': importacion.registros_procesados,
                'errores': importacion.registros_con_error,
                'tasa_exito': (
                    (importacion.registros_procesados / importacion.registros_totales) * 100
                    if importacion.registros_totales > 0 else 0
                )
            }
            cache.set(cache_key, stats, timeout=300)  # Cache por 5 minutos
        
        return Response(stats)

    @swagger_auto_schema(
        operation_description="Reprocesa un archivo Excel",
        responses={
            200: openapi.Response('Reprocesamiento iniciado correctamente'),
            400: 'Solicitud inválida',
            404: 'Importación no encontrada'
        }
    )
    @action(detail=True, methods=['post'])
    def reprocesar(self, request, pk=None):
        """Inicia el reprocesamiento asíncrono del archivo."""
        importacion = self.get_object()
        task = procesar_archivo_excel.delay(importacion.id, reprocesar=True)
        return Response({
            'task_id': task.id,
            'status': 'Reprocesamiento iniciado'
        })

class MapeoColumnasViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar mapeos de columnas.
    
    * Requiere autenticación.
    * Solo usuarios autorizados pueden acceder.
    """
    queryset = MapeoColumnas.objects.all()
    serializer_class = MapeoColumnasSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Valida un mapeo de columnas",
        request_body=MapeoColumnasSerializer,
        responses={
            200: openapi.Response('Mapeo válido'),
            400: 'Mapeo inválido'
        }
    )
    @action(detail=False, methods=['post'])
    def validar(self, request):
        """Valida un mapeo de columnas antes de guardarlo."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response({'valid': True})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)