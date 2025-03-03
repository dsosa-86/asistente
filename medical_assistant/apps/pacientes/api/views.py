from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Paciente
from .serializers import PacienteSerializer

class PacienteViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar pacientes.
    
    * Requiere autenticación.
    * Solo usuarios autorizados pueden acceder.
    """
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated]
