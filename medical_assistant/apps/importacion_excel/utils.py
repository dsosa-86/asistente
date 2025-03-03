# utils.py app/importacion_excel
import pandas as pd
from typing import Dict, List, Any, Tuple
from django.db import transaction
from django.utils import timezone
from django.forms import ValidationError
from .validators import ValidadorExcel
from .models import ExcelImport, CorreccionDatos
from apps.pacientes.models import Paciente
from apps.usuarios.models import Usuario, Medico
from apps.obras_sociales.models import ObraSocial
from apps.centros_medicos.models import CentroMedico

class ProcesadorExcel:
    """Clase principal para procesar archivos Excel"""
    
    def __init__(self, import_id: int, modo: str = 'ESTRICTO'):
        self.importacion = ExcelImport.objects.get(id=import_id)
        self.validator = ValidadorExcel(modo)
        self.errores = []
        self.advertencias = []
        self.registros_procesados = []

    def procesar_archivo(self) -> bool:
        """
        Procesa el archivo Excel completo
        Retorna: True si el proceso fue exitoso
        """
        try:
            self.importacion.iniciar_procesamiento()
            
            # Leer el archivo Excel
            df_dict = pd.read_excel(
                self.importacion.archivo.path,
                sheet_name=None,  # Lee todas las hojas
                engine='openpyxl'
            )
            
            # Guardar datos originales
            self.importacion.datos_originales = {
                nombre: df.to_dict('records')
                for nombre, df in df_dict.items()
            }
            self.importacion.save()

            # Procesar cada hoja
            for nombre_hoja, df in df_dict.items():
                self._procesar_hoja(nombre_hoja, df)

            # Actualizar estadísticas
            self.importacion.actualizar_estadisticas()
            
            # Finalizar procesamiento
            exitoso = len(self.errores) == 0
            self.importacion.finalizar_procesamiento(exitoso)
            
            return exitoso

        except Exception as e:
            self.errores.append({
                'tipo': 'ERROR_CRITICO',
                'mensaje': f'Error al procesar el archivo: {str(e)}'
            })
            self.importacion.finalizar_procesamiento(False)
            return False

    def _procesar_hoja(self, nombre_hoja: str, df: pd.DataFrame):
        """Procesa una hoja individual del Excel"""
        for idx, row in df.iterrows():
            registro = row.to_dict()
            
            # Validar registro
            registro_procesado, errores, advertencias = self.validator.validar_registro(
                registro, idx + 2, nombre_hoja  # +2 para compensar el encabezado y el índice base-0
            )
            
            self.errores.extend(errores)
            self.advertencias.extend(advertencias)
            
            if not errores:  # Solo procesar si no hay errores críticos
                self.registros_procesados.append({
                    'hoja': nombre_hoja,
                    'fila': idx + 2,
                    'datos': registro_procesado
                })

    @transaction.atomic
    def guardar_datos(self) -> bool:
        """
        Guarda los datos procesados en la base de datos
        Retorna: True si el guardado fue exitoso
        """
        try:
            for registro in self.registros_procesados:
                self._guardar_registro(registro['datos'])
            return True
        except Exception as e:
            self.errores.append({
                'tipo': 'ERROR_GUARDADO',
                'mensaje': f'Error al guardar los datos: {str(e)}'
            })
            return False

    def _guardar_registro(self, datos: Dict[str, Any]):
        """Guarda un registro individual en la base de datos"""
        # Crear o actualizar paciente
        paciente = self._crear_actualizar_paciente(datos)
        
        # Crear o actualizar relaciones
        self._crear_actualizar_relaciones(paciente, datos)

    def _crear_actualizar_paciente(self, datos: Dict[str, Any]) -> Paciente:
        """Crea o actualiza un paciente con los datos proporcionados"""
        # Buscar paciente existente por DNI
        paciente = Paciente.objects.filter(dni=datos['dni']).first()
        
        if not paciente:
            # Crear usuario para el paciente
            usuario = Usuario.objects.create_user(
                username=datos['dni'],
                email=datos.get('email', ''),
                password=Usuario.objects.make_random_password(),
                first_name=datos['nombre'],
                last_name=datos['apellido'],
                rol='paciente'
            )
            
            # Crear nuevo paciente
            paciente = Paciente.objects.create(
                usuario=usuario,
                dni=datos['dni'],
                nombre=datos['nombre'],
                apellido=datos['apellido'],
                fecha_nacimiento=datos.get('fecha_nacimiento'),
                telefono=datos.get('telefono', ''),
                email=datos.get('email', '')
            )
        else:
            # Actualizar datos existentes
            paciente.nombre = datos['nombre']
            paciente.apellido = datos['apellido']
            if datos.get('telefono'):
                paciente.telefono = datos['telefono']
            if datos.get('email'):
                paciente.email = datos['email']
            paciente.save()
            
            # Actualizar usuario asociado
            usuario = paciente.usuario
            usuario.first_name = datos['nombre']
            usuario.last_name = datos['apellido']
            if datos.get('email'):
                usuario.email = datos['email']
            usuario.save()

        return paciente

    def _crear_actualizar_relaciones(self, paciente: Paciente, datos: Dict[str, Any]):
        """Crea o actualiza las relaciones del paciente"""
        # Asignar obra social
        if datos.get('obra_social'):
            obra_social = ObraSocial.objects.filter(
                nombre__iexact=datos['obra_social']
            ).first()
            if obra_social:
                paciente.obra_social = obra_social
                paciente.numero_afiliacion = datos.get('numero_afiliado', '')

        # Asignar médico
        if datos.get('medico'):
            medico = Medico.objects.filter(
                usuario__last_name__iexact=datos['medico']
            ).first()
            if medico:
                paciente.medico = medico

        # Asignar sanatorio
        if datos.get('sanatorio'):
            centro = CentroMedico.objects.filter(
                nombre__iexact=datos['sanatorio']
            ).first()
            if centro:
                paciente.sanatorio = centro

        paciente.save()

    def generar_reporte(self) -> Dict[str, Any]:
        """Genera un reporte del proceso de importación"""
        return {
            'total_registros': len(self.registros_procesados),
            'errores': self.errores,
            'advertencias': self.advertencias,
            'estado': self.importacion.estado,
            'fecha_proceso': self.importacion.fecha_procesamiento,
            'estadisticas': {
                'registros_totales': self.importacion.registros_totales,
                'registros_procesados': self.importacion.registros_procesados,
                'registros_con_error': self.importacion.registros_con_error
            }
        }

