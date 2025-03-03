# App Importación Excel

## Descripción
Gestiona la importación de datos desde archivos Excel, incluyendo validación, corrección y seguimiento del proceso de importación.

## Modelos Implementados

### ExcelImport
- **Campos principales:**
  - `archivo`: FileField para el archivo Excel
  - `tipo_importacion`: Tipo de importación (AGENDA, HISTORICOS)
  - `estado`: Estado del proceso (PENDIENTE, EN_REVISION, CORREGIDO, etc.)
  - `usuario`: ForeignKey → Usuario
  - `fecha_subida`: Fecha de carga
  - `fecha_procesamiento`: Fecha de procesamiento
  - `registros_totales`: Cantidad total de registros
  - `registros_procesados`: Registros procesados exitosamente
  - `registros_con_error`: Registros con errores

### MapeoColumnas
- **Campos principales:**
  - `nombre_columna_excel`: Nombre de la columna en Excel
  - `campo_modelo`: Campo correspondiente en el modelo
  - `transformacion`: Tipo de transformación
  - `es_requerido`: Indica si el campo es obligatorio

### ReglaCorreccion
- **Campos principales:**
  - `campo`: Campo al que aplica la regla
  - `patron_original`: Patrón a identificar
  - `correccion`: Valor de reemplazo
  - `activa`: Estado de la regla

## Vistas Implementadas

### Importación
- `importar_excel/`: Carga inicial del archivo
- `previsualizar_excel/<pk>/`: Previsualización de datos
- `revisar_excel/`: Revisión y corrección
- `ver_resultados/<pk>/`: Resultados de importación

### Configuración
- `mapeo/`: Gestión de mapeos
- `reglas/`: Gestión de reglas de corrección

## Templates Implementados

### Importación
```html
# importar.html
- Formulario de carga
- Drag & drop para archivos
- Lista de importaciones recientes

# previsualizar.html
- Detalles de la importación
- Tabla de datos
- Validaciones y errores
- Botones de acción

# resultados.html
- Estadísticas de importación
- Gráfico de resultados
- Tabla de correcciones
- Barra de progreso
```

## Características Implementadas

### Validación de Datos
- Verificación de campos requeridos
- Validación de formatos
- Detección de duplicados
- Aplicación de reglas de corrección

### Interfaz de Usuario
- Carga de archivos con drag & drop
- Previsualización de datos
- Estadísticas en tiempo real
- Indicadores visuales de progreso

### Procesamiento
- Manejo asíncrono de importaciones
- Validación por lotes
- Correcciones automáticas
- Registro de errores

## Mejoras y Correcciones Realizadas

### Correcciones de Estilo
- Implementación de variables CSS para la barra de progreso:
```html
style="--progress-width: {{ tasa_exito }}%; width: var(--progress-width);"
```

### Mejoras en Modelos
- Campo `tipo_importacion` con valor por defecto 'HISTORICOS'
- Validaciones mejoradas para archivos Excel
- Manejo de errores en procesamiento

## Próximos Pasos
1. Implementar exportación de datos
2. Agregar más reglas de validación
3. Mejorar el sistema de correcciones
4. Implementar reportes detallados

## Consideraciones de Seguridad
- Validación de tipos de archivo
- Límite de tamaño de archivo (5MB)
- Registro de acciones de usuario
- Control de acceso por permisos

## Integración con Otras Apps
- Pacientes (importación de historias)
- Turnos (importación de agenda)
- Operaciones (importación de protocolos)
- Usuarios (permisos y auditoría)