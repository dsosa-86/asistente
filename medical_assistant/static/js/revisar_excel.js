// static/js/revisar_excel.js
document.addEventListener('DOMContentLoaded', function() {
    const tabla = document.querySelector('.data-table');
    const guardarBtn = document.getElementById('guardarDatos');
    const forzarValidacionCheck = document.getElementById('forzarValidacion');

    // Hacer las celdas editables
    function hacerCeldasEditables() {
        const celdas = tabla.querySelectorAll('td[data-editable="true"]');
        celdas.forEach(celda => {
            celda.addEventListener('click', function() {
                if (this.querySelector('input')) return;
                
                const valorOriginal = this.textContent;
                const input = document.createElement('input');
                input.type = 'text';
                input.value = valorOriginal;
                input.className = 'form-control form-control-sm';
                
                input.addEventListener('blur', function() {
                    const nuevoValor = this.value;
                    celda.textContent = nuevoValor;
                    validarCelda(celda, nuevoValor);
                });

                this.textContent = '';
                this.appendChild(input);
                input.focus();
            });
        });
    }

    // Validar celda individual
    function validarCelda(celda, valor) {
        const tipo = celda.dataset.tipo;
        const fila = celda.closest('tr').dataset.fila;
        
        // Limpiar clases de error previas
        celda.classList.remove('error-cell', 'warning-cell');

        // Validaciones específicas
        switch (tipo) {
            case 'dni':
                if (!/^\d+$/.test(valor)) {
                    marcarError(celda, fila, 'DNI debe contener solo números');
                }
                break;
            case 'fecha':
                if (!validarFormatoFecha(valor)) {
                    marcarError(celda, fila, 'Formato de fecha inválido (dd-mm-yyyy)');
                }
                break;
            case 'email':
                if (valor && !valor.includes('@')) {
                    marcarError(celda, fila, 'Email inválido');
                }
                break;
            // Agregar más validaciones según sea necesario
        }
    }

    // Marcar error en celda
    function marcarError(celda, fila, mensaje) {
        celda.classList.add('error-cell');
        actualizarResumenErrores('agregar', {
            fila: fila,
            campo: celda.dataset.campo,
            mensaje: mensaje
        });
    }

    // Validar formato de fecha
    function validarFormatoFecha(fecha) {
        const regex = /^(\d{2})-(\d{2})-(\d{4})$/;
        if (!regex.test(fecha)) return false;
        
        const [, dia, mes, anio] = fecha.match(regex);
        const fechaObj = new Date(anio, mes - 1, dia);
        return fechaObj.getDate() == dia && 
               fechaObj.getMonth() == mes - 1 && 
               fechaObj.getFullYear() == anio;
    }

    // Guardar datos
    guardarBtn.addEventListener('click', async function() {
        try {
            const response = await fetch('/importacion/guardar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    datos: obtenerDatosTabla(),
                    forzar_validacion: forzarValidacionCheck.checked
                })
            });

            const resultado = await response.json();
            
            if (resultado.errores && resultado.errores.length > 0) {
                mostrarErrores(resultado.errores);
            } else {
                mostrarExito(resultado);
            }
        } catch (error) {
            console.error('Error al guardar:', error);
            mostrarError('Error al guardar los datos');
        }
    });

    // Inicializar
    hacerCeldasEditables();
});
