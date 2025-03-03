# Documentación de la API

## Descripción General
Esta documentación cubre los endpoints de la API del proyecto Asistente Médico.

## Endpoints

### Consultas
- `GET /api/consultas/`: Lista de consultas
- `POST /api/consultas/`: Crear consulta
- `GET /api/consultas/{id}/`: Detalle de consulta
- `PUT /api/consultas/{id}/`: Actualizar consulta
- `DELETE /api/consultas/{id}/`: Eliminar consulta

### Pacientes
- `GET /api/pacientes/`: Lista de pacientes
- `POST /api/pacientes/`: Crear paciente
- `GET /api/pacientes/{id}/`: Detalle de paciente
- `PUT /api/pacientes/{id}/`: Actualizar paciente
- `DELETE /api/pacientes/{id}/`: Eliminar paciente

### Médicos
- `GET /api/medicos/`: Lista de médicos
- `POST /api/medicos/`: Crear médico
- `GET /api/medicos/{id}/`: Detalle de médico
- `PUT /api/medicos/{id}/`: Actualizar médico
- `DELETE /api/medicos/{id}/`: Eliminar médico

## Ejemplos de Solicitudes y Respuestas

### Consultas

#### Obtener Lista de Consultas
**Solicitud:**
```http
GET /api/consultas/
```

**Respuesta:**
```json
[
    {
        "id": 1,
        "paciente": 1,
        "medico": 1,
        "fecha_hora": "2023-10-10T10:00:00Z",
        "diagnostico": "Diagnostico Test",
        "tratamiento": "Tratamiento Test"
    }
]
```

#### Crear Consulta
**Solicitud:**
```http
POST /api/consultas/
Content-Type: application/json

{
    "paciente": 1,
    "medico": 1,
    "fecha_hora": "2023-10-10T10:00:00Z",
    "diagnostico": "Diagnostico Test",
    "tratamiento": "Tratamiento Test"
}
```

**Respuesta:**
```json
{
    "id": 1,
    "paciente": 1,
    "medico": 1,
    "fecha_hora": "2023-10-10T10:00:00Z",
    "diagnostico": "Diagnostico Test",
    "tratamiento": "Tratamiento Test"
}
```

#### Obtener Detalle de Consulta
**Solicitud:**
```http
GET /api/consultas/1/
```

**Respuesta:**
```json
{
    "id": 1,
    "paciente": 1,
    "medico": 1,
    "fecha_hora": "2023-10-10T10:00:00Z",
    "diagnostico": "Diagnostico Test",
    "tratamiento": "Tratamiento Test"
}
```

#### Actualizar Consulta
**Solicitud:**
```http
PUT /api/consultas/1/
Content-Type: application/json

{
    "paciente": 1,
    "medico": 1,
    "fecha_hora": "2023-10-11T10:00:00Z",
    "diagnostico": "Diagnostico Editado",
    "tratamiento": "Tratamiento Editado"
}
```

**Respuesta:**
```json
{
    "id": 1,
    "paciente": 1,
    "medico": 1,
    "fecha_hora": "2023-10-11T10:00:00Z",
    "diagnostico": "Diagnostico Editado",
    "tratamiento": "Tratamiento Editado"
}
```

#### Eliminar Consulta
**Solicitud:**
```http
DELETE /api/consultas/1/
```

**Respuesta:**
```http
204 No Content
```

### Pacientes

#### Obtener Lista de Pacientes
**Solicitud:**
```http
GET /api/pacientes/
```

**Respuesta:**
```json
[
    {
        "id": 1,
        "nombre": "Paciente Test",
        "dni": "12345678",
        "obra_social": "Obra Social Test"
    }
]
```

#### Crear Paciente
**Solicitud:**
```http
POST /api/pacientes/
Content-Type: application/json

{
    "nombre": "Paciente Test",
    "dni": "12345678",
    "obra_social": "Obra Social Test"
}
```

**Respuesta:**
```json
{
    "id": 1,
    "nombre": "Paciente Test",
    "dni": "12345678",
    "obra_social": "Obra Social Test"
}
```

#### Obtener Detalle de Paciente
**Solicitud:**
```http
GET /api/pacientes/1/
```

**Respuesta:**
```json
{
    "id": 1,
    "nombre": "Paciente Test",
    "dni": "12345678",
    "obra_social": "Obra Social Test"
}
```

#### Actualizar Paciente
**Solicitud:**
```http
PUT /api/pacientes/1/
Content-Type: application/json

{
    "nombre": "Paciente Editado",
    "dni": "87654321",
    "obra_social": "Obra Social Editada"
}
```

**Respuesta:**
```json
{
    "id": 1,
    "nombre": "Paciente Editado",
    "dni": "87654321",
    "obra_social": "Obra Social Editada"
}
```

#### Eliminar Paciente
**Solicitud:**
```http
DELETE /api/pacientes/1/
```

**Respuesta:**
```http
204 No Content
```

### Médicos

#### Obtener Lista de Médicos
**Solicitud:**
```http
GET /api/medicos/
```

**Respuesta:**
```json
[
    {
        "id": 1,
        "usuario": "Medico Test",
        "nombre": "Medico Test"
    }
]
```

#### Crear Médico
**Solicitud:**
```http
POST /api/medicos/
Content-Type: application/json

{
    "usuario": "Medico Test",
    "nombre": "Medico Test"
}
```

**Respuesta:**
```json
{
    "id": 1,
    "usuario": "Medico Test",
    "nombre": "Medico Test"
}
```

#### Obtener Detalle de Médico
**Solicitud:**
```http
GET /api/medicos/1/
```

**Respuesta:**
```json
{
    "id": 1,
    "usuario": "Medico Test",
    "nombre": "Medico Test"
}
```

#### Actualizar Médico
**Solicitud:**
```http
PUT /api/medicos/1/
Content-Type: application/json

{
    "usuario": "Medico Editado",
    "nombre": "Medico Editado"
}
```

**Respuesta:**
```json
{
    "id": 1,
    "usuario": "Medico Editado",
    "nombre": "Medico Editado"
}
```

#### Eliminar Médico
**Solicitud:**
```http
DELETE /api/medicos/1/
```

**Respuesta:**
```http
204 No Content
```