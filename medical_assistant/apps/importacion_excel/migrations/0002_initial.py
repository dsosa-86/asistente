# Generated by Django 5.1.6 on 2025-03-03 21:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('importacion_excel', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='correcciondatos',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='correcciones_realizadas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='excelimport',
            name='usuario',
            field=models.ForeignKey(blank=True, help_text='Usuario que realiza la importación', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='correcciondatos',
            name='importacion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='correcciones', to='importacion_excel.excelimport'),
        ),
        migrations.AlterUniqueTogether(
            name='mapeocolumnas',
            unique_together={('nombre_columna_excel', 'campo_modelo')},
        ),
        migrations.AddField(
            model_name='reglacorreccion',
            name='creada_por',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
