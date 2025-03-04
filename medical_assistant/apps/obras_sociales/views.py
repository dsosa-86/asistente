from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import ObraSocial
from .forms import ObraSocialForm

def lista_obras_sociales(request):
    obras_sociales = ObraSocial.objects.all()
    return render(request, 'obras_sociales/lista_obras_sociales.html', {'obras_sociales': obras_sociales})

def crear_obra_social(request):
    if request.method == 'POST':
        form = ObraSocialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Obra social creada correctamente.")
            return redirect('obras_sociales:lista_obras_sociales')
    else:
        form = ObraSocialForm()
    return render(request, 'obras_sociales/form_obra_social.html', {'form': form})

def editar_obra_social(request, pk):
    obra_social = get_object_or_404(ObraSocial, pk=pk)
    if request.method == 'POST':
        form = ObraSocialForm(request.POST, instance=obra_social)
        if form.is_valid():
            form.save()
            messages.success(request, "Obra social actualizada correctamente.")
            return redirect('obras_sociales:lista_obras_sociales')
    else:
        form = ObraSocialForm(instance=obra_social)
    return render(request, 'obras_sociales/form_obra_social.html', {'form': form})

def eliminar_obra_social(request, pk):
    obra_social = get_object_or_404(ObraSocial, pk=pk)
    if request.method == 'POST':
        obra_social.delete()
        messages.success(request, "Obra social eliminada correctamente.")
        return redirect('obras_sociales:lista_obras_sociales')
    return render(request, 'obras_sociales/eliminar_obra_social.html', {'obra_social': obra_social})
