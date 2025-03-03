from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Consulta
from .forms import ConsultaForm

@login_required
def detalle_consulta(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk)
    context = {
        'consulta': consulta
    }
    return render(request, 'consultas/detalle_consulta.html', context)

@login_required
def crear_consulta(request):
    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('consultas:lista_consultas')
    else:
        form = ConsultaForm()
    return render(request, 'consultas/form_consulta.html', {'form': form})

@login_required
def listar_consultas(request):
    consultas = Consulta.objects.all()
    return render(request, 'consultas/listar_consultas.html', {'consultas': consultas})

@login_required
def editar_consulta(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk)
    if request.method == 'POST':
        form = ConsultaForm(request.POST, instance=consulta)
        if form.is_valid():
            form.save()
            return redirect('consultas:detalle_consulta', pk=consulta.pk)
    else:
        form = ConsultaForm(instance=consulta)
    return render(request, 'consultas/form_consulta.html', {'form': form})

@login_required
def eliminar_consulta(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk)
    if request.method == 'POST':
        consulta.delete()
        return redirect('consultas:lista_consultas')
    return render(request, 'consultas/eliminar_consulta.html', {'consulta': consulta})
