// Gestión de la interfaz de usuario para importación Excel

class ImportacionUI {
    constructor() {
        this.initializeComponents();
        this.setupEventListeners();
    }

    initializeComponents() {
        // Componentes principales
        this.fileInput = document.getElementById('archivo');
        this.progressBar = document.querySelector('.progress-bar');
        this.previewContainer = document.getElementById('preview-container');
        this.toastContainer = document.querySelector('.toast-container');
        
        // Inicializar tooltips y popovers de Bootstrap
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }

    setupEventListeners() {
        // Evento de cambio de archivo
        if (this.fileInput) {
            this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }

        // Eventos de arrastrar y soltar
        const dropZone = document.querySelector('.drop-zone');
        if (dropZone) {
            dropZone.addEventListener('dragover', (e) => this.handleDragOver(e));
            dropZone.addEventListener('drop', (e) => this.handleDrop(e));
        }

        // Botón de procesar
        const processButton = document.getElementById('process-button');
        if (processButton) {
            processButton.addEventListener('click', () => this.startProcessing());
        }
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.validateAndPreviewFile(file);
        }
    }

    handleDragOver(event) {
        event.preventDefault();
        event.currentTarget.classList.add('drag-over');
    }

    handleDrop(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('drag-over');
        
        const file = event.dataTransfer.files[0];
        if (file) {
            this.validateAndPreviewFile(file);
        }
    }

    async validateAndPreviewFile(file) {
        // Validar tipo de archivo
        if (!this.isValidExcelFile(file)) {
            this.showToast('error', 'Archivo no válido', 'Solo se permiten archivos Excel (.xlsx, .xls)');
            return;
        }

        // Mostrar preview
        await this.showFilePreview(file);
    }

    isValidExcelFile(file) {
        const validTypes = [
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ];
        return validTypes.includes(file.type);
    }

    async showFilePreview(file) {
        try {
            const formData = new FormData();
            formData.append('archivo', file);

            const response = await fetch('/importacion/preview/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            if (!response.ok) throw new Error('Error en la previsualización');

            const data = await response.json();
            this.renderPreview(data);
            this.showToast('success', 'Archivo cargado', 'La previsualización está lista');
        } catch (error) {
            this.showToast('error', 'Error', 'No se pudo previsualizar el archivo');
            console.error('Error:', error);
        }
    }

    renderPreview(data) {
        if (!this.previewContainer) return;

        // Limpiar contenedor
        this.previewContainer.innerHTML = '';

        // Crear tabla de previsualización
        const table = document.createElement('table');
        table.className = 'table table-striped table-hover';
        
        // Encabezados
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        Object.keys(data.columns).forEach(column => {
            const th = document.createElement('th');
            th.textContent = column;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Datos
        const tbody = document.createElement('tbody');
        data.preview.forEach(row => {
            const tr = document.createElement('tr');
            Object.values(row).forEach(cell => {
                const td = document.createElement('td');
                td.textContent = cell;
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        this.previewContainer.appendChild(table);
    }

    async startProcessing() {
        try {
            this.showProgress();
            const importId = document.getElementById('import-id').value;
            
            const response = await fetch(`/importacion/${importId}/procesar/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCsrfToken(),
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) throw new Error('Error al iniciar el procesamiento');

            const data = await response.json();
            this.monitorProgress(data.task_id);
        } catch (error) {
            this.hideProgress();
            this.showToast('error', 'Error', 'No se pudo iniciar el procesamiento');
            console.error('Error:', error);
        }
    }

    showProgress() {
        if (this.progressBar) {
            this.progressBar.style.width = '0%';
            this.progressBar.parentElement.style.display = 'block';
        }
    }

    hideProgress() {
        if (this.progressBar) {
            this.progressBar.parentElement.style.display = 'none';
        }
    }

    updateProgress(percentage) {
        if (this.progressBar) {
            this.progressBar.style.width = `${percentage}%`;
            this.progressBar.setAttribute('aria-valuenow', percentage);
        }
    }

    showToast(type, title, message) {
        if (!this.toastContainer) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type} fade show`;
        toast.innerHTML = `
            <div class="toast-header">
                <strong class="me-auto">${title}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">${message}</div>
        `;

        this.toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Remover después de mostrarse
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    async monitorProgress(taskId) {
        const checkProgress = async () => {
            try {
                const response = await fetch(`/importacion/progress/${taskId}/`);
                const data = await response.json();

                if (data.state === 'PROGRESS') {
                    this.updateProgress(data.progress);
                    setTimeout(checkProgress, 1000);
                } else if (data.state === 'SUCCESS') {
                    this.updateProgress(100);
                    this.showToast('success', 'Completado', 'Procesamiento finalizado con éxito');
                    setTimeout(() => window.location.href = data.result_url, 2000);
                } else if (data.state === 'FAILURE') {
                    this.hideProgress();
                    this.showToast('error', 'Error', 'Error en el procesamiento');
                }
            } catch (error) {
                this.hideProgress();
                this.showToast('error', 'Error', 'Error al monitorear el progreso');
                console.error('Error:', error);
            }
        };

        checkProgress();
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new ImportacionUI();
}); 