# Generated by Django 5.1.6 on 2025-02-25 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExcelImport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archivo', models.FileField(upload_to='excel_imports/')),
                ('fecha_subida', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
