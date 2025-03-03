# Generated by Django 5.1.6 on 2025-02-26 02:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CentroMedico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('direccion', models.CharField(max_length=200)),
                ('telefono', models.CharField(max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('activo', models.BooleanField(default=True)),
                ('horario_apertura', models.TimeField()),
                ('horario_cierre', models.TimeField()),
            ],
            options={
                'verbose_name': 'Centro Médico',
                'verbose_name_plural': 'Centros Médicos',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='DisponibilidadQuirofano',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia_semana', models.CharField(choices=[('Lunes', 'Lunes'), ('Martes', 'Martes'), ('Miércoles', 'Miércoles'), ('Jueves', 'Jueves'), ('Viernes', 'Viernes'), ('Sábado', 'Sábado'), ('Domingo', 'Domingo')], max_length=10)),
                ('hora_inicio', models.TimeField()),
                ('hora_fin', models.TimeField()),
            ],
            options={
                'verbose_name': 'Disponibilidad de Quirófano',
                'verbose_name_plural': 'Disponibilidades de Quirófano',
            },
        ),
        migrations.CreateModel(
            name='EquipamientoAlquilado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('proveedor', models.CharField(max_length=100)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('costo_diario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('numero_contrato', models.CharField(max_length=50)),
                ('observaciones', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Equipamiento Alquilado',
                'verbose_name_plural': 'Equipamientos Alquilados',
            },
        ),
        migrations.CreateModel(
            name='EquipamientoQuirofano',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('numero_serie', models.CharField(max_length=50, unique=True)),
                ('fecha_instalacion', models.DateField()),
                ('fecha_ultimo_mantenimiento', models.DateField()),
                ('fecha_proximo_mantenimiento', models.DateField()),
                ('activo', models.BooleanField(default=True)),
                ('observaciones', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Equipamiento de Quirófano',
                'verbose_name_plural': 'Equipamientos de Quirófano',
            },
        ),
        migrations.CreateModel(
            name='HorarioAtencion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia_semana', models.CharField(choices=[('Lunes', 'Lunes'), ('Martes', 'Martes'), ('Miércoles', 'Miércoles'), ('Jueves', 'Jueves'), ('Viernes', 'Viernes'), ('Sábado', 'Sábado'), ('Domingo', 'Domingo')], max_length=10)),
                ('hora_inicio', models.TimeField()),
                ('hora_fin', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='MedicoCentroMedico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activo', models.BooleanField(default=True)),
                ('fecha_inicio', models.DateField(auto_now_add=True)),
                ('fecha_fin', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Relación Médico-Centro Médico',
                'verbose_name_plural': 'Relaciones Médico-Centro Médico',
            },
        ),
        migrations.CreateModel(
            name='Quirofano',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('tipo', models.CharField(choices=[('GENERAL', 'Quirófano General'), ('ESPECIALIZADO', 'Quirófano Especializado'), ('AMBULATORIO', 'Quirófano Ambulatorio')], max_length=20)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('piso', models.CharField(max_length=10)),
                ('superficie', models.DecimalField(decimal_places=2, help_text='Superficie en metros cuadrados', max_digits=6)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Quirófano',
                'verbose_name_plural': 'Quirófanos',
                'ordering': ['centro_medico', 'nombre'],
            },
        ),
        migrations.CreateModel(
            name='Consultorio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=10)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('piso', models.CharField(blank=True, max_length=10, null=True)),
                ('capacidad', models.IntegerField(default=1)),
                ('activo', models.BooleanField(default=True)),
                ('centro_medico', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consultorios', to='centros_medicos.centromedico')),
            ],
            options={
                'ordering': ['centro_medico', 'numero'],
            },
        ),
        migrations.CreateModel(
            name='ConvenioObraSocial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_prestador', models.CharField(max_length=50)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField(blank=True, null=True)),
                ('activo', models.BooleanField(default=True)),
                ('centro_medico', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='centros_medicos.centromedico')),
            ],
            options={
                'verbose_name': 'Convenio con Obra Social',
                'verbose_name_plural': 'Convenios con Obras Sociales',
            },
        ),
    ]
