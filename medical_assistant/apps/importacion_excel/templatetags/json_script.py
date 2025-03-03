# Archivo: importacion_excel/templatetags/json_script.py

from django import template
import json
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def json_script(value, element_id):
    """
    Devuelve un bloque <script> con type="application/json" que contiene
    la representación JSON del valor recibido.

    Uso en la plantilla:
      {% load json_script %}
      {% json_script datos "datos_json" %}
    """
    try:
        json_value = json.dumps(value)
    except TypeError:
        json_value = 'null'
    html = f'<script id="{element_id}" type="application/json">{json_value}</script>'
    return mark_safe(html)