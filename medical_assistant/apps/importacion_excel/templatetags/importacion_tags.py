from django import template
from django.template.defaultfilters import floatformat
import json

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtiene un valor de un diccionario usando una clave"""
    if isinstance(dictionary, str):
        try:
            dictionary = json.loads(dictionary)
        except:
            return None
    return dictionary.get(key)

@register.filter
def pprint(value):
    """Formatea un objeto JSON para mejor visualización"""
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except:
            return value
    return json.dumps(value, indent=2, ensure_ascii=False)

@register.filter
def sub(value, arg):
    """Resta dos números"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def porcentaje(value, total):
    """Calcula el porcentaje"""
    try:
        if float(total) == 0:
            return 0
        return floatformat((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0 