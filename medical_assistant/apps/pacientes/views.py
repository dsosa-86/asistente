from django.shortcuts import get_object_or_404, render

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib import messages
import pandas as pd

from .models import Paciente  # Ajusta según donde esté tu modelo
from .forms import ArchivoExcelForm  # Ajusta según donde esté tu formulario
from .forms import PacienteForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from datetime import datetime, timedelta
from apps.operaciones.models import PrequirurgicoPaciente, Operacion
from apps.consultas.models import Consulta


def cargar_excel(request):
    if request.method == "POST":
        form = ArchivoExcelForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo']
            try:
                df = pd.read_excel(archivo, engine='openpyxl')
                
                for _, row in df.iterrows():
                    Paciente.objects.create(
                        # ... existing code ...
                    )
                messages.success(request, "Datos cargados correctamente.")
                return redirect('admin:paciente_changelist')  # Ajusta según tu URL de admin

            except Exception as e:
                messages.error(request, f"Error al procesar el archivo: {e}")
    
    else:
        form = ArchivoExcelForm()

    return render(request, 'pacientes/cargar_excel.html', {'form': form})

def crear_paciente(request):
    if request.method == "POST":
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Paciente creado correctamente.")
            return redirect('listar_pacientes')
    else:
        form = PacienteForm()
    return render(request, 'pacientes/crear_paciente.html', {'form': form})

def listar_pacientes(request):
    pacientes = Paciente.objects.all()
    return render(request, 'pacientes/listar_pacientes.html', {'pacientes': pacientes})

def editar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == "POST":
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, "Paciente actualizado correctamente.")
            return redirect('listar_pacientes')
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'pacientes/editar_paciente.html', {'form': form})

@login_required
def dashboard_paciente(request, pk):
    """Vista del dashboard del paciente"""
    paciente = get_object_or_404(Paciente, pk=pk)
    
    # Obtener estudios prequirúrgicos pendientes
    estudios_pendientes = PrequirurgicoPaciente.objects.filter(
        paciente=paciente,
        estado__in=['PENDIENTE', 'SOLICITADO']
    ).select_related('estudio')
    
    # Obtener próximas operaciones
    proximas_operaciones = Operacion.objects.filter(
        paciente=paciente,
        estado='PROGRAMADA',
        fecha_programada__gte=datetime.now()
    ).order_by('fecha_programada')[:5]
    
    # Obtener últimas consultas
    ultimas_consultas = Consulta.objects.filter(
        paciente=paciente
    ).order_by('-fecha_hora')[:5]
    
    # Estadísticas generales
    fecha_limite = datetime.now() - timedelta(days=365)
    estadisticas = {
        'total_consultas': Consulta.objects.filter(paciente=paciente).count(),
        'consultas_ultimo_año': Consulta.objects.filter(
            paciente=paciente,
            fecha_hora__gte=fecha_limite
        ).count(),
        'operaciones_realizadas': Operacion.objects.filter(
            paciente=paciente,
            estado='FINALIZADA'
        ).count(),
        'estudios_pendientes': estudios_pendientes.count()
    }
    
    context = {
        'paciente': paciente,
        'estudios_pendientes': estudios_pendientes,
        'proximas_operaciones': proximas_operaciones,
        'ultimas_consultas': ultimas_consultas,
        'estadisticas': estadisticas,
    }
    
    return render(request, 'pacientes/dashboard.html', context)

