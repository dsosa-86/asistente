from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Paciente
from apps.operaciones.models import PrequirurgicoPaciente
from datetime import datetime, timedelta
from .serializers import (
    PacienteSerializer,
    PacienteDetalleSerializer,
    PrequirurgicoPacienteSerializer
)

class PacienteViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar pacientes.
    
    list:
        Retorna una lista de todos los pacientes.
    
    create:
        Crea un nuevo paciente.
        
    retrieve:
        Retorna los detalles de un paciente específico.
        
    update:
        Actualiza un paciente existente.
        
    partial_update:
        Actualiza parcialmente un paciente existente.
        
    destroy:
        Elimina un paciente existente.
    """
    queryset = Paciente.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['dni', 'obra_social']
    search_fields = ['nombre', 'apellido', 'dni']
    ordering_fields = ['apellido', 'nombre', 'fecha_nacimiento']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PacienteDetalleSerializer
        return PacienteSerializer
    
    @action(detail=True, methods=['get'])
    def estudios(self, request, pk=None):
        """Retorna todos los estudios prequirúrgicos del paciente"""
        paciente = self.get_object()
        estudios = PrequirurgicoPaciente.objects.filter(paciente=paciente)
        serializer = PrequirurgicoPacienteSerializer(estudios, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def estadisticas(self, request, pk=None):
        """Retorna estadísticas del paciente"""
        paciente = self.get_object()
        from datetime import datetime, timedelta
        from django.db.models import Count
        
        # Calcular estadísticas
        fecha_limite = datetime.now() - timedelta(days=365)
        stats = {
            'total_consultas': paciente.consulta_set.count(),
            'consultas_ultimo_año': paciente.consulta_set.filter(
                fecha_hora__gte=fecha_limite
            ).count(),
            'total_operaciones': paciente.operaciones.count(),
            'estudios_pendientes': paciente.estudios_prequirurgicos.filter(
                estado__in=['PENDIENTE', 'SOLICITADO']
            ).count(),
            'estudios_por_tipo': paciente.estudios_prequirurgicos.values(
                'estudio__tipo'
            ).annotate(
                total=Count('id')
            )
        }
        
        return Response(stats)

class PrequirurgicoPacienteViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar estudios prequirúrgicos de pacientes.
    """
    serializer_class = PrequirurgicoPacienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['paciente', 'estado', 'estudio__tipo']
    ordering_fields = ['fecha_solicitud', 'fecha_realizacion']
    
    def get_queryset(self):
        return PrequirurgicoPaciente.objects.select_related(
            'paciente', 'estudio'
        ).all()
    
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Actualiza el estado de un estudio"""
        estudio = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if nuevo_estado not in dict(PrequirurgicoPaciente.ESTADOS).keys():
            return Response(
                {'error': 'Estado inválido'},
                status=400
            )
        
        estudio.estado = nuevo_estado
        if nuevo_estado == 'REALIZADO':
            estudio.fecha_realizacion = datetime.now()
        estudio.save()
        
        serializer = self.get_serializer(estudio)
        return Response(serializer.data) 