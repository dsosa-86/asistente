from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import EstudioPrequirurgico, PrequirurgicoPaciente, TipoCirugia
from .forms import EstudioPrequirurgicoForm, PrequirurgicoPacienteForm
from .models import Operacion

@login_required
def lista_estudios_prequirurgicos(request):
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    tipo_cirugia = request.GET.get('tipo_cirugia', '')
    estudios = EstudioPrequirurgico.objects.all()
    if query:
        estudios = estudios.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query)
        )
    if tipo:
        estudios = estudios.filter(tipo=tipo)
    if tipo_cirugia:
        estudios = estudios.filter(tipo_cirugia_id=tipo_cirugia)
    paginator = Paginator(estudios, 10)
    page = request.GET.get('page')
    estudios_paginados = paginator.get_page(page)
    tipos_cirugia = TipoCirugia.objects.all()
    context = {
        'estudios': estudios_paginados,
        'tipos_cirugia': tipos_cirugia,
        'tipos_estudio': EstudioPrequirurgico.TIPOS,
        'query': query,
        'tipo_selected': tipo,
        'tipo_cirugia_selected': tipo_cirugia
    }
    return render(request, 'operaciones/estudios/lista.html', context)

@login_required
def detalle_estudio_prequirurgico(request, pk):
    estudio = get_object_or_404(EstudioPrequirurgico, pk=pk)
    pacientes_estudio = PrequirurgicoPaciente.objects.filter(estudio=estudio)
    context = {
        'estudio': estudio,
        'pacientes_estudio': pacientes_estudio
    }
    return render(request, 'operaciones/estudios/detalle.html', context)

@login_required
def crear_estudio_prequirurgico(request):
    if request.method == 'POST':
        form = EstudioPrequirurgicoForm(request.POST)
        if form.is_valid():
            estudio = form.save()
            messages.success(request, 'Estudio prequirúrgico creado exitosamente.')
            return redirect('operaciones:detalle_estudio', pk=estudio.pk)
    else:
        form = EstudioPrequirurgicoForm()
    return render(request, 'operaciones/estudios/form.html', {
        'form': form,
        'titulo': 'Crear Estudio Prequirúrgico'
    })

@login_required
def editar_estudio_prequirurgico(request, pk):
    estudio = get_object_or_404(EstudioPrequirurgico, pk=pk)
    if request.method == 'POST':
        form = EstudioPrequirurgicoForm(request.POST, instance=estudio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estudio prequirúrgico actualizado exitosamente.')
            return redirect('operaciones:detalle_estudio', pk=estudio.pk)
    else:
        form = EstudioPrequirurgicoForm(instance=estudio)
    return render(request, 'operaciones/estudios/form.html', {
        'form': form,
        'estudio': estudio,
        'titulo': 'Editar Estudio Prequirúrgico'
    })

@login_required
def eliminar_estudio_prequirurgico(request, pk):
    estudio = get_object_or_404(EstudioPrequirurgico, pk=pk)
    if request.method == 'POST':
        estudio.delete()
        messages.success(request, 'Estudio prequirúrgico eliminado exitosamente.')
        return redirect('operaciones:lista_estudios')
    return render(request, 'operaciones/estudios/eliminar.html', {
        'estudio': estudio
    })

@login_required
def lista_estudios_paciente(request, paciente_id):
    estudios = PrequirurgicoPaciente.objects.filter(paciente_id=paciente_id)
    context = {
        'estudios': estudios,
        'paciente_id': paciente_id
    }
    return render(request, 'operaciones/estudios/lista_paciente.html', context)

@login_required
def cargar_resultado_estudio(request, estudio_paciente_id):
    estudio_paciente = get_object_or_404(PrequirurgicoPaciente, pk=estudio_paciente_id)
    if request.method == 'POST':
        form = PrequirurgicoPacienteForm(request.POST, request.FILES, instance=estudio_paciente)
        if form.is_valid():
            estudio = form.save(commit=False)
            estudio.estado = 'REALIZADO'
            estudio.save()
            messages.success(request, 'Resultado cargado exitosamente.')
            return redirect('operaciones:lista_estudios_paciente', paciente_id=estudio.paciente.id)
    else:
        form = PrequirurgicoPacienteForm(instance=estudio_paciente)
    return render(request, 'operaciones/estudios/cargar_resultado.html', {
        'form': form,
        'estudio_paciente': estudio_paciente
    })

@login_required
def actualizar_estado_estudio(request, estudio_paciente_id):
    if request.method == 'POST':
        estudio_paciente = get_object_or_404(PrequirurgicoPaciente, pk=estudio_paciente_id)
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(PrequirurgicoPaciente.ESTADOS):
            estudio_paciente.estado = nuevo_estado
            estudio_paciente.save()
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def detalle_operacion(request, pk):
    operacion = get_object_or_404(Operacion, pk=pk)
    context = {
        'operacion': operacion,
        'estudios': PrequirurgicoPaciente.objects.filter(operacion=operacion)
    }
    return render(request, 'operaciones/detalle_operacion.html', context)
