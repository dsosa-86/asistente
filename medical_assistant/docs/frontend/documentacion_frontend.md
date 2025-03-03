# Documentación del Frontend

## Descripción General
Esta documentación cubre la estructura y el uso del frontend del proyecto Asistente Médico.

## Estructura de Archivos

### Vistas
- `landing_page.html`: Página principal del sitio.
- `dashboard_paciente.html`: Dashboard para pacientes.
- `dashboard_administrativo.html`: Dashboard para administrativos.
- `dashboard_medico.html`: Dashboard para médicos.

### Templates Base
- `base.html`: Template base para todas las vistas.
- `dashboard_base.html`: Template base para los dashboards.

### Partials
- `navbar.html`: Barra de navegación.
- `footer.html`: Pie de página.

### Archivos Estáticos
- `styles.css`: Archivo de estilos CSS.
- `main.js`: Archivo JavaScript para la interacción del usuario.

## Vistas y Templates

### Página Principal
```html
{% extends "frontend/base.html" %}

{% block title %}Página Principal{% endblock %}

{% block content %}
<section class="hero">
    <h1>Bienvenido a Nuestra Clínica</h1>
    <p>Ofrecemos los mejores servicios médicos para ti y tu familia.</p>
    <button class="cta">Conoce Más</button>
</section>
<section id="servicios" class="services">
    <!-- Servicios Médicos -->
</section>
<section id="equipo" class="team">
    <!-- Equipo Médico -->
</section>
<section id="instalaciones" class="facilities">
    <!-- Instalaciones -->
</section>
<section id="obras-sociales" class="insurance">
    <!-- Obras Sociales -->
</section>
{% endblock %}
```

### Dashboard Paciente
```html
{% extends "frontend/dashboard_base.html" %}

{% block title %}Dashboard Paciente{% endblock %}

{% block content %}
<div class="card">
    <h2>Próximos Turnos</h2>
    <ul>
        {% for consulta in consultas %}
        <li>{{ consulta.fecha_hora }} - {{ consulta.medico }}</li>
        {% endfor %}
    </ul>
</div>
<div class="card">
    <h2>Historial Clínico</h2>
    <!-- Historial clínico -->
</div>
<div class="card">
    <h2>Estudios</h2>
    <!-- Lista de estudios -->
</div>
<div class="card">
    <h2>Solicitudes</h2>
    <!-- Solicitudes -->
</div>
<div class="card">
    <h2>ChatBot Asistente</h2>
    <!-- ChatBot -->
</div>
{% endblock %}
```

### Dashboard Administrativo
```html
{% extends "frontend/dashboard_base.html" %}

{% block title %}Dashboard Administrativo{% endblock %}

{% block content %}
<div class="card">
    <h2>Gestión de Pacientes</h2>
    <ul>
        {% for paciente in pacientes %}
        <li>{{ paciente.nombre }}</li>
        {% endfor %}
    </ul>
</div>
<div class="card">
    <h2>Agenda</h2>
    <!-- Agenda -->
</div>
<div class="card">
    <h2>Autorizaciones</h2>
    <!-- Autorizaciones -->
</div>
<div class="card">
    <h2>Reportes</h2>
    <!-- Reportes -->
</div>
<div class="card">
    <h2>ChatBot Asistente</h2>
    <!-- ChatBot -->
</div>
{% endblock %}
```

### Dashboard Médico
```html
{% extends "frontend/dashboard_base.html" %}

{% block title %}Dashboard Médico{% endblock %}

{% block content %}
<div class="card">
    <h2>Pacientes</h2>
    <ul>
        {% for consulta in consultas %}
        <li>{{ consulta.paciente }} - {{ consulta.fecha_hora }}</li>
        {% endfor %}
    </ul>
</div>
<div class="card">
    <h2>Agenda Médica</h2>
    <!-- Agenda médica -->
</div>
<div class="card">
    <h2>Quirófano</h2>
    <!-- Gestión de quirófano -->
</div>
<div class="card">
    <h2>Documentación</h2>
    <!-- Documentación médica -->
</div>
<div class="card">
    <h2>ChatBot Asistente</h2>
    <!-- ChatBot -->
</div>
{% endblock %}
```

