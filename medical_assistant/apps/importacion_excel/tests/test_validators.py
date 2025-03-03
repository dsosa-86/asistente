from django.test import TestCase
from django.core.exceptions import ValidationError
from ..validators import ValidadorExcel, validar_archivo_excel
from django.core.files.uploadedfile import SimpleUploadedFile
import pandas as pd
import io

class TestValidadores(TestCase):
    def setUp(self):
        self.validador = ValidadorExcel(modo='ESTRICTO')
        self.excel_content = b"PK\x03\x04\x14\x00\x00\x00\x08\x00"  # Contenido mínimo Excel
        self.archivo_valido = SimpleUploadedFile(
            "test.xlsx",
            self.excel_content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    def test_validar_archivo_excel(self):
        # Test archivo válido
        try:
            validar_archivo_excel(self.archivo_valido)
        except ValidationError:
            self.fail("validar_archivo_excel levantó ValidationError inesperadamente")

        # Test archivo inválido
        archivo_invalido = SimpleUploadedFile("test.txt", b"contenido", content_type="text/plain")
        with self.assertRaises(ValidationError):
            validar_archivo_excel(archivo_invalido)

    def test_validar_estructura_excel(self):
        # Crear DataFrame de prueba
        df = pd.DataFrame({
            'dni': ['12345678'],
            'nombre': ['Test'],
            'apellido': ['Usuario'],
            'fecha_nacimiento': ['2000-01-01']
        })
        
        # Test estructura válida
        resultado = self.validador.validar_registro(df.iloc[0].to_dict(), 0, 'Sheet1')
        self.assertIsNotNone(resultado)

        # Test estructura inválida
        df_invalido = pd.DataFrame({'columna_invalida': ['valor']})
        with self.assertRaises(ValidationError):
            self.validador.validar_registro(df_invalido.iloc[0].to_dict(), 0, 'Sheet1')

    def test_validar_tipos_datos(self):
        # Test DNI válido
        registro = {'dni': '12345678', 'nombre': 'Test', 'apellido': 'Usuario'}
        resultado = self.validador.validar_registro(registro, 0, 'Sheet1')
        self.assertEqual(resultado.get('dni'), '12345678')

        # Test DNI inválido
        registro_invalido = {'dni': 'abc12345', 'nombre': 'Test', 'apellido': 'Usuario'}
        with self.assertRaises(ValidationError):
            self.validador.validar_registro(registro_invalido, 0, 'Sheet1')

    def test_validar_duplicados(self):
        # Implementar test de duplicados
        pass  # TODO: Implementar cuando tengamos la funcionalidad de duplicados

    def test_modo_estricto_vs_flexible(self):
        validador_flexible = ValidadorExcel(modo='FLEXIBLE')
        registro_incompleto = {'dni': '12345678'}  # Falta nombre y apellido

        # En modo estricto debería fallar
        with self.assertRaises(ValidationError):
            self.validador.validar_registro(registro_incompleto, 0, 'Sheet1')

        # En modo flexible debería pasar
        try:
            validador_flexible.validar_registro(registro_incompleto, 0, 'Sheet1')
        except ValidationError:
            self.fail("Modo flexible no debería levantar ValidationError") 