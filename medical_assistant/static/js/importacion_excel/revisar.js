// Configuración inicial
document.addEventListener('DOMContentLoaded', function() {
    initializeForm();
    setupEventListeners();
    setupSearch();
    setupFilters();
});

// Inicialización del formulario
function initializeForm() {
    const form = document.getElementById('correccionForm');
    const inputs = form.querySelectorAll('input[type="text"]');
    
    inputs.forEach(input => {
        // Marcar campos modificados
        input.addEventListener('input', function() {
            const isModified = this.value !== this.dataset.original;
            this.classList.toggle('modified', isModified);
            updatePreview(this);
        });

        // Sugerencias automáticas
        input.addEventListener('focus', function() {
            showSuggestions(this);
        });
    });
}

// Configuración de event listeners
function setupEventListeners() {
    // Prevenir envío accidental con Enter
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.target.type === 'text') {
            e.preventDefault();
            const inputs = Array.from(document.querySelectorAll('input[type="text"]'));
            const currentIndex = inputs.indexOf(e.target);
            if (currentIndex < inputs.length - 1) {
                inputs[currentIndex + 1].focus();
            }
        }
    });

    // Manejar envío del formulario
    document.getElementById('correccionForm').addEventListener('submit', function(e) {
        e.preventDefault();
        if (validateForm()) {
            prepareDataAndSubmit(this);
        }
    });

    // Limpiar búsqueda
    document.getElementById('clearSearch').addEventListener('click', function() {
        document.getElementById('searchInput').value = '';
        filterTable('');
    });
}

// Configuración de búsqueda
function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    let timeoutId;

    searchInput.addEventListener('input', function() {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            filterTable(this.value);
        }, 300);
    });
}

// Configuración de filtros
function setupFilters() {
    document.getElementById('filterSheet').addEventListener('change', function() {
        const selectedSheet = this.value;
        const sections = document.querySelectorAll('.sheet-section');
        
        sections.forEach(section => {
            if (selectedSheet === 'all' || section.dataset.sheet === selectedSheet) {
                section.style.display = 'block';
            } else {
                section.style.display = 'none';
            }
        });
    });
}

// Filtrado de tabla
function filterTable(searchText) {
    const rows = document.querySelectorAll('tbody tr');
    const searchLower = searchText.toLowerCase();

    rows.forEach(row => {
        const text = Array.from(row.querySelectorAll('input'))
            .map(input => input.value)
            .join(' ')
            .toLowerCase();

        if (text.includes(searchLower)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Mostrar sugerencias
function showSuggestions(input) {
    const key = input.dataset.key;
    const value = input.value;
    const suggestionsContainer = input.nextElementSibling;

    // Obtener sugerencias del servidor
    fetch(`/importacion_excel/api/sugerir-correccion/?campo=${key}&valor=${encodeURIComponent(value)}`)
        .then(response => response.json())
        .then(data => {
            if (data.sugerencias && data.sugerencias.length > 0) {
                suggestionsContainer.innerHTML = data.sugerencias
                    .map(sugerencia => `
                        <div class="suggestion-item" onclick="applySuggestion('${input.id}', '${sugerencia}')">
                            ${sugerencia}
                        </div>
                    `)
                    .join('');
                suggestionsContainer.classList.remove('d-none');
            }
        });
}

// Aplicar sugerencia
function applySuggestion(inputId, value) {
    const input = document.getElementById(inputId);
    input.value = value;
    input.dispatchEvent(new Event('input'));
    input.nextElementSibling.classList.add('d-none');
}

// Actualizar vista previa
function updatePreview(input) {
    const previewContent = document.querySelector('.preview-content');
    const modified = document.querySelectorAll('.modified');
    
    let previewHtml = '<h6>Cambios Realizados:</h6><ul>';
    modified.forEach(field => {
        previewHtml += `
            <li>
                <strong>${field.dataset.key}:</strong>
                <del class="text-danger">${field.dataset.original}</del>
                <span class="text-success">${field.value}</span>
            </li>
        `;
    });
    previewHtml += '</ul>';
    
    previewContent.innerHTML = previewHtml;
}

// Validar formulario
function validateForm() {
    let isValid = true;
    const requiredFields = document.querySelectorAll('[data-required="true"]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Preparar datos y enviar
function prepareDataAndSubmit(form) {
    const data = {};
    const sections = document.querySelectorAll('.sheet-section');
    
    sections.forEach(section => {
        const sheetName = section.dataset.sheet;
        data[sheetName] = [];
        
        const rows = section.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const rowData = {};
            row.querySelectorAll('input').forEach(input => {
                rowData[input.dataset.key] = input.value;
            });
            data[sheetName].push(rowData);
        });
    });

    document.getElementById('excel_data_corregido').value = JSON.stringify(data);
    form.submit();
}

// Utilidades
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Manejo de atajos de teclado
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + S para guardar
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        document.querySelector('button[type="submit"]').click();
    }
}); 