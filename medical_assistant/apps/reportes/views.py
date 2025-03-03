from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Reporte
from .serializers import ReporteSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

@login_required
def lista_reportes(request):
    reportes = Reporte.objects.filter(usuario=request.user)
    return render(request, 'reportes/lista.html', {'reportes': reportes})

@login_required
def detalle_reporte(request, pk):
    reporte = get_object_or_404(Reporte, pk=pk)
    return render(request, 'reportes/detalle.html', {'reporte': reporte})

class ReporteViewSet(viewsets.ModelViewSet):
    queryset = Reporte.objects.all()
    serializer_class = ReporteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(usuario=self.request.user)
