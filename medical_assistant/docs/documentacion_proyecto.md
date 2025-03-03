# Medical Assistant - Documentación del Proyecto

## Descripción General
Sistema de gestión integral para centros médicos, especializado en el seguimiento de procedimientos quirúrgicos y estudios prequirúrgicos.

## Estructura del Proyecto

### Apps Principales

1. **usuarios/**
   - Gestión de usuarios y roles (Médicos, Administrativos, Pacientes)
   - Autenticación y permisos
   - Gestión administrativa de médicos y centros

2. **pacientes/**
   - Gestión de historias clínicas
   - Información personal y médica
   - Seguimiento de estudios y tratamientos
   - Vinculación con obras sociales

3. **operaciones/**
   - Programación de cirugías
   - Estudios prequirúrgicos
   - Protocolos quirúrgicos
   - Equipos médicos

4. **centros_medicos/**
   - Gestión de centros médicos
   - Quirófanos y equipamiento
   - Convenios con obras sociales
   - Horarios y disponibilidad

5. **obras_sociales/**
   - Gestión de obras sociales
   - Planes y coberturas
   - Autorizaciones
   - Facturación

6. **importacion_excel/**
   - Importación de datos históricos
   - Validación y corrección
   - Mapeo de columnas
   - Seguimiento de importaciones

7. **turnos/**
   - Gestión de turnos de pacientes con médicos
   - Estados de turnos (pendiente, confirmado, cancelado)

8. **informes**
   - Plantillas de informes
   - Generación y firma de informes
   - Procedimientos y seguimiento post-procedimiento

9. **consultas/**
   - Registro de consultas
   - Asignación de médico
   - Registro de diagnóstico y tratamiento
   - Seguimiento de consultas

10. **notificaciones**
    - Gestión de notificaciones
    - Configuración de preferencias de notificaciones
    - Envío de notificaciones por correo, SMS y WhatsApp
    - Manejo de reintentos y errores
    - Monitoreo y alertas con Sentry

11. **reportes**
    - Generación y visualización de reportes
    - Almacenamiento de estadísticas
    - Tareas asíncronas para generación de reportes

### Modelos Clave

#### Pacientes
```python
class Paciente(models.Model):
    usuario = OneToOneField(Usuario)
    dni = CharField(unique=True)
    obra_social = ForeignKey(ObraSocial)
    estudios_prequirurgicos = RelatedManager(PrequirurgicoPaciente)
    # ... otros campos

    def validar_dni(value):
        # ...

    def validar_telefono(value):
        # ...

    def calcular_edad(self):
        # ...

    def fecha_nacimiento_formateada(self):
        # ...
```

#### Operaciones
```python
class Operacion(models.Model):
    paciente = ForeignKey(Paciente)
    tipo_cirugia = ForeignKey(TipoCirugia)
    equipo_quirurgico = OneToOneField(EquipoQuirurgico)
    estado = CharField(choices=ESTADOS)
    # ... otros campos

class EstudioPrequirurgico(models.Model):
    nombre = CharField()
    tipo = CharField(choices=TIPOS)
    tipo_cirugia = ForeignKey(TipoCirugia)
    es_obligatorio = BooleanField()
    # ... otros campos
```

#### Importación
```python
class ExcelImport(models.Model):
    archivo = FileField()
    tipo_importacion = CharField(choices=TIPOS)
    estado = CharField(choices=ESTADOS)
    usuario = ForeignKey(Usuario)
    # ... otros campos
```
#### Turnos 
``` Python
class Turno(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    consultorio = models.ForeignKey(Consultorio, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
    ])
```
#### Informes
``` Python
class PlantillaInforme(models.Model):
    # ...

class Informe(models.Model):
    # ...

class VariablePersonalizada(models.Model):
    # ...

class FirmaDigital(models.Model):
    # ...

class VersionInforme(models.Model):
    # ...

class FirmaInforme(models.Model):
    # ...

class ProtocoloProcedimiento(models.Model):
    # ...

class ComponenteProcedimiento(models.Model):
    # ...

class MaterialProcedimiento(models.Model):
    # ...

class MedicamentoProcedimiento(models.Model):
    # ...

class FirmaProtocolo(models.Model):
    # ...

class SeguimientoPostProcedimiento(models.Model):
    # ...
```
#### Consultas
```python
class Consulta(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    diagnostico = models.TextField()
    tratamiento = models.TextField()
```

#### Notificaciones
```python
class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50, choices=TIPOS)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(maxlength=20, choices=ESTADOS, default='PENDIENTE')
    prioridad = models.CharField(maxlength=10, choices=PRIORIDADES, default='MEDIA')
    intentos = models.PositiveSmallIntegerField(default=0)
    error_mensaje = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
```

#### Reportes
```python
class Reporte(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    datos = models.JSONField()

    def __str__(self):
        return self.nombre

class Estadistica(models.Model):
    reporte = models.ForeignKey(Reporte, on_delete=models.CASCADE, related_name='estadisticas')
    nombre = models.CharField(max_length=100)
    valor = models.FloatField()
    fecha = models.DateField()

    def __str__(self):
        return f"{self.nombre} - {self.valor}"
```

## Flujos Principales

### 1. Gestión de Pacientes
1. Registro de paciente
2. Asignación de obra social
3. Programación de estudios
4. Seguimiento de resultados

### 2. Programación Quirúrgica
1. Evaluación inicial
2. Solicitud de estudios prequirúrgicos
3. Validación de requisitos
4. Programación de fecha
5. Asignación de equipo

### 3. Importación de Datos
1. Carga de archivo Excel
2. Validación automática
3. Corrección de errores
4. Confirmación y aplicación
5. Registro de cambios

### 4. Gestión de Turnos
1. Registro de turno
2. Confirmación de turno
3. Cancelación de turno

### 5. Generación de Informes
1. Creación de plantilla de informe
2. Generación de informe
3. Firma digital de informe
4. Seguimiento post-procedimiento

### 6. Gestión de Consultas
1. Registro de consulta
2. Asignación de médico
3. Registro de diagnóstico y tratamiento
4. Seguimiento de consultas

### 7. Generación de Reportes
1. Creación de reporte
2. Generación de estadísticas
3. Visualización de reportes
4. Exportación de datos

## Configuración del Proyecto

### Requisitos
```txt
Django==5.0.2
django-environ==0.11.2
django-filter==23.5
djangorestframework==3.14.0
pandas==2.2.0
XlsxWriter==3.2.2
twilio==7.0.0
sentry-sdk==1.5.0
# ... otros requisitos
```

### Variables de Entorno
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:pass@localhost/dbname
# ... otras variables
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
SENTRY_DSN=your_sentry_dsn
```

## APIs y Endpoints

### Pacientes
- `GET /api/pacientes/`: Lista de pacientes
- `POST /api/pacientes/`: Crear paciente
- `GET /api/pacientes/{id}/estudios/`: Estudios del paciente

### Operaciones
- `GET /api/operaciones/`: Lista de operaciones
- `POST /api/operaciones/programar/`: Programar operación
- `GET /api/estudios/`: Lista de estudios prequirúrgicos

### Importación
- `POST /api/importar/`: Importar archivo Excel
- `GET /api/importar/{id}/estado/`: Estado de importación
- `POST /api/importar/{id}/corregir/`: Corregir datos

### Turnos
- `GET /api/turnos/`: Lista de turnos
- `POST /api/turnos/`: Crear turno
- `GET /api/turnos/{id}/`: Detalle de turno
- `PUT /api/turnos/{id}/`: Actualizar turno
- `DELETE /api/turnos/{id}/`: Eliminar turno

### Informes
- `GET /api/informes/`: Lista de informes
- `POST /api/informes/`: Crear informe
- `GET /api/informes/{id}/`: Detalle de informe
- `PUT /api/informes/{id}/`: Actualizar informe
- `DELETE /api/informes/{id}/`: Eliminar informe

### Consultas
- `GET /api/consultas/`: Lista de consultas
- `POST /api/consultas/`: Crear consulta
- `GET /api/consultas/{id}/`: Detalle de consulta
- `PUT /api/consultas/{id}/`: Actualizar consulta
- `DELETE /api/consultas/{id}/`: Eliminar consulta

### Reportes
- `GET /api/reportes/`: Lista de reportes
- `POST /api/reportes/`: Crear reporte
- `GET /api/reportes/{id}/`: Detalle de reporte
- `PUT /api/reportes/{id}/`: Actualizar reporte
- `DELETE /api/reportes/{id}/`: Eliminar reporte

## Seguridad

### Permisos por Rol
1. **Médicos**
   - Gestionar pacientes propios
   - Programar operaciones
   - Ver historias clínicas

2. **Administrativos**
   - Gestionar turnos
   - Importar datos
   - Gestionar obras sociales

3. **Pacientes**
   - Ver sus estudios
   - Ver sus turnos
   - Actualizar datos personales

### Validaciones
1. **Datos Personales**
   - DNI único
   - Email válido
   - Teléfono con formato

2. **Estudios**
   - Fechas coherentes
   - Archivos permitidos
   - Resultados completos

3. **Importación**
   - Formato Excel válido
   - Datos requeridos
   - Integridad referencial

## Estado Actual del Proyecto

### Completado
- ✅ Modelos base definidos
- ✅ Migraciones iniciales
- ✅ Admin site configurado
- ✅ Importación de datos históricos
- ✅ Gestión de estudios prequirúrgicos

### En Progreso
- 🔄 Interfaz de usuario
    - falta pruebas de usuario y feedback
- 🔄 API REST
    - falta pruebas de usuario y feedback
- 🔄 Sistema de notificaciones
    - notificaciones por mail - implementado falta testeo
    - notificaciones por whatsapp - implementado falta testeo
- 🔄 Reportes y estadísticas
    - falta testeo y feedback

### Pendiente
- ⏳ Tests automatizados
- ⏳ Documentación de API
- ⏳ Deploy a producción
- ⏳ Optimizaciones de rendimiento

## Próximos Pasos
1. Implementar vistas y templates
2. Desarrollar API REST
3. Configurar sistema de notificaciones
4. Implementar tests
5. Preparar para producción

## Contribución
1. Fork del repositorio
2. Crear rama feature/fix
3. Commit con mensaje descriptivo
4. Pull request a develop

## Contacto
- **Desarrollador Principal:** [Nombre]
- **Email:** [Email]
- **GitHub:** [Usuario]