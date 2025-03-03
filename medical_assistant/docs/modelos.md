# Modelos del Proyecto

## Usuarios
```python
class Usuario(AbstractUser):
    rol = models.CharField(max_length=20, choices=ROLES)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=255, blank=True)

class Medico(models.Model):
    tipo = models.CharField(max_length=50)
    especialidad = models.CharField(max_length=100)
    matricula = models.CharField(max_length=50)

class Administrativo(models.Model):
    departamento = models.CharField(max_length=100)

class GestionAdministrativa(models.Model):
    tipo_gestion = models.CharField(max_length=20, choices=[('MEDICO', 'Médico'), ('CENTRO', 'Centro Médico')])
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, null=True, blank=True)
    centro_medico = models.ForeignKey('centros_medicos.CentroMedico', on_delete=models.CASCADE, null=True, blank=True)
    activo = models.BooleanField(default=True)
```

## Pacientes
```python
class Paciente(models.Model):
    dni = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    fecha_hora_ingreso = models.DateTimeField(auto_now_add=True)
    medico = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True, blank=True, related_name='pacientes')
    obra_social = models.ForeignKey(ObraSocial, on_delete=models.SET_NULL, null=True, blank=True, related_name='pacientes')
    sanatorio = models.ForeignKey(CentroMedico, on_delete=models.SET_NULL, null=True, blank=True, related_name='pacientes')
    derivado = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='derivados')
    activo = models.BooleanField(default=True)
```

## Turnos
```python
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

## Operaciones
```python
class Operacion(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, related_name='operaciones')
    tipo_cirugia = models.ForeignKey(TipoCirugia, on_delete=models.PROTECT)
    procedimiento_especifico = models.ForeignKey(ProcedimientoEspecifico, on_delete=models.SET_NULL, null=True, blank=True)
    cirujano_principal = models.ForeignKey(Medico, on_delete=models.PROTECT, related_name='operaciones_como_cirujano')
    anestesiologo = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True, related_name='operaciones_como_anestesiologo')
    instrumentador = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True, related_name='operaciones_como_instrumentador')
    fecha_programada = models.DateTimeField()
    duracion_estimada = models.DurationField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PROGRAMADA')
    centro_medico = models.ForeignKey(CentroMedico, on_delete=models.PROTECT)
    quirofano = models.ForeignKey(Quirofano, on_delete=models.SET_NULL, null=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    notas_preoperatorias = models.TextField(blank=True)
    complicaciones = models.TextField(blank=True)
```

### Etapa 4: Documentación y Migraciones

Actualizar la documentación con los modelos completados.

#### /c:/Users/Tecno/Documents/Proyectos/asistente_medico/asistente/medical_assistant/apps/usuarios/migrations/0002_auto.py

Crear y aplicar migraciones para los modelos de `usuarios`.

<file>
```python
// filepath: /c:/Users/Tecno/Documents/Proyectos/asistente_medico/asistente/medical_assistant/apps/usuarios/migrations/0002_auto.py
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='rol',
            field=models.CharField(max_length=20, choices=[('paciente', 'Paciente'), ('medico', 'Médico'), ('administrativo', 'Administrativo')]),
        ),
        migrations.AddField(
            model_name='usuario',
            name='telefono',
            field=models.CharField(max_length=20, blank=True),
        ),
        migrations.AddField(
            model_name='usuario',
            name='direccion',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='medico',
            name='tipo',
            field=models.CharField(max_length=50),
        ),
        migrations.AddField(
            model_name='medico',
            name='especialidad',
            field=models.CharField(max_length=100),
        ),
        migrations.AddField(
            model_name='medico',
            name='matricula',
            field=models.CharField(max_length=50),
        ),
        migrations.AddField(
            model_name='administrativo',
            name='departamento',
            field=models.CharField(max_length=100),
        ),
        migrations.AddField(
            model_name='gestionadministrativa',
            name='tipo_gestion',
            field=models.CharField(max_length=20, choices=[('MEDICO', 'Médico'), ('CENTRO', 'Centro Médico')]),
        ),
        migrations.AddField(
            model_name='gestionadministrativa',
            name='medico',
            field=models.ForeignKey(on_delete=models.CASCADE, null=True, blank=True, to='usuarios.Medico'),
        ),
        migrations.AddField(
            model_name='gestionadministrativa',
            name='centro_medico',
            field=models.ForeignKey(on_delete=models.CASCADE, null=True, blank=True, to='centros_medicos.CentroMedico'),
        ),
        migrations.AddField(
            model_name='gestionadministrativa',
            name='activo',
            field=models.BooleanField(default=True),
        ),
    ]
```
</file>
