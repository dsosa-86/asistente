from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Notificacion, ConfiguracionNotificacion
from .services import ServicioNotificaciones

@login_required
def lista_notificaciones(request):
    """Vista para mostrar todas las notificaciones del usuario"""
    notificaciones = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(notificaciones, 20)  # 20 notificaciones por página
    page = request.GET.get('page')
    notificaciones_paginadas = paginator.get_page(page)
    
    return render(request, 'notificaciones/lista.html', {
        'notificaciones': notificaciones_paginadas
    })

@login_required
def configuracion_notificaciones(request):
    """Vista para configurar las preferencias de notificaciones"""
    config, created = ConfiguracionNotificacion.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        config.email_activo = request.POST.get('email_activo') == 'on'
        config.sms_activo = request.POST.get('sms_activo') == 'on'
        config.sistema_activo = request.POST.get('sistema_activo') == 'on'
        config.whatsapp_activo = request.POST.get('whatsapp_activo') == 'on'
        config.horario_inicio = request.POST.get('horario_inicio')
        config.horario_fin = request.POST.get('horario_fin')
        config.dias_habiles = request.POST.get('dias_habiles') == 'on'
        config.save()
        
        messages.success(request, 'Configuración actualizada correctamente')
        return redirect('notificaciones:configuracion')
        
    return render(request, 'notificaciones/configuracion.html', {
        'config': config
    })

@login_required
@require_POST
def marcar_como_leida(request, notificacion_id):
    """Vista para marcar una notificación como leída"""
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
    notificacion.marcar_como_leido()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    
    messages.success(request, 'Notificación marcada como leída')
    return redirect('notificaciones:lista')

@login_required
@require_POST
def marcar_todas_como_leidas(request):
    """Vista para marcar todas las notificaciones como leídas"""
    ServicioNotificaciones.marcar_como_leidas(request.user)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    
    messages.success(request, 'Todas las notificaciones han sido marcadas como leídas')
    return redirect('notificaciones:lista')

@login_required
def obtener_notificaciones_pendientes(request):
    """Vista para obtener las notificaciones pendientes (para actualización en tiempo real)"""
    notificaciones = ServicioNotificaciones.obtener_notificaciones_pendientes(request.user)
    
    return JsonResponse({
        'notificaciones': [{
            'id': n.id,
            'tipo': n.get_tipo_display(),
            'titulo': n.titulo,
            'mensaje': n.mensaje,
            'fecha': n.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
            'prioridad': n.get_prioridad_display()
        } for n in notificaciones]
    })

@login_required
def listar_notificaciones(request):
    notificaciones = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    return render(request, 'notificaciones/listar_notificaciones.html', {'notificaciones': notificaciones})

@login_required
def marcar_como_leida(request, pk):
    notificacion = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
    notificacion.leida = True
    notificacion.save()
    return redirect('listar_notificaciones')