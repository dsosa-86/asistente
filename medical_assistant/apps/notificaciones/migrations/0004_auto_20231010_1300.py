from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('notificaciones', '0003_auto_20231010_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificacion',
            name='estado',
            field=models.CharField(choices=[('PENDIENTE', 'Pendiente de Envío'), ('ENVIADO', 'Enviado'), ('ERROR', 'Error en el Envío'), ('LEIDO', 'Leído por el Usuario')], default='PENDIENTE', max_length=20),
        ),
        migrations.AlterField(
            model_name='notificacion',
            name='prioridad',
            field=models.CharField(choices=[('BAJA', 'Baja'), ('MEDIA', 'Media'), ('ALTA', 'Alta'), ('URGENTE', 'Urgente')], default='MEDIA', max_length=10),
        ),
    ]
