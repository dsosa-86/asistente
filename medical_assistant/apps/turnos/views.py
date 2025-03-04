from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Turno
from .forms import TurnoForm

def lista_turnos(request):
    turnos = Turno.objects.all()
    return render(request, 'turnos/lista_turnos.html', {'turnos': turnos})

def crear_turno(request):
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Turno creado correctamente.")
            return redirect('turnos:lista_turnos')
    else:
        form = TurnoForm()
    return render(request, 'turnos/form_turno.html', {'form': form})

def editar_turno(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    if request.method == 'POST':
        form = TurnoForm(request.POST, instance=turno)
        if form.is_valid():
            form.save()
            messages.success(request, "Turno actualizado correctamente.")
            return redirect('turnos:lista_turnos')
    else:
        form = TurnoForm(instance=turno)
    return render(request, 'turnos/form_turno.html', {'form': form})

def eliminar_turno(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    if request.method == 'POST':
        turno.delete()
        messages.success(request, "Turno eliminado correctamente.")
        return redirect('turnos:lista_turnos')
    return render(request, 'turnos/eliminar_turno.html', {'turno': turno})
