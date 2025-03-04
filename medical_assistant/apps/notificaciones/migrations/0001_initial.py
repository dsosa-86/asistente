# Generated by Django 5.1.6 on 2025-03-04 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConfiguracionNotificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_activo', models.BooleanField(default=True, help_text='Recibir notificaciones por correo')),
                ('sms_activo', models.BooleanField(default=False, help_text='Recibir notificaciones por SMS')),
                ('sistema_activo', models.BooleanField(default=True, help_text='Recibir notificaciones en el sistema')),
                ('whatsapp_activo', models.BooleanField(default=False, help_text='Recibir notificaciones por WhatsApp')),
                ('horario_inicio', models.TimeField(default='08:00', help_text='Hora de inicio para recibir notificaciones')),
                ('horario_fin', models.TimeField(default='20:00', help_text='Hora de fin para recibir notificaciones')),
                ('dias_habiles', models.BooleanField(default=True, help_text='Solo recibir notificaciones en días hábiles')),
            ],
            options={
                'verbose_name': 'Configuración de Notificaciones',
                'verbose_name_plural': 'Configuraciones de Notificaciones',
            },
        ),
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('EMAIL', 'Correo Electrónico'), ('SMS', 'Mensaje de Texto'), ('SISTEMA', 'Notificación del Sistema'), ('WHATSAPP', 'Mensaje de WhatsApp')], max_length=50)),
                ('mensaje', models.TextField()),
                ('leida', models.BooleanField(default=False)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_envio', models.DateTimeField(blank=True, null=True)),
                ('fecha_lectura', models.DateTimeField(blank=True, null=True)),
                ('estado', models.CharField(choices=[('PENDIENTE', 'Pendiente de Envío'), ('ENVIADO', 'Enviado'), ('ERROR', 'Error en el Envío'), ('LEIDO', 'Leído por el Usuario')], default='PENDIENTE', max_length=20)),
                ('prioridad', models.CharField(choices=[('BAJA', 'Baja'), ('MEDIA', 'Media'), ('ALTA', 'Alta'), ('URGENTE', 'Urgente')], default='MEDIA', max_length=10)),
                ('intentos', models.PositiveSmallIntegerField(default=0)),
                ('error_mensaje', models.TextField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
            ],
            options={
                'verbose_name': 'Notificación',
                'verbose_name_plural': 'Notificaciones',
                'ordering': ['-fecha_creacion'],
            },
        ),
        migrations.CreateModel(
            name='PlantillaNotificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('tipo', models.CharField(choices=[('EMAIL', 'Correo Electrónico'), ('SMS', 'Mensaje de Texto'), ('SISTEMA', 'Notificación del Sistema'), ('WHATSAPP', 'Mensaje de WhatsApp')], max_length=10)),
                ('asunto', models.CharField(max_length=200)),
                ('contenido', models.TextField(help_text='Usa {{variable}} para campos dinámicos')),
                ('variables', models.JSONField(help_text="Define las variables disponibles en formato {'nombre': 'descripción'}")),
                ('activa', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Plantilla de Notificación',
                'verbose_name_plural': 'Plantillas de Notificaciones',
            },
        ),
    ]
