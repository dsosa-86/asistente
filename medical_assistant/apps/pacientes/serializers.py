from rest_framework import serializers
from .models import Paciente
from apps.operaciones.models import PrequirurgicoPaciente, EstudioPrequirurgico

class PacienteSerializer(serializers.ModelSerializer):
    """Serializer para operaciones CRUD básicas de pacientes"""
    class Meta:
        model = Paciente
        fields = [
            'id', 'nombre', 'apellido', 'dni', 'fecha_nacimiento',
            'sexo', 'direccion', 'telefono', 'email', 'obra_social',
            'numero_afiliacion', 'antecedentes_medicos', 'alergias',
            'medicacion_actual', 'grupo_sanguineo'
        ]

class PacienteDetalleSerializer(PacienteSerializer):
    """Serializer con información detallada del paciente"""
    estudios_pendientes = serializers.SerializerMethodField()
    proximas_operaciones = serializers.SerializerMethodField()
    ultimas_consultas = serializers.SerializerMethodField()
    
    class Meta(PacienteSerializer.Meta):
        fields = PacienteSerializer.Meta.fields + [
            'estudios_pendientes', 'proximas_operaciones', 'ultimas_consultas'
        ]
    
    def get_estudios_pendientes(self, obj):
        estudios = PrequirurgicoPaciente.objects.filter(
            paciente=obj,
            estado__in=['PENDIENTE', 'SOLICITADO']
        ).select_related('estudio')
        return [{
            'id': estudio.id,
            'nombre': estudio.estudio.nombre,
            'tipo': estudio.estudio.tipo,
            'estado': estudio.estado,
            'fecha_solicitud': estudio.fecha_solicitud
        } for estudio in estudios]
    
    def get_proximas_operaciones(self, obj):
        from apps.operaciones.models import Operacion
        from datetime import datetime
        
        operaciones = Operacion.objects.filter(
            paciente=obj,
            estado='PROGRAMADA',
            fecha_programada__gte=datetime.now()
        ).order_by('fecha_programada')[:5]
        
        return [{
            'id': op.id,
            'tipo_cirugia': str(op.tipo_cirugia),
            'fecha_programada': op.fecha_programada,
            'cirujano': str(op.cirujano_principal)
        } for op in operaciones]
    
    def get_ultimas_consultas(self, obj):
        from apps.consultas.models import Consulta
        
        consultas = Consulta.objects.filter(
            paciente=obj
        ).order_by('-fecha_hora')[:5]
        
        return [{
            'id': consulta.id,
            'medico': str(consulta.medico),
            'fecha': consulta.fecha_hora,
            'diagnostico': consulta.diagnostico
        } for consulta in consultas]

class EstudioPrequirurgicoSerializer(serializers.ModelSerializer):
    """Serializer para estudios prequirúrgicos"""
    class Meta:
        model = EstudioPrequirurgico
        fields = ['id', 'nombre', 'descripcion', 'tipo', 'tipo_cirugia', 'es_obligatorio']

class PrequirurgicoPacienteSerializer(serializers.ModelSerializer):
    """Serializer para la relación entre pacientes y estudios"""
    estudio = EstudioPrequirurgicoSerializer(read_only=True)
    
    class Meta:
        model = PrequirurgicoPaciente
        fields = [
            'id', 'paciente', 'estudio', 'estado', 'fecha_solicitud',
            'fecha_realizacion', 'resultado', 'archivo'
        ]
        read_only_fields = ['fecha_solicitud']

    def validate(self, data):
        """Validaciones personalizadas para los estudios"""
        if data.get('estado') == 'REALIZADO' and not data.get('fecha_realizacion'):
            raise serializers.ValidationError(
                "Debe especificar la fecha de realización para estudios completados"
            )
        return data 