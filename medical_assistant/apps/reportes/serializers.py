from rest_framework import serializers
from .models import Reporte, Estadistica

class EstadisticaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estadistica
        fields = '__all__'

class ReporteSerializer(serializers.ModelSerializer):
    estadisticas = EstadisticaSerializer(many=True, read_only=True)

    class Meta:
        model = Reporte
        fields = '__all__'
