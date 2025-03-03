# validator.py app/importacion_excel
from datetime import datetime
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re
from typing import Dict, Any, List, Tuple, Optional
from .models import ReglaCorreccion
from apps.pacientes.models import Paciente
from apps.usuarios.models import Medico
from apps.obras_sociales.models import ObraSocial
from apps.centros_medicos.models import CentroMedico

class ValidadorBase:
    """Clase base para validadores específicos"""
    def __init__(self, modo='ESTRICTO'):
        self.modo = modo
        self.errores = []
        self.advertencias = []

    def validar(self, valor: Any) -> Tuple[bool, Any]:
        """
        Método base de validación
        Retorna: (es_valido, valor_procesado)
        """
        raise NotImplementedError("Debe implementar el método validar")

    def agregar_error(self, mensaje: str):
        self.errores.append(mensaje)

    def agregar_advertencia(self, mensaje: str):
        self.advertencias.append(mensaje)

class ValidadorDNI(ValidadorBase):
    def validar(self, valor: Any) -> Tuple[bool, str]:
        if not valor:
            self.agregar_error("El DNI es obligatorio")
            return False, valor

        # Eliminar caracteres no numéricos
        dni_limpio = re.sub(r'[^0-9]', '', str(valor))
        
        # Validar longitud
        if len(dni_limpio) < 7 or len(dni_limpio) > 8:
            self.agregar_error("El DNI debe tener 7 u 8 dígitos")
            return False, valor

        return True, dni_limpio

class ValidadorFecha(ValidadorBase):
    FORMATOS_FECHA = [
        '%d/%m/%Y',
        '%Y-%m-%d',
        '%d-%m-%Y',
        '%d/%m/%Y %H:%M',
        '%Y-%m-%d %H:%M:%S',
    ]

    def validar(self, valor: Any) -> Tuple[bool, Optional[datetime]]:
        if not valor:
            return True, None

        if isinstance(valor, datetime):
            return True, valor

        valor_str = str(valor).strip()
        for formato in self.FORMATOS_FECHA:
            try:
                fecha = datetime.strptime(valor_str, formato)
                return True, fecha
            except ValueError:
                continue

        self.agregar_error(f"Formato de fecha inválido: {valor}")
        return False, None

class ValidadorEmail(ValidadorBase):
    def validar(self, valor: Any) -> Tuple[bool, str]:
        if not valor:
            return True, ""

        valor_str = str(valor).strip().lower()
        try:
            validate_email(valor_str)
            return True, valor_str
        except ValidationError:
            self.agregar_error(f"Email inválido: {valor}")
            return False, valor

class ValidadorTelefono(ValidadorBase):
    def validar(self, valor: Any) -> Tuple[bool, str]:
        if not valor:
            return True, ""

        # Eliminar caracteres no numéricos excepto '+'
        telefono_limpio = re.sub(r'[^0-9+]', '', str(valor))
        
        # Validar formato
        if not re.match(r'^\+?[0-9]{10,15}$', telefono_limpio):
            self.agregar_error(f"Formato de teléfono inválido: {valor}")
            return False, valor

        return True, telefono_limpio

class ValidadorNombreApellido(ValidadorBase):
    def validar(self, valor: Any) -> Tuple[bool, str]:
        if not valor:
            self.agregar_error("El nombre/apellido es obligatorio")
            return False, valor

        valor_str = str(valor).strip()
        
        # Eliminar múltiples espacios
        valor_limpio = re.sub(r'\s+', ' ', valor_str)
        
        # Capitalizar cada palabra
        valor_capitalizado = ' '.join(word.capitalize() for word in valor_limpio.split())
        
        # Validar longitud
        if len(valor_capitalizado) < 2:
            self.agregar_error("El nombre/apellido es demasiado corto")
            return False, valor

        return True, valor_capitalizado

class ValidadorExcel:
    """Clase principal para validación de datos del Excel"""
    def __init__(self, modo='ESTRICTO'):
        self.modo = modo
        self.validadores = {
            'dni': ValidadorDNI(modo),
            'fecha': ValidadorFecha(modo),
            'email': ValidadorEmail(modo),
            'telefono': ValidadorTelefono(modo),
            'nombre': ValidadorNombreApellido(modo),
            'apellido': ValidadorNombreApellido(modo),
        }
        self.cache = {}
        self._inicializar_cache()
        self.reglas_correccion = self._cargar_reglas_correccion()

    def _inicializar_cache(self):
        """Inicializa el caché de validaciones frecuentes"""
        self.cache = {
            'dnis_existentes': set(Paciente.objects.values_list('dni', flat=True)),
            'medicos': {m.usuario.get_full_name(): m.id for m in Medico.objects.all()},
            'obras_sociales': {os.nombre: os.id for os in ObraSocial.objects.all()},
            'centros_medicos': {cm.nombre: cm.id for cm in CentroMedico.objects.all()},
        }

    def _actualizar_cache(self, campo: str, valor: Any):
        """Actualiza el caché con nuevos valores"""
        if campo == 'dni':
            self.cache['dnis_existentes'].add(valor)

    def obtener_sugerencias(self, campo: str, valor: str, min_similitud: float = 0.7) -> List[str]:
        """Obtiene sugerencias para valores similares en el campo especificado"""
        from difflib import get_close_matches
        
        if campo == 'medico':
            return get_close_matches(valor, self.cache['medicos'].keys(), n=3, cutoff=min_similitud)
        elif campo == 'obra_social':
            return get_close_matches(valor, self.cache['obras_sociales'].keys(), n=3, cutoff=min_similitud)
        elif campo == 'centro_medico':
            return get_close_matches(valor, self.cache['centros_medicos'].keys(), n=3, cutoff=min_similitud)
        
        return []

    def _validar_consistencia(self, registro: Dict[str, Any]) -> List[str]:
        """Valida la consistencia entre campos relacionados"""
        errores = []
        
        # Validar coherencia de fechas
        if 'fecha_nacimiento' in registro and 'fecha_hora_ingreso' in registro:
            if registro['fecha_nacimiento'] and registro['fecha_hora_ingreso']:
                if registro['fecha_nacimiento'] > registro['fecha_hora_ingreso'].date():
                    errores.append("La fecha de nacimiento no puede ser posterior a la fecha de ingreso")

        # Validar relaciones necesarias
        if registro.get('obra_social') and not registro.get('numero_afiliado'):
            errores.append("Si se especifica obra social, el número de afiliado es obligatorio")

        return errores

    def _cargar_reglas_correccion(self) -> Dict[str, List[ReglaCorreccion]]:
        """Carga las reglas de corrección activas agrupadas por campo"""
        reglas = {}
        for regla in ReglaCorreccion.objects.filter(activa=True):
            if regla.campo not in reglas:
                reglas[regla.campo] = []
            reglas[regla.campo].append(regla)
        return reglas

    def validar_registro(self, registro: Dict[str, Any], idx: int, nombre_hoja: str) -> Tuple[Dict[str, Any], List[Dict], List[Dict]]:
        """Valida un registro completo y retorna el registro procesado, errores y advertencias"""
        registro_procesado = {}
        errores = []
        advertencias = []

        try:
            # Procesar campos básicos
            self._procesar_campos_basicos(registro, registro_procesado)
            
            # Validar consistencia entre campos
            errores_consistencia = self._validar_consistencia(registro_procesado)
            if errores_consistencia:
                errores.extend([{
                    'tipo': 'ERROR_CONSISTENCIA',
                    'mensaje': error,
                    'fila': idx,
                    'hoja': nombre_hoja
                } for error in errores_consistencia])

            # Validar relaciones
            self._validar_relaciones(registro, registro_procesado)
            
            # Aplicar reglas de corrección
            self._aplicar_reglas_correccion(registro_procesado)

        except Exception as e:
            errores.append({
                'tipo': 'ERROR_PROCESAMIENTO',
                'mensaje': str(e),
                'fila': idx,
                'hoja': nombre_hoja
            })

        return registro_procesado, errores, advertencias

    def _procesar_campos_basicos(self, registro: Dict[str, Any], registro_procesado: Dict[str, Any]):
        """Procesa y valida los campos básicos del registro"""
        # Validar DNI
        es_valido, dni = self.validadores['dni'].validar(registro.get('DNI', ''))
        if es_valido:
            registro_procesado['dni'] = dni
            if dni in self.cache['dnis_existentes']:
                self.validadores['dni'].agregar_advertencia(f"DNI {dni} ya existe en la base de datos")

        # Validar nombre y apellido
        nombre_completo = registro.get('APELLIDO Y NOMBRE', '')
        partes = nombre_completo.split(',', 1)
        if len(partes) == 2:
            apellido, nombre = partes
        else:
            apellido = nombre_completo
            nombre = ''

        es_valido, apellido = self.validadores['apellido'].validar(apellido)
        if es_valido:
            registro_procesado['apellido'] = apellido

        es_valido, nombre = self.validadores['nombre'].validar(nombre)
        if es_valido:
            registro_procesado['nombre'] = nombre

        # Validar fecha
        fecha_str = registro.get('FECHA', '')
        es_valido, fecha = self.validadores['fecha'].validar(fecha_str)
        if es_valido:
            registro_procesado['fecha_hora_ingreso'] = fecha

        # Procesar campos opcionales
        es_valido, email = self.validadores['email'].validar(registro.get('MAIL', ''))
        if es_valido:
            registro_procesado['email'] = email

        es_valido, telefono = self.validadores['telefono'].validar(registro.get('TELEFONO', ''))
        if es_valido:
            registro_procesado['telefono'] = telefono

        # Procesar otros campos
        registro_procesado.update({
            'sanatorio': registro.get('SANATORIO', '').strip(),
            'procedimiento': registro.get('PROCEDIMIENTO', '').strip(),
            'obra_social': registro.get('OBRA SOC', '').strip(),
            'numero_afiliado': registro.get('N° AFILIADO', '').strip(),
            'medico': registro.get('MEDICO', '').strip(),
            'anti_coagulantes': self._convertir_booleano(registro.get('ANTI C', 'No')),
            'instrumentador': registro.get('INSTRUMENTADOR', '').strip(),
            'anestesia': registro.get('ANESTESIA', 'Local').strip(),
            'autorizacion': self._convertir_booleano(registro.get('AUTORIZACION', 'No')),
            'cx': registro.get('CX', '').strip(),
            'protocolo': registro.get('PROTOCOLO', 'No').strip(),
            'derivado': registro.get('DERIVADO', 'No').strip(),
            'observaciones': registro.get('OBS', '').strip()
        })

    def _validar_relaciones(self, registro: Dict[str, Any], registro_procesado: Dict[str, Any]):
        """Valida las relaciones con otras entidades"""
        # Validar médico
        if registro_procesado.get('medico'):
            medico_id = self.cache['medicos'].get(registro_procesado['medico'])
            if not medico_id:
                sugerencias = self.obtener_sugerencias('medico', registro_procesado['medico'])
                if sugerencias:
                    self.validadores['nombre'].agregar_advertencia(
                        f"Médico no encontrado. ¿Quizás quiso decir: {', '.join(sugerencias)}?"
                    )
                else:
                    self.validadores['nombre'].agregar_error("Médico no encontrado")

        # Validar obra social
        if registro_procesado.get('obra_social'):
            obra_social_id = self.cache['obras_sociales'].get(registro_procesado['obra_social'])
            if not obra_social_id:
                sugerencias = self.obtener_sugerencias('obra_social', registro_procesado['obra_social'])
                if sugerencias:
                    self.validadores['nombre'].agregar_advertencia(
                        f"Obra Social no encontrada. ¿Quizás quiso decir: {', '.join(sugerencias)}?"
                    )
                else:
                    self.validadores['nombre'].agregar_error("Obra Social no encontrada")

        # Validar centro médico
        if registro_procesado.get('sanatorio'):
            centro_id = self.cache['centros_medicos'].get(registro_procesado['sanatorio'])
            if not centro_id:
                sugerencias = self.obtener_sugerencias('centro_medico', registro_procesado['sanatorio'])
                if sugerencias:
                    self.validadores['nombre'].agregar_advertencia(
                        f"Centro Médico no encontrado. ¿Quizás quiso decir: {', '.join(sugerencias)}?"
                    )
                else:
                    self.validadores['nombre'].agregar_error("Centro Médico no encontrado")

    def _aplicar_reglas_correccion(self, registro_procesado: Dict[str, Any]):
        """Aplica las reglas de corrección configuradas"""
        for campo, valor in registro_procesado.items():
            if campo in self.reglas_correccion:
                for regla in self.reglas_correccion[campo]:
                    valor_corregido = regla.aplicar(valor)
                    if valor_corregido != valor:
                        registro_procesado[campo] = valor_corregido
                        self.validadores['nombre'].agregar_advertencia(
                            f"Se aplicó corrección automática en campo {campo}: {valor} -> {valor_corregido}"
                        )

    @staticmethod
    def _convertir_booleano(valor: Any) -> bool:
        """Convierte un valor a booleano"""
        if isinstance(valor, bool):
            return valor
        
        valor_str = str(valor).strip().lower()
        return valor_str in ['si', 'sí', 'yes', 'true', '1', 'verdadero']

# Fin del modulo validators.py