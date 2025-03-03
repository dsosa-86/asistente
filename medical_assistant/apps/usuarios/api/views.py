from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Medico
from .serializers import MedicoSerializer

class MedicoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar médicos.
    
    * Requiere autenticación.
    * Solo usuarios autorizados pueden acceder.
    """
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer
    permission_classes = [IsAuthenticated]
