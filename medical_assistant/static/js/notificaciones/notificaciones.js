document.addEventListener('DOMContentLoaded', function() {
    // Configuración de la actualización periódica
    const INTERVALO_ACTUALIZACION = 30000; // 30 segundos
    let ultimaActualizacion = new Date();
    
    // Función para verificar nuevas notificaciones
    function verificarNotificaciones() {
        fetch('/notificaciones/pendientes/')
            .then(response => response.json())
            .then(data => {
                if (data.notificaciones && data.notificaciones.length > 0) {
                    actualizarContadorNotificaciones(data.notificaciones.length);
                    mostrarNuevasNotificaciones(data.notificaciones);
                }
            })
            .catch(error => console.error('Error al verificar notificaciones:', error));
    }
    
    // Función para actualizar el contador de notificaciones
    function actualizarContadorNotificaciones(cantidad) {
        const contador = document.getElementById('contador-notificaciones');
        if (contador) {
            contador.textContent = cantidad;
            contador.style.display = cantidad > 0 ? 'inline' : 'none';
        }
    }
    
    // Función para mostrar nuevas notificaciones
    function mostrarNuevasNotificaciones(notificaciones) {
        const contenedor = document.querySelector('.list-group');
        if (!contenedor) return;
        
        notificaciones.forEach(notificacion => {
            // Verificar si la notificación ya existe
            if (!document.querySelector(`[data-notificacion-id="${notificacion.id}"]`)) {
                const elemento = crearElementoNotificacion(notificacion);
                contenedor.insertBefore(elemento, contenedor.firstChild);
            }
        });
    }
    
    // Función para crear el elemento HTML de una notificación
    function crearElementoNotificacion(notificacion) {
        const div = document.createElement('div');
        div.className = 'list-group-item list-group-item-action notification-new';
        div.setAttribute('data-notificacion-id', notificacion.id);
        
        const icono = obtenerIconoNotificacion(notificacion.tipo);
        
        div.innerHTML = `
            <div class="d-flex w-100 justify-content-between">
                <h5 class="mb-1">
                    ${icono}
                    ${notificacion.titulo}
                </h5>
                <small class="text-muted">${notificacion.fecha}</small>
            </div>
            <p class="mb-1">${notificacion.mensaje}</p>
            <div class="d-flex justify-content-between align-items-center mt-2">
                <small>
                    <span class="badge ${obtenerClasePrioridad(notificacion.prioridad)}">
                        ${notificacion.prioridad}
                    </span>
                </small>
                <form action="/notificaciones/marcar-leida/${notificacion.id}/" method="post" class="d-inline">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${obtenerCSRFToken()}">
                    <button type="submit" class="btn btn-sm btn-outline-secondary">
                        <i class="fas fa-check"></i> Marcar como leída
                    </button>
                </form>
            </div>
        `;
        
        return div;
    }
    
    // Función para obtener el ícono según el tipo de notificación
    function obtenerIconoNotificacion(tipo) {
        const iconos = {
            'Correo Electrónico': '<i class="fas fa-envelope text-primary"></i>',
            'Mensaje de Texto': '<i class="fas fa-sms text-success"></i>',
            'Notificación del Sistema': '<i class="fas fa-bell text-warning"></i>'
        };
        return iconos[tipo] || '<i class="fas fa-bell text-warning"></i>';
    }
    
    // Función para obtener la clase de la badge según la prioridad
    function obtenerClasePrioridad(prioridad) {
        const clases = {
            'Alta': 'bg-danger',
            'Media': 'bg-warning',
            'Baja': 'bg-info'
        };
        return clases[prioridad] || 'bg-secondary';
    }
    
    // Función para obtener el token CSRF
    function obtenerCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
    
    // Iniciar verificación periódica
    setInterval(verificarNotificaciones, INTERVALO_ACTUALIZACION);
    
    // Verificar inmediatamente al cargar la página
    verificarNotificaciones();
    
    // Manejar marcado de notificaciones como leídas
    document.addEventListener('submit', function(e) {
        if (e.target.matches('form[action^="/notificaciones/marcar-leida/"]')) {
            e.preventDefault();
            const form = e.target;
            
            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': obtenerCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    const notificacion = form.closest('.list-group-item');
                    notificacion.classList.remove('unread');
                    form.remove();
                }
            })
            .catch(error => console.error('Error al marcar como leída:', error));
        }
    });
}); 