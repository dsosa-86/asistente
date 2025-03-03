# Diagrama General de la Base de Datos

## Descripción
Este diagrama muestra las relaciones principales entre las diferentes apps del sistema, incluyendo el módulo de importación de datos y el dashboard de pacientes.

## Diagrama de Relaciones
```mermaid
erDiagram
    %% Usuarios y Autenticación
    Usuario ||--o| Medico : es
    Usuario ||--o| Administrativo : es
    Usuario ||--o| Paciente : es
    
    %% Pacientes y Consultas
    Paciente ||--o{ Consulta : tiene
    Paciente ||--o{ Operacion : tiene
    Paciente ||--o{ Turno : agenda
    Paciente }o--|| ObraSocial : pertenece_a
    Paciente ||--o{ PrequirurgicoPaciente : requiere
    
    %% Dashboard de Paciente
    Paciente ||--o{ EstadisticaPaciente : genera
    Paciente ||--o{ HistorialMedico : tiene
    Paciente ||--o{ NotificacionPaciente : recibe
    
    %% Médicos y sus relaciones
    Medico ||--o{ Consulta : realiza
    Medico ||--o{ Operacion : realiza
    Medico ||--o{ DisponibilidadMedico : configura
    Medico ||--o{ MedicoCentroMedico : trabaja_en
    
    %% Importación de Datos
    ExcelImport }o--|| Usuario : creado_por
    ExcelImport ||--o{ CorreccionDatos : tiene
    ReglaCorreccion ||--o{ CorreccionDatos : aplica
    MapeoColumnas ||--o{ ExcelImport : configura
    
    %% Centros Médicos
    CentroMedico ||--o{ Consultorio : tiene
    CentroMedico ||--o{ Quirofano : tiene
    CentroMedico ||--o{ ConvenioObraSocial : mantiene
    
    %% Operaciones y Protocolos
    Operacion ||--|| EquipoQuirurgico : tiene
    Operacion ||--|| Protocolo : genera
    Operacion ||--o{ UsoMaterial : utiliza
    Operacion ||--o{ UsoMedicamento : requiere
    Operacion }o--|| TipoCirugia : es_de_tipo
    
    %% Estudios Prequirúrgicos
    EstudioPrequirurgico ||--o{ PrequirurgicoPaciente : asignado_a
    EstudioPrequirurgico }o--|| TipoCirugia : requerido_para
    
    %% Informes y Documentación
    Informe }o--|| Consulta : documenta
    Informe }o--|| Operacion : documenta
    Informe ||--o{ VersionInforme : tiene
    Informe ||--o{ FirmaInforme : requiere
    
    %% Obras Sociales y Coberturas
    ObraSocial ||--o{ Plan : ofrece
    Plan ||--o{ Cobertura : define
    Cobertura ||--o{ Autorizacion : genera
    
    %% Insumos Médicos
    MaterialQuirurgico ||--o{ UsoMaterial : usado_en
    MedicamentoQuirurgico ||--o{ UsoMedicamento : usado_en
    
    %% Turnos y Agenda
    Turno }o--|| DisponibilidadMedico : asignado_a
    Turno }o--|| Consultorio : ubicado_en
```

## Notas sobre el Diagrama

### Módulos Principales
1. **Usuarios y Roles**
   - Usuario como base para Médicos, Administrativos y Pacientes
   - Gestión de permisos y accesos

2. **Gestión de Pacientes**
   - Dashboard personalizado
   - Historias clínicas
   - Consultas y operaciones
   - Turnos y seguimiento
   - Estudios prequirúrgicos

3. **Dashboard de Paciente**
   - Estadísticas personalizadas
   - Historial médico
   - Notificaciones
   - Seguimiento de estudios

4. **Operaciones y Protocolos**
   - Equipos quirúrgicos
   - Materiales y medicamentos
   - Documentación y seguimiento
   - Estudios prequirúrgicos requeridos

5. **Importación de Datos**
   - Importación desde Excel
   - Validación y corrección
   - Mapeo de columnas
   - Reglas de transformación

6. **Centros Médicos**
   - Consultorios y quirófanos
   - Convenios con obras sociales
   - Disponibilidad de recursos

7. **Documentación**
   - Informes médicos
   - Versiones y firmas digitales
   - Protocolos y plantillas

### Relaciones Clave
1. **Paciente-Dashboard**
   - Estadísticas personalizadas
   - Historial médico
   - Notificaciones

2. **Paciente-Estudios**
   - Estudios prequirúrgicos
   - Estado de los estudios
   - Seguimiento de resultados

3. **Operación-Estudios**
   - Requisitos por tipo de cirugía
   - Validación de estudios completos
   - Control de vencimientos 