from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.consultas.models import Consulta
from apps.pacientes.models import Paciente
from apps.usuarios.models import Medico

def landing_page(request):
    return render(request, 'frontend/landing_page.html')

@login_required
def dashboard_paciente(request):
    consultas = Consulta.objects.filter(paciente=request.user.paciente)
    return render(request, 'frontend/dashboard_paciente.html', {'consultas': consultas})

@login_required
def dashboard_administrativo(request):
    pacientes = Paciente.objects.all()
    return render(request, 'frontend/dashboard_administrativo.html', {'pacientes': pacientes})

@login_required
def dashboard_medico(request):
    consultas = Consulta.objects.filter(medico=request.user.medico)
    return render(request, 'frontend/dashboard_medico.html', {'consultas': consultas})
