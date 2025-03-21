# Generated by Django 5.1.6 on 2025-03-04 18:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('centros_medicos', '0002_initial'),
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicocentromedico',
            name='medico',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='centros_medicos', to='usuarios.medico'),
        ),
        migrations.AddField(
            model_name='quirofano',
            name='centro_medico',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quirofanos', to='centros_medicos.centromedico'),
        ),
        migrations.AddField(
            model_name='quirofano',
            name='equipamiento_fijo',
            field=models.ManyToManyField(blank=True, to='centros_medicos.equipamientoquirofano'),
        ),
        migrations.AddField(
            model_name='equipamientoalquilado',
            name='quirofano',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='equipamiento_alquilado', to='centros_medicos.quirofano'),
        ),
        migrations.AddField(
            model_name='disponibilidadquirofano',
            name='quirofano',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='disponibilidades', to='centros_medicos.quirofano'),
        ),
        migrations.AlterUniqueTogether(
            name='consultorio',
            unique_together={('centro_medico', 'numero')},
        ),
        migrations.AlterUniqueTogether(
            name='convenioobrasocial',
            unique_together={('centro_medico', 'obra_social')},
        ),
        migrations.AlterUniqueTogether(
            name='medicocentromedico',
            unique_together={('medico', 'centro_medico')},
        ),
    ]
