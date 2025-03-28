# Generated by Django 5.1.6 on 2025-03-04 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ComponenteProcedimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(max_length=100)),
                ('descripcion', models.CharField(max_length=200)),
                ('diagnostico', models.CharField(max_length=100)),
                ('orden', models.PositiveSmallIntegerField(default=1)),
            ],
            options={
                'verbose_name': 'Componente de Procedimiento',
                'verbose_name_plural': 'Componentes de Procedimiento',
                'ordering': ['orden'],
            },
        ),
        migrations.CreateModel(
            name='FirmaDigital',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firma_imagen', models.ImageField(upload_to='firmas/')),
                ('certificado_digital', models.FileField(blank=True, null=True, upload_to='certificados/')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('activa', models.BooleanField(default=True)),
                ('pin', models.CharField(help_text='PIN encriptado para validación de firma', max_length=128)),
                ('intentos_fallidos', models.PositiveSmallIntegerField(default=0)),
                ('bloqueada', models.BooleanField(default=False)),
                ('ultima_actividad', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Firma Digital',
                'verbose_name_plural': 'Firmas Digitales',
            },
        ),
        migrations.CreateModel(
            name='FirmaInforme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rol', models.CharField(choices=[('PRINCIPAL', 'Médico Principal'), ('REVISOR', 'Médico Revisor'), ('SUPERVISOR', 'Supervisor')], max_length=20)),
                ('fecha_firma', models.DateTimeField(auto_now_add=True)),
                ('ip_firma', models.GenericIPAddressField(help_text='Dirección IP desde donde se firmó')),
                ('dispositivo', models.CharField(help_text='Información del dispositivo usado para firmar', max_length=200)),
                ('hash_documento', models.CharField(help_text='Hash SHA-256 del contenido firmado', max_length=64)),
            ],
            options={
                'verbose_name': 'Firma de Informe',
                'verbose_name_plural': 'Firmas de Informes',
                'ordering': ['fecha_firma'],
            },
        ),
        migrations.CreateModel(
            name='FirmaProtocolo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rol', models.CharField(choices=[('PRINCIPAL', 'Médico Principal'), ('ANESTESIOLOGO', 'Anestesiólogo'), ('ASISTENTE', 'Médico Asistente'), ('INSTRUMENTADOR', 'Instrumentador')], max_length=20)),
                ('fecha_firma', models.DateTimeField(auto_now_add=True)),
                ('ip_firma', models.GenericIPAddressField(help_text='Dirección IP desde donde se firmó')),
                ('dispositivo', models.CharField(help_text='Información del dispositivo usado para firmar', max_length=200)),
            ],
            options={
                'ordering': ['fecha_firma'],
            },
        ),
        migrations.CreateModel(
            name='Informe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_firma', models.DateTimeField(blank=True, null=True)),
                ('estado', models.CharField(choices=[('BORRADOR', 'Borrador'), ('PENDIENTE_FIRMA', 'Pendiente de Firma'), ('FIRMADO', 'Firmado'), ('ANULADO', 'Anulado')], default='BORRADOR', max_length=20)),
                ('contenido', models.TextField()),
                ('variables_utilizadas', models.JSONField()),
                ('archivo_generado', models.FileField(blank=True, null=True, upload_to='informes/')),
            ],
            options={
                'verbose_name': 'Informe',
                'verbose_name_plural': 'Informes',
                'ordering': ['-fecha_creacion'],
            },
        ),
        migrations.CreateModel(
            name='MaterialProcedimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=8)),
                ('especificaciones', models.CharField(blank=True, help_text='Ej: Calibre 21G, longitud 8.9cm', max_length=100)),
                ('lote', models.CharField(blank=True, max_length=50)),
                ('observaciones', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='MedicamentoProcedimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dosis', models.CharField(max_length=50)),
                ('via_administracion', models.CharField(max_length=50)),
                ('lote', models.CharField(blank=True, max_length=50)),
                ('observaciones', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlantillaInforme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('tipo', models.CharField(choices=[('CONSULTA', 'Informe de Consulta'), ('PROTOCOLO_PRE', 'Protocolo Pre-Quirúrgico'), ('PROTOCOLO_POST', 'Protocolo Post-Quirúrgico'), ('CERTIFICADO', 'Certificado Médico'), ('RECETA', 'Receta Médica'), ('DERIVACION', 'Informe de Derivación')], max_length=20)),
                ('contenido', models.TextField(help_text='Utilice {variables} para campos dinámicos')),
                ('variables', models.JSONField(help_text="Define las variables disponibles en el formato {'nombre': 'descripción'}")),
                ('activa', models.BooleanField(default=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('ultima_modificacion', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Plantilla de Informe',
                'verbose_name_plural': 'Plantillas de Informes',
            },
        ),
        migrations.CreateModel(
            name='ProtocoloProcedimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_procedimiento', models.CharField(choices=[('BLOQUEO_FINO', 'Bloqueo Fino'), ('TERMOLESION', 'Termolesión'), ('INFILTRACION', 'Infiltración Simple')], max_length=20)),
                ('tipo_guia', models.CharField(choices=[('TAC', 'Tomografía Computada'), ('RX', 'Radiografía'), ('ECO', 'Ecografía'), ('RMN', 'Resonancia Magnética')], max_length=20)),
                ('tipo_anestesia', models.CharField(max_length=50)),
                ('tecnica_utilizada', models.TextField()),
                ('materiales_utilizados', models.TextField()),
                ('medicamentos_utilizados', models.TextField()),
                ('complicaciones', models.TextField(blank=True, default='No se presentan complicaciones inherentes al método.')),
                ('estado_paciente', models.CharField(choices=[('BUENO', 'Bueno'), ('REGULAR', 'Regular'), ('INESTABLE', 'Inestable')], max_length=20)),
                ('respuesta_procedimiento', models.CharField(choices=[('FAVORABLE', 'Favorable'), ('PARCIAL', 'Parcial'), ('SIN_CAMBIOS', 'Sin Cambios'), ('DESFAVORABLE', 'Desfavorable')], max_length=20)),
                ('requiere_recuperacion', models.BooleanField(default=True)),
                ('indicaciones_postprocedimiento', models.TextField()),
                ('imagenes_adjuntas', models.BooleanField(default=True, help_text='Indica si se envían registros obtenidos')),
                ('imagenes_pre', models.FileField(blank=True, null=True, upload_to='protocolos/imagenes/pre/')),
                ('imagenes_post', models.FileField(blank=True, null=True, upload_to='protocolos/imagenes/post/')),
                ('plantilla_pdf', models.CharField(default='default_template.html', help_text='Plantilla HTML para generar el PDF', max_length=50)),
                ('estilo_pdf', models.CharField(default='default_style.css', help_text='Hoja de estilos CSS para el PDF', max_length=50)),
            ],
            options={
                'verbose_name': 'Protocolo de Procedimiento',
                'verbose_name_plural': 'Protocolos de Procedimientos',
            },
        ),
        migrations.CreateModel(
            name='SeguimientoPostProcedimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_programada', models.DateTimeField()),
                ('fecha_realizado', models.DateTimeField(blank=True, null=True)),
                ('estado', models.CharField(choices=[('PROGRAMADO', 'Control Programado'), ('REALIZADO', 'Control Realizado'), ('CANCELADO', 'Control Cancelado')], default='PROGRAMADO', max_length=20)),
                ('evolucion', models.TextField(blank=True)),
                ('cumplimiento_indicaciones', models.TextField(blank=True)),
                ('efectos_adversos', models.TextField(blank=True)),
                ('requiere_nuevo_control', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['fecha_programada'],
            },
        ),
        migrations.CreateModel(
            name='VariablePersonalizada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('valor_predeterminado', models.TextField()),
                ('descripcion', models.TextField(blank=True)),
                ('activa', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Variable Personalizada',
                'verbose_name_plural': 'Variables Personalizadas',
            },
        ),
        migrations.CreateModel(
            name='VersionInforme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.TextField()),
                ('variables_utilizadas', models.JSONField()),
                ('archivo_generado', models.FileField(blank=True, null=True, upload_to='informes/versiones/')),
                ('fecha_modificacion', models.DateTimeField(auto_now_add=True)),
                ('motivo_modificacion', models.TextField()),
                ('version', models.PositiveIntegerField()),
            ],
            options={
                'verbose_name': 'Versión de Informe',
                'verbose_name_plural': 'Versiones de Informes',
                'ordering': ['-fecha_modificacion'],
            },
        ),
    ]