## Archivos Estáticos

### Estilos CSS
```css
/* filepath: /c:/Users/Tecno/Documents/Proyectos/asistente_medico/asistente/medical_assistant/apps/frontend/static/css/styles.css */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f4f4f4;
}

.main-header, .dashboard-header {
    background-color: #007bff;
    color: white;
    padding: 1rem;
    text-align: center;
}

.main-nav ul {
    list-style: none;
    padding: 0;
}

.main-nav ul li {
    display: inline;
    margin-right: 1rem;
}

.main-nav ul li a {
    color: white;
    text-decoration: none;
}

.auth-buttons {
    display: flex;
    justify-content: flex-end;
}

.auth-buttons button {
    margin-left: 1rem;
    padding: 0.5rem 1rem;
    border: none;
    background-color: #28a745;
    color: white;
    cursor: pointer;
}

.hero {
    text-align: center;
    padding: 2rem;
    background-color: #007bff;
    color: white;
}

.hero .cta {
    padding: 1rem 2rem;
    background-color: #28a745;
    color: white;
    border: none;
    cursor: pointer;
}

.dashboard-content {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-around;
    padding: 2rem;
}

.card {
    background-color: white;
    padding: 1rem;
    margin: 1rem;
    border-radius: 5px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    width: 30%;
}

.card h2 {
    margin-top: 0;
}

.main-footer {
    background-color: #007bff;
    color: white;
    padding: 1rem;
    text-align: center;
}

.main-footer .contact, .main-footer .social-media, .main-footer .map {
    margin-bottom: 1rem;
}
```

### JavaScript
```javascript
// filepath: /c:/Users/Tecno/Documents/Proyectos/asistente_medico/asistente/medical_assistant/apps/frontend/static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    const loginButton = document.querySelector('.login');
    const registerButton = document.querySelector('.register');

    loginButton.addEventListener('click', function() {
        window.location.href = '/login/';
    });

    registerButton.addEventListener('click', function() {
        window.location.href = '/register/';
    });
});
```

## Partials

### Barra de Navegación
```html
<!-- filepath: /c:/Users/Tecno/Documents/Proyectos/asistente_medico/asistente/medical_assistant/apps/frontend/templates/frontend/partials/navbar.html -->
<nav class="main-nav">
    <ul>
        <li><a href="{% url 'landing_page' %}">Inicio</a></li>
        <li><a href="#servicios">Servicios</a></li>
        <li><a href="#equipo">Equipo Médico</a></li>
        <li><a href="#instalaciones">Instalaciones</a></li>
        <li><a href="#obras-sociales">Obras Sociales</a></li>
    </ul>
</nav>
```

### Pie de Página
```html
<!-- filepath: /c:/Users/Tecno/Documents/Proyectos/asistente_medico/asistente/medical_assistant/apps/frontend/templates/frontend/partials/footer.html -->
<footer class="main-footer">
    <div class="contact">
        <h3>Contacto</h3>
        <!-- Información de contacto -->
    </div>
    <div class="social-media">
        <h3>Redes Sociales</h3>
        <!-- Enlaces a redes sociales -->
    </div>
    <div class="map">
        <h3>Ubicación</h3>
        <!-- Mapa de ubicación -->
    </div>
</footer>
```

## Pruebas

### Pruebas de Vistas
```python
# filepath: /c:/Users/Tecno/Documents/Proyectos/asistente_medico/asistente/medical_assistant/apps/frontend/tests.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from apps.pacientes.models import Paciente
from apps.usuarios.models import Medico
from apps.consultas.models import Consulta

class FrontendTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.paciente = Paciente.objects.create(usuario=self.user, nombre='Paciente Test')
        self.medico = Medico.objects.create(usuario=self.user, nombre='Medico Test')
        self.consulta = Consulta.objects.create(paciente=self.paciente, medico=self.medico, fecha_hora='2023-10-10T10:00:00Z')

    def test_landing_page(self):
        response = self.client.get(reverse('landing_page'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_paciente(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('dashboard_paciente'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_administrativo(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('dashboard_administrativo'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_medico(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('dashboard_medico'))
        self.assertEqual(response.status_code, 200)
```
````