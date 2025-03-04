from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import InsumoMedico
from .forms import InsumoMedicoForm

def lista_insumos_medicos(request):
    insumos_medicos = InsumoMedico.objects.all()
    return render(request, 'insumos_medicos/lista_insumos_medicos.html', {'insumos_medicos': insumos_medicos})

def crear_insumo_medico(request):
    if request.method == 'POST':
        form = InsumoMedicoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Insumo médico creado correctamente.")
            return redirect('insumos_medicos:lista_insumos_medicos')
    else:
        form = InsumoMedicoForm()
    return render(request, 'insumos_medicos/form_insumo_medico.html', {'form': form})

def editar_insumo_medico(request, pk):
    insumo_medico = get_object_or_404(InsumoMedico, pk=pk)
    if request.method == 'POST':
        form = InsumoMedicoForm(request.POST, instance=insumo_medico)
        if form.is_valid():
            form.save()
            messages.success(request, "Insumo médico actualizado correctamente.")
            return redirect('insumos_medicos:lista_insumos_medicos')
    else:
        form = InsumoMedicoForm(instance=insumo_medico)
    return render(request, 'insumos_medicos/form_insumo_medico.html', {'form': form})

def eliminar_insumo_medico(request, pk):
    insumo_medico = get_object_or_404(InsumoMedico, pk=pk)
    if request.method == 'POST':
        insumo_medico.delete()
        messages.success(request, "Insumo médico eliminado correctamente.")
        return redirect('insumos_medicos:lista_insumos_medicos')
    return render(request, 'insumos_medicos/eliminar_insumo_medico.html', {'insumo_medico': insumo_medico})
