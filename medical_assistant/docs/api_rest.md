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
  - Soporta filtros: `dni`, `obra_social`, `nombre`
  - Búsqueda por: `nombre`, `apellido`
  - Ordenamiento por: `fecha_registro`

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

### Operaciones
- **GET** `/api/operaciones/`
  - Lista todas las operaciones
  - Soporta filtros: `paciente`, `tipo_cirugia`, `estado`
  - Búsqueda por: `paciente__nombre`, `tipo_cirugia__nombre`
  - Ordenamiento por: `fecha_programada`

- **POST** `/api/operaciones/programar/`
  - Programa una nueva operación
  - Requiere todos los campos obligatorios

- **GET** `/api/operaciones/{id}/`
  - Retorna detalles de la operación

- **PUT** `/api/operaciones/{id}/`
  - Actualiza todos los campos de la operación

- **PATCH** `/api/operaciones/{id}/`
  - Actualiza parcialmente los datos de la operación

- **DELETE** `/api/operaciones/{id}/`
  - Elimina la operación

### Estudios Prequirúrgicos
- **GET** `/api/estudios/`
  - Lista todos los estudios prequirúrgicos
  - Soporta filtros: `tipo`, `nombre`
  - Búsqueda por: `nombre`
  - Ordenamiento por: `fecha_creacion`

- **POST** `/api/estudios/`
  - Crea un nuevo estudio prequirúrgico
  - Requiere todos los campos obligatorios

- **GET** `/api/estudios/{id}/`
  - Retorna detalles del estudio prequirúrgico

- **PUT** `/api/estudios/{id}/`
  - Actualiza todos los campos del estudio prequirúrgico

- **PATCH** `/api/estudios/{id}/`
  - Actualiza parcialmente los datos del estudio prequirúrgico

- **DELETE** `/api/estudios/{id}/`
  - Elimina el estudio prequirúrgico

### Importación
- **POST** `/api/importar/`
  - Importa un archivo Excel
  - Requiere el archivo y tipo de importación

- **GET** `/api/importar/{id}/estado/`
  - Retorna el estado de la importación

- **POST** `/api/importar/{id}/corregir/`
  - Corrige datos de la importación

### Turnos
- **GET** `/api/turnos/`
  - Lista todos los turnos
  - Soporta filtros: `paciente`, `medico`, `estado`
  - Búsqueda por: `paciente__nombre`, `medico__nombre`
  - Ordenamiento por: `fecha_hora`

- **POST** `/api/turnos/`
  - Crea un nuevo turno
  - Requiere todos los campos obligatorios

- **GET** `/api/turnos/{id}/`
  - Retorna detalles del turno

- **PUT** `/api/turnos/{id}/`
  - Actualiza todos los campos del turno

- **PATCH** `/api/turnos/{id}/`
  - Actualiza parcialmente los datos del turno

- **DELETE** `/api/turnos/{id}/`
  - Elimina el turno

### Informes
- **GET** `/api/informes/`
  - Lista todos los informes
  - Soporta filtros: `paciente`, `medico`, `estado`
  - Búsqueda por: `paciente__nombre`, `medico__nombre`
  - Ordenamiento por: `fecha_hora`

- **POST** `/api/informes/`
  - Crea un nuevo informe
  - Requiere todos los campos obligatorios

- **GET** `/api/informes/{id}/`
  - Retorna detalles del informe

- **PUT** `/api/informes/{id}/`
  - Actualiza todos los campos del informe

- **PATCH** `/api/informes/{id}/`
  - Actualiza parcialmente los datos del informe

- **DELETE** `/api/informes/{id}/`
  - Elimina el informe


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