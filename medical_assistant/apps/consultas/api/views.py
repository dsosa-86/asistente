from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Consulta
from .serializers import ConsultaSerializer

class ConsultaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar consultas.
    
    * Requiere autenticación.
    * Solo usuarios autorizados pueden acceder.
    """
    queryset = Consulta.objects.all()
    serializer_class = ConsultaSerializer
    permission_classes = [IsAuthenticated]
