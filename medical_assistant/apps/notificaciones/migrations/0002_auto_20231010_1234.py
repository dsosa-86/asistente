from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('notificaciones', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificacion',
            name='whatsapp_activo',
            field=models.BooleanField(default=False, help_text='Recibir notificaciones por WhatsApp'),
        ),
        migrations.AlterField(
            model_name='notificacion',
            name='tipo',
            field=models.CharField(choices=[('EMAIL', 'Correo Electrónico'), ('SMS', 'Mensaje de Texto'), ('SISTEMA', 'Notificación del Sistema'), ('WHATSAPP', 'Mensaje de WhatsApp')], max_length=50),
        ),
    ]
