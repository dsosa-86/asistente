# Generated by Django 5.1.6 on 2025-03-03 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Consulta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora', models.DateTimeField()),
                ('diagnostico', models.TextField()),
                ('tratamiento', models.TextField()),
            ],
        ),
    ]