class ExcelProcessor:
    def __init__(self):
        self.validator = ValidadorExcel()

    def procesar_registro(self, registro, idx, nombre_hoja):
        """Procesa y valida un registro individual del Excel."""
        errores = []
        advertencias = []
        registro_procesado = {}
        
        try:
            # Procesar datos básicos
            apellido, nombre = self.validator.separar_nombre_apellido(
                registro.get('APELLIDO Y NOMBRE', '')
            )
            
            registro_procesado.update({
                'nombre': nombre,
                'apellido': apellido,
                'dni': self.validator.validar_dni(registro.get('DNI', '')),
                'fecha_nacimiento': self.validator.normalizar_fecha(registro.get('NACIMIENTO', '')),
                'email': self.validator.validar_email(registro.get('MAIL', '')),
                'fecha_hora_ingreso': self.validator.normalizar_fecha(registro.get('FECHA', '')),
                'sanatorio': registro.get('SANATORIO', '').strip(),
                'procedimiento': registro.get('PROCEDIMIENTO', '').strip(),
                'medico': self.validator.normalizar_medico(registro.get('MEDICO', '')),
                'anti_coagulantes': self.validator.convertir_booleano(registro.get('ANTI C', 'No')),
                'instrumentador': registro.get('INSTRUMENTADOR', 'No').strip(),
                'anestesia': registro.get('ANESTESIA', 'Local').strip(),
                'autorizacion': self.validator.convertir_booleano(registro.get('AUTORIZACION', 'No')),
                'cx': registro.get('CX', '').strip(),
                'protocolo': registro.get('PROTOCOLO', 'No').strip(),
                'derivado': registro.get('DERIVADO', 'No').strip(),
                'observaciones': registro.get('OBS', 'Sin observaciones').strip(),
                'afiliacion': registro.get('OBRA SOC', '').strip(),
                'numero_afiliacion': registro.get('N° AFILIADO', '').strip()
            })

            # Validaciones adicionales
            self._validar_campos_requeridos(registro_procesado, errores, idx, nombre_hoja)
            self._validar_duplicados(registro_procesado, advertencias, idx, nombre_hoja)

        except ValidationError as e:
            errores.append({
                'fila': idx,
                'hoja': nombre_hoja,
                'mensaje': str(e)
            })
        except Exception as e:
            errores.append({
                'fila': idx,
                'hoja': nombre_hoja,
                'mensaje': f'Error inesperado: {str(e)}'
            })

        return registro_procesado, errores, advertencias

    def _validar_campos_requeridos(self, registro, errores, idx, nombre_hoja):
        """Valida los campos obligatorios."""
        campos_requeridos = ['procedimiento', 'dni', 'fecha_hora_ingreso']
        for campo in campos_requeridos:
            if not registro.get(campo):
                errores.append({
                    'fila': idx,
                    'hoja': nombre_hoja,
                    'campo': campo,
                    'mensaje': f'El campo {campo} es requerido'
                })

    def _validar_duplicados(self, registro, advertencias, idx, nombre_hoja):
        """Valida duplicados en la base de datos."""
        if Paciente.objects.filter(dni=registro['dni']).exists():
            advertencias.append({
                'fila': idx,
                'hoja': nombre_hoja,
                'campo': 'DNI',
                'mensaje': f'Ya existe un paciente con el DNI {registro["dni"]}'
            })

# fin modulo utils.py