from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from apps.importacion_excel.models import ExcelImport
from apps.importacion_excel.tasks import procesar_archivo_excel, enviar_notificacion_exito, enviar_notificacion_error
from unittest.mock import patch
from celery.result import AsyncResult

class TestTareasAsincronas(TestCase):
    def setUp(self):
        User = get_user_model()
        self.usuario = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.excel_content = b"PK\x03\x04\x14\x00\x00\x00\x08\x00"
        self.archivo = SimpleUploadedFile(
            "test.xlsx",
            self.excel_content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        self.importacion = ExcelImport.objects.create(
            archivo=self.archivo,
            tipo_importacion='AGENDA',
            usuario=self.usuario
        )

    @patch('apps.importacion_excel.tasks.procesar_archivo_excel.delay')
    def test_procesamiento_asincrono(self, mock_task):
        # Configurar el mock
        mock_task.return_value = AsyncResult('test-task-id')
        
        # Ejecutar la tarea
        result = procesar_archivo_excel.delay(self.importacion.id)
        
        # Verificar que la tarea fue llamada
        mock_task.assert_called_once_with(self.importacion.id)
        self.assertIsInstance(result, AsyncResult)

    @patch('django.core.mail.send_mail')
    def test_notificacion_exito(self, mock_send_mail):
        # Ejecutar la tarea de notificación
        enviar_notificacion_exito(self.importacion.id)
        
        # Verificar que se envió el email
        self.assertTrue(mock_send_mail.called)
        args = mock_send_mail.call_args[0]
        self.assertIn('exitosa', args[0])  # Verificar que el asunto contiene 'exitosa'

    @patch('django.core.mail.send_mail')
    def test_notificacion_error(self, mock_send_mail):
        # Ejecutar la tarea de notificación de error
        enviar_notificacion_error(self.importacion.id)
        
        # Verificar que se envió el email
        self.assertTrue(mock_send_mail.called)
        args = mock_send_mail.call_args[0]
        self.assertIn('error', args[0])  # Verificar que el asunto contiene 'error'

    def test_reintentos_automaticos(self):
        with patch('apps.importacion_excel.tasks.procesar_archivo_excel.retry') as mock_retry:
            # Forzar una excepción para probar el reintento
            with patch('apps.importacion_excel.models.ExcelImport.objects.get') as mock_get:
                mock_get.side_effect = Exception('Error de prueba')
                
                # Ejecutar la tarea
                procesar_archivo_excel(self.importacion.id)
                
                # Verificar que se intentó reintentar
                self.assertTrue(mock_retry.called)

    def test_limpieza_archivos(self):
        # TODO: Implementar test para limpiar_archivos_temporales
        pass

    def tearDown(self):
        # Limpiar archivos creados durante las pruebas
        self.importacion.archivo.delete() 