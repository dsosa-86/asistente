# Generated by Django 5.1.6 on 2025-03-04 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CorreccionDatos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campo', models.CharField(max_length=100)),
                ('valor_original', models.CharField(max_length=200)),
                ('valor_corregido', models.CharField(max_length=200)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('justificacion', models.TextField(blank=True, help_text='Razón de la corrección')),
                ('fila', models.IntegerField(help_text='Número de fila en el Excel')),
                ('hoja', models.CharField(help_text='Nombre de la hoja del Excel', max_length=100)),
            ],
            options={
                'verbose_name': 'Corrección de Datos',
                'verbose_name_plural': 'Correcciones de Datos',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='ExcelImport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archivo', models.FileField(help_text='Archivo Excel (.xlsx, .xls) con los datos a importar', upload_to='excel_imports/')),
                ('tipo_importacion', models.CharField(choices=[('AGENDA', 'Importación de Agenda'), ('HISTORICOS', 'Datos Históricos')], default='HISTORICOS', help_text='Tipo de datos que contiene el archivo', max_length=20)),
                ('estado', models.CharField(choices=[('PENDIENTE', 'Pendiente de Revisión'), ('EN_REVISION', 'En Revisión'), ('CORREGIDO', 'Datos Corregidos'), ('IMPORTADO', 'Importado'), ('ERROR', 'Error en Importación')], default='PENDIENTE', max_length=20)),
                ('fecha_subida', models.DateTimeField(auto_now_add=True)),
                ('fecha_procesamiento', models.DateTimeField(blank=True, null=True)),
                ('registros_totales', models.IntegerField(default=0)),
                ('registros_procesados', models.IntegerField(default=0)),
                ('registros_con_error', models.IntegerField(default=0)),
                ('log_procesamiento', models.JSONField(blank=True, help_text='Registro detallado del proceso de importación', null=True)),
                ('datos_originales', models.JSONField(blank=True, help_text='Datos originales del Excel', null=True)),
                ('datos_corregidos', models.JSONField(blank=True, help_text='Datos después de las correcciones', null=True)),
            ],
            options={
                'verbose_name': 'Importación de Excel',
                'verbose_name_plural': 'Importaciones de Excel',
                'ordering': ['-fecha_subida'],
            },
        ),
        migrations.CreateModel(
            name='MapeoColumnas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_columna_excel', models.CharField(help_text='Nombre de la columna en el archivo Excel', max_length=100)),
                ('campo_modelo', models.CharField(help_text='Nombre del campo en el modelo de Django', max_length=100)),
                ('transformacion', models.CharField(choices=[('NONE', 'Sin transformación'), ('UPPERCASE', 'Convertir a mayúsculas'), ('LOWERCASE', 'Convertir a minúsculas'), ('CAPITALIZE', 'Capitalizar'), ('STRIP', 'Eliminar espacios'), ('CUSTOM', 'Transformación personalizada')], default='NONE', help_text='Tipo de transformación a aplicar', max_length=20)),
                ('funcion_transformacion', models.TextField(blank=True, help_text='Código Python para transformación personalizada', null=True)),
                ('validaciones', models.JSONField(default=list, help_text='Lista de validaciones a aplicar')),
                ('es_requerido', models.BooleanField(default=False, help_text='Indica si el campo es obligatorio')),
                ('valor_defecto', models.CharField(blank=True, help_text='Valor por defecto si el campo está vacío', max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'Mapeo de Columna',
                'verbose_name_plural': 'Mapeo de Columnas',
            },
        ),
        migrations.CreateModel(
            name='ReglaCorreccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campo', models.CharField(max_length=100)),
                ('tipo_regla', models.CharField(choices=[('EXACTO', 'Coincidencia Exacta'), ('REGEX', 'Expresión Regular'), ('SIMILITUD', 'Similitud de Texto'), ('FUNCION', 'Función Personalizada')], default='EXACTO', help_text='Tipo de comparación para aplicar la regla', max_length=20)),
                ('patron_original', models.CharField(help_text='Patrón a identificar (puede ser regex)', max_length=200)),
                ('correccion', models.CharField(help_text='Valor de reemplazo', max_length=200)),
                ('funcion_correccion', models.TextField(blank=True, help_text='Código Python para corrección personalizada', null=True)),
                ('umbral_similitud', models.FloatField(default=0.8, help_text='Umbral de similitud (0-1) para tipo SIMILITUD')),
                ('confianza', models.FloatField(default=0.0, help_text='Nivel de confianza de la regla (0-1)')),
                ('veces_aplicada', models.IntegerField(default=0)),
                ('veces_rechazada', models.IntegerField(default=0, help_text='Número de veces que la corrección fue rechazada')),
                ('activa', models.BooleanField(default=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('ultima_aplicacion', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Regla de Corrección',
                'verbose_name_plural': 'Reglas de Corrección',
                'ordering': ['-confianza', '-veces_aplicada'],
            },
        ),
    ]
