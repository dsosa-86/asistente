# Generated by Django 5.1.6 on 2025-03-04 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Enfermero',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('apellido', models.CharField(max_length=100)),
                ('matricula', models.CharField(max_length=20)),
                ('especialidad', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='EquipoQuirurgico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='EstudioPrequirurgico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('tipo', models.CharField(choices=[('LABORATORIO', 'Laboratorio'), ('IMAGEN', 'Imagen'), ('CARDIOLOGIA', 'Cardiología'), ('OTROS', 'Otros')], max_length=20)),
                ('es_obligatorio', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Operacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_programada', models.DateTimeField()),
                ('duracion_estimada', models.DurationField()),
                ('estado', models.CharField(choices=[('PROGRAMADA', 'Programada'), ('EN_CURSO', 'En Curso'), ('FINALIZADA', 'Finalizada'), ('CANCELADA', 'Cancelada')], default='PROGRAMADA', max_length=20)),
                ('fecha_inicio', models.DateTimeField(blank=True, null=True)),
                ('fecha_fin', models.DateTimeField(blank=True, null=True)),
                ('notas_preoperatorias', models.TextField(blank=True)),
                ('complicaciones', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlantillaProtocolo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('contenido', models.TextField()),
                ('variables', models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='PrequirurgicoPaciente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('SOLICITADO', 'Solicitado'), ('REALIZADO', 'Realizado'), ('VENCIDO', 'Vencido'), ('CANCELADO', 'Cancelado')], default='PENDIENTE', max_length=20)),
                ('fecha_solicitud', models.DateTimeField(auto_now_add=True)),
                ('fecha_realizacion', models.DateField(blank=True, null=True)),
                ('resultado', models.TextField(blank=True)),
                ('archivo', models.FileField(blank=True, null=True, upload_to='estudios_prequirurgicos/')),
            ],
        ),
        migrations.CreateModel(
            name='ProcedimientoEspecifico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField()),
                ('pasos', models.JSONField(default=list)),
            ],
        ),
        migrations.CreateModel(
            name='Protocolo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('contenido', models.TextField()),
                ('diagnostico', models.TextField()),
                ('procedimiento', models.TextField()),
                ('observaciones', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='TipoCirugia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True)),
                ('duracion_estimada', models.DurationField()),
                ('requiere_internacion', models.BooleanField(default=False)),
            ],
        ),
    ]
