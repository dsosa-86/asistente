from typing import Any, Dict, List, Optional
import re
from difflib import SequenceMatcher
from django.core.cache import cache
from .models import ReglaCorreccion

class GestorReglas:
    """Gestor de reglas de corrección"""
    def __init__(self):
        self.reglas = {}
        self.cache_key = 'reglas_correccion'
        self._cargar_reglas()

    def _cargar_reglas(self):
        """Carga las reglas desde la base de datos o caché"""
        reglas_cache = cache.get(self.cache_key)
        
        if not reglas_cache:
            reglas_db = ReglaCorreccion.objects.filter(activa=True).order_by('-confianza')
            reglas_cache = {}
            
            for regla in reglas_db:
                if regla.campo not in reglas_cache:
                    reglas_cache[regla.campo] = []
                reglas_cache[regla.campo].append({
                    'id': regla.id,
                    'tipo': regla.tipo_regla,
                    'patron': regla.patron_original,
                    'correccion': regla.correccion,
                    'funcion': regla.funcion_correccion,
                    'umbral': regla.umbral_similitud,
                    'confianza': regla.confianza
                })
            
            cache.set(self.cache_key, reglas_cache, timeout=3600)  # Cache por 1 hora
        
        self.reglas = reglas_cache

    def aplicar_reglas(self, campo: str, valor: Any) -> tuple[Any, Optional[int]]:
        """Aplica las reglas de corrección a un valor"""
        if not valor or campo not in self.reglas:
            return valor, None

        valor_str = str(valor)
        mejor_correccion = None
        mejor_confianza = 0
        regla_id = None

        for regla in self.reglas[campo]:
            correccion, confianza = self._aplicar_regla(regla, valor_str)
            if correccion and confianza > mejor_confianza:
                mejor_correccion = correccion
                mejor_confianza = confianza
                regla_id = regla['id']

        return mejor_correccion if mejor_correccion else valor, regla_id

    def _aplicar_regla(self, regla: Dict, valor: str) -> tuple[Optional[str], float]:
        """Aplica una regla específica y retorna la corrección y su confianza"""
        try:
            if regla['tipo'] == 'EXACTO':
                if valor.lower() == regla['patron'].lower():
                    return regla['correccion'], 1.0
                return None, 0.0

            elif regla['tipo'] == 'REGEX':
                patron = re.compile(regla['patron'], re.IGNORECASE)
                if patron.match(valor):
                    return patron.sub(regla['correccion'], valor), 1.0
                return None, 0.0

            elif regla['tipo'] == 'SIMILITUD':
                similitud = SequenceMatcher(None, valor.lower(), regla['patron'].lower()).ratio()
                if similitud >= regla['umbral']:
                    return regla['correccion'], similitud
                return None, 0.0

            elif regla['tipo'] == 'FUNCION':
                if regla['funcion']:
                    # Ejecutar función personalizada de forma segura
                    namespace = {}
                    exec(regla['funcion'], namespace)
                    if 'corregir' in namespace:
                        resultado = namespace['corregir'](valor)
                        if isinstance(resultado, tuple):
                            return resultado
                        return resultado, 1.0
                return None, 0.0

        except Exception as e:
            print(f"Error al aplicar regla: {str(e)}")
            return None, 0.0

    def validar_regla(self, regla: ReglaCorreccion) -> List[str]:
        """Valida una regla antes de guardarla"""
        errores = []
        
        # Validar tipo de regla
        if regla.tipo_regla not in ['EXACTO', 'REGEX', 'SIMILITUD', 'FUNCION']:
            errores.append("Tipo de regla inválido")

        # Validar patrón
        if not regla.patron_original:
            errores.append("El patrón es obligatorio")
        elif regla.tipo_regla == 'REGEX':
            try:
                re.compile(regla.patron_original)
            except re.error:
                errores.append("El patrón no es una expresión regular válida")

        # Validar corrección
        if not regla.correccion and regla.tipo_regla != 'FUNCION':
            errores.append("La corrección es obligatoria")

        # Validar función
        if regla.tipo_regla == 'FUNCION':
            if not regla.funcion_correccion:
                errores.append("La función de corrección es obligatoria")
            else:
                try:
                    # Intentar compilar la función
                    compile(regla.funcion_correccion, '<string>', 'exec')
                except SyntaxError:
                    errores.append("La función contiene errores de sintaxis")

        # Validar umbral de similitud
        if regla.tipo_regla == 'SIMILITUD':
            if not (0 <= regla.umbral_similitud <= 1):
                errores.append("El umbral de similitud debe estar entre 0 y 1")

        return errores

    def actualizar_confianza(self, regla_id: int, exitoso: bool):
        """Actualiza la confianza de una regla basado en su uso"""
        try:
            regla = ReglaCorreccion.objects.get(id=regla_id)
            
            # Actualizar contadores
            if exitoso:
                regla.veces_aplicada += 1
            else:
                regla.veces_rechazada += 1
            
            # Calcular nueva confianza
            total_usos = regla.veces_aplicada + regla.veces_rechazada
            if total_usos > 0:
                regla.confianza = regla.veces_aplicada / total_usos
            
            # Desactivar reglas con baja confianza
            if total_usos >= 10 and regla.confianza < 0.3:
                regla.activa = False
            
            regla.save()
            
            # Actualizar caché
            cache.delete(self.cache_key)
            self._cargar_reglas()
            
        except ReglaCorreccion.DoesNotExist:
            pass

class ReglaFactory:
    """Fábrica para crear reglas de corrección"""
    @staticmethod
    def crear_regla_exacta(campo: str, patron: str, correccion: str) -> ReglaCorreccion:
        return ReglaCorreccion(
            campo=campo,
            tipo_regla='EXACTO',
            patron_original=patron,
            correccion=correccion
        )

    @staticmethod
    def crear_regla_regex(campo: str, patron: str, correccion: str) -> ReglaCorreccion:
        return ReglaCorreccion(
            campo=campo,
            tipo_regla='REGEX',
            patron_original=patron,
            correccion=correccion
        )

    @staticmethod
    def crear_regla_similitud(campo: str, patron: str, correccion: str, umbral: float = 0.8) -> ReglaCorreccion:
        return ReglaCorreccion(
            campo=campo,
            tipo_regla='SIMILITUD',
            patron_original=patron,
            correccion=correccion,
            umbral_similitud=umbral
        )

    @staticmethod
    def crear_regla_funcion(campo: str, funcion: str) -> ReglaCorreccion:
        return ReglaCorreccion(
            campo=campo,
            tipo_regla='FUNCION',
            funcion_correccion=funcion
        ) 