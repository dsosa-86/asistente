# Medical Assistant

## Descripción
Sistema de gestión médica que incluye manejo de pacientes, turnos, consultas, operaciones y más.

## Características Principales

### Gestión de Pacientes
- Dashboard personalizado
- Historia clínica digital
- Seguimiento de estudios
- Turnos y consultas

### Operaciones y Protocolos
- Programación de cirugías
- Estudios prequirúrgicos
- Protocolos quirúrgicos
- Seguimiento postoperatorio

### Importación de Datos
- Carga desde Excel
- Validación automática
- Corrección de errores
- Seguimiento de importaciones

### API REST
- Endpoints para gestión de pacientes
- Manejo de estudios prequirúrgicos
- Estadísticas y reportes
- Documentación completa

## Requisitos
- Python 3.8+
- Django 5.1+
- PostgreSQL 12+
- Dependencias adicionales en requirements/

## Instalación

1. Clonar el repositorio:
```bash
git clone [url-repositorio]
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements/local.txt
```

4. Configurar base de datos:
```bash
python manage.py migrate
```

5. Crear superusuario:
```bash
python manage.py createsuperuser
```

6. Ejecutar servidor:
```bash
python manage.py runserver
```

## Documentación
- [API REST](docs/api_rest.md)
- [Modelos y Relaciones](docs/diagrama_general.md)
- [Importación de Datos](docs/apps/importacion_excel.md)
- [Dashboard de Pacientes](docs/apps/pacientes.md)

## Estructura del Proyecto
```
medical_assistant/
├── apps/
│   ├── pacientes/
│   ├── operaciones/
│   ├── consultas/
│   └── ...
├── docs/
├── requirements/
├── static/
├── templates/
└── manage.py
```

## Contribución
1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## Licencia
[Tipo de Licencia]

## Contacto
[Información de contacto] 