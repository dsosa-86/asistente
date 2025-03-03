# API REST

## Descripción
API REST para la gestión de pacientes, estudios prequirúrgicos y datos relacionados.

## Configuración

### Dependencias Requeridas
```bash
# Archivo requirements/base.txt
djangorestframework>=3.14.0
django-filter>=23.5
markdown>=3.5.1
```

### Configuración en settings.py
```python
INSTALLED_APPS = [
    # ... otras apps ...
    'rest_framework',
    'django_filters',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}
```

## Endpoints Disponibles

### Pacientes

#### Lista y Creación
- **GET** `/api/pacientes/`
  - Lista todos los pacientes
  - Soporta filtros: `dni`, `obra_social`
  - Búsqueda por: `nombre`, `apellido`, `dni`
  - Ordenamiento por: `apellido`, `nombre`, `fecha_nacimiento`

- **POST** `/api/pacientes/`
  - Crea un nuevo paciente
  - Requiere todos los campos obligatorios

#### Operaciones por ID
- **GET** `/api/pacientes/{id}/`
  - Retorna detalles del paciente
  - Incluye estudios pendientes, próximas operaciones y últimas consultas

- **PUT** `/api/pacientes/{id}/`
  - Actualiza todos los campos del paciente

- **PATCH** `/api/pacientes/{id}/`
  - Actualiza parcialmente los datos del paciente

- **DELETE** `/api/pacientes/{id}/`
  - Elimina el paciente

#### Endpoints Adicionales
- **GET** `/api/pacientes/{id}/estudios/`
  - Lista todos los estudios prequirúrgicos del paciente

- **GET** `/api/pacientes/{id}/estadisticas/`
  - Retorna estadísticas del paciente:
    - Total de consultas
    - Consultas del último año
    - Total de operaciones
    - Estudios pendientes
    - Estudios por tipo

### Estudios Prequirúrgicos

#### Lista y Creación
- **GET** `/api/estudios-prequirurgicos/`
  - Lista todos los estudios
  - Filtros: `paciente`, `estado`, `estudio__tipo`
  - Ordenamiento por: `fecha_solicitud`, `fecha_realizacion`

- **POST** `/api/estudios-prequirurgicos/`
  - Crea un nuevo estudio prequirúrgico

#### Operaciones por ID
- **GET** `/api/estudios-prequirurgicos/{id}/`
  - Retorna detalles del estudio

- **PUT/PATCH** `/api/estudios-prequirurgicos/{id}/`
  - Actualiza el estudio

- **DELETE** `/api/estudios-prequirurgicos/{id}/`
  - Elimina el estudio

#### Endpoints Adicionales
- **POST** `/api/estudios-prequirurgicos/{id}/cambiar-estado/`
  - Actualiza el estado del estudio
  - Estados válidos según modelo PrequirurgicoPaciente

## Serializers

### PacienteSerializer
```python
fields = [
    'id', 'nombre', 'apellido', 'dni', 'fecha_nacimiento',
    'sexo', 'direccion', 'telefono', 'email', 'obra_social',
    'numero_afiliacion', 'antecedentes_medicos', 'alergias',
    'medicacion_actual', 'grupo_sanguineo'
]
```

### PacienteDetalleSerializer
Extiende PacienteSerializer y agrega:
- `estudios_pendientes`
- `proximas_operaciones`
- `ultimas_consultas`

### PrequirurgicoPacienteSerializer
```python
fields = [
    'id', 'paciente', 'estudio', 'estado', 'fecha_solicitud',
    'fecha_realizacion', 'resultado', 'archivo'
]
```

## Permisos
- Todos los endpoints requieren autenticación
- Se utiliza el sistema de permisos por defecto de Django REST Framework

## Paginación
- Paginación por números de página
- 10 elementos por página por defecto
- Personalizable en settings.py

## Ejemplos de Uso

### Listar Pacientes con Filtros
```http
GET /api/pacientes/?obra_social=1&ordering=-apellido
```

### Crear Paciente
```http
POST /api/pacientes/
Content-Type: application/json

{
    "nombre": "Juan",
    "apellido": "Pérez",
    "dni": "12345678",
    "fecha_nacimiento": "1980-01-01"
}
```

### Actualizar Estado de Estudio
```http
POST /api/estudios-prequirurgicos/1/cambiar-estado/
Content-Type: application/json

{
    "estado": "REALIZADO"
}
```

## Consideraciones de Seguridad
1. Autenticación requerida para todos los endpoints
2. Validación de datos en serializers
3. Filtrado de información sensible
4. Control de acceso basado en permisos

## Próximas Mejoras
1. Implementar autenticación por tokens
2. Agregar rate limiting
3. Mejorar documentación automática
4. Implementar caché para endpoints frecuentes 