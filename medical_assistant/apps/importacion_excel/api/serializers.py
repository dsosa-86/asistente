from rest_framework import serializers
from ..models import ExcelImport, MapeoColumnas, CorreccionDatos

class ExcelImportSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo ExcelImport.
    Incluye validaciones adicionales para el archivo Excel.
    """
    class Meta:
        model = ExcelImport
        fields = '__all__'
        read_only_fields = ('estado', 'fecha_subida', 'fecha_procesamiento',
                          'registros_totales', 'registros_procesados',
                          'registros_con_error')

    def validate_archivo(self, value):
        """Valida el archivo Excel."""
        from ..validators import validar_archivo_excel
        validar_archivo_excel(value)
        return value

class MapeoColumnasSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo MapeoColumnas.
    Incluye validación de la función de transformación personalizada.
    """
    class Meta:
        model = MapeoColumnas
        fields = '__all__'

    def validate_funcion_transformacion(self, value):
        """Valida la función de transformación personalizada."""
        if value:
            try:
                # Intentar compilar el código para verificar sintaxis
                compile(value, '<string>', 'exec')
            except Exception as e:
                raise serializers.ValidationError(f"Error en la función: {str(e)}")
        return value

class CorreccionDatosSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo CorreccionDatos.
    """
    class Meta:
        model = CorreccionDatos
        fields = '__all__'
        read_only_fields = ('fecha',)

class EstadisticasSerializer(serializers.Serializer):
    """
    Serializador para las estadísticas de importación.
    """
    total_registros = serializers.IntegerField()
    procesados = serializers.IntegerField()
    errores = serializers.IntegerField()
    tasa_exito = serializers.FloatField()

class ErrorImportacionSerializer(serializers.Serializer):
    """
    Serializador para errores de importación.
    """
    fila = serializers.IntegerField()
    columna = serializers.CharField()
    mensaje = serializers.CharField()
    valor = serializers.CharField(allow_null=True)

class ResultadoValidacionSerializer(serializers.Serializer):
    """
    Serializador para resultados de validación.
    """
    es_valido = serializers.BooleanField()
    errores = ErrorImportacionSerializer(many=True, required=False)
    advertencias = serializers.ListField(child=serializers.CharField(), required=False) 