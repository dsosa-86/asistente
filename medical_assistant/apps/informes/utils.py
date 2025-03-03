from django.template.loader import render_to_string
from django.conf import settings
import os
from weasyprint import HTML, CSS
from datetime import datetime

class GeneradorPDF:
    """
    Clase para generar PDFs de protocolos médicos.
    
    Esta clase utiliza WeasyPrint para convertir HTML+CSS en PDF.
    La estructura está diseñada para ser fácilmente personalizable:
    1. Las plantillas HTML están en templates/informes/
    2. Los estilos CSS están en static/css/informes/
    3. Cada tipo de protocolo puede tener su propia plantilla y estilo
    """

    def __init__(self, protocolo):
        self.protocolo = protocolo
        self.template_path = f"informes/{protocolo.plantilla_pdf}"
        self.style_path = f"css/informes/{protocolo.estilo_pdf}"
        
    def get_context(self):
        """
        Prepara el contexto para la plantilla HTML.
        Personaliza este método para agregar o modificar variables disponibles
        en la plantilla.
        """
        return {
            'protocolo': self.protocolo,
            'informe': self.protocolo.informe,
            'paciente': self.protocolo.informe.paciente,
            'medico': self.protocolo.informe.medico,
            'componentes': self.protocolo.componentes.all(),
            'materiales': self.protocolo.materiales.all(),
            'medicamentos': self.protocolo.medicamentos.all(),
            'firmas': self.protocolo.firmas.all(),
            'fecha_actual': datetime.now(),
            # Agrega aquí más variables según necesites
        }

    def get_header_footer(self):
        """
        Genera el HTML para encabezado y pie de página.
        Personaliza este método para modificar el diseño.
        """
        header = render_to_string('informes/partials/header.html', self.get_context())
        footer = render_to_string('informes/partials/footer.html', self.get_context())
        return header, footer

    def get_css(self):
        """
        Carga y combina los archivos CSS.
        Agrega aquí más archivos CSS según necesites.
        """
        css_files = [
            self.style_path,
            'css/informes/common.css',  # Estilos comunes a todos los protocolos
            'css/informes/print.css',   # Estilos específicos para impresión
        ]
        
        css_paths = [os.path.join(settings.STATIC_ROOT, css) for css in css_files]
        return [CSS(filename=path) for path in css_paths if os.path.exists(path)]

    def generar(self):
        """
        Genera el PDF final combinando todos los elementos.
        Retorna: BytesIO con el contenido del PDF.
        """
        from io import BytesIO
        
        # Renderiza la plantilla principal
        context = self.get_context()
        html_content = render_to_string(self.template_path, context)
        
        # Agrega encabezado y pie de página
        header, footer = self.get_header_footer()
        
        # Combina todo en un HTML final
        html_final = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="UTF-8">
                <!-- Los estilos se cargarán desde get_css() -->
            </head>
            <body>
                {header}
                {html_content}
                {footer}
            </body>
        </html>
        """
        
        # Genera el PDF
        pdf_buffer = BytesIO()
        HTML(string=html_final).write_pdf(
            pdf_buffer,
            stylesheets=self.get_css(),
            presentational_hints=True
        )
        
        return pdf_buffer

# Plantillas predefinidas para diferentes tipos de protocolos
PLANTILLAS_PREDEFINIDAS = {
    'BLOQUEO_FINO': {
        'html': 'bloqueo_fino.html',
        'css': 'bloqueo_fino.css',
        'variables': {
            'tipo_guia': 'TAC',
            'tipo_anestesia': 'neuroleptoanalgesia',
            'materiales_base': [
                'aguja espinal raquídea',
                'iodopovidona',
                'lidocaína',
            ],
            'medicamentos_base': [
                'Bupivacaína',
                'Triamcinolona',
            ],
        }
    },
    'TERMOLESION': {
        'html': 'termolesion.html',
        'css': 'termolesion.css',
        'variables': {
            'tipo_guia': 'TAC',
            'tipo_anestesia': 'neuroleptoanalgesia',
            'materiales_base': [
                'aguja de radiofrecuencia',
                'iodopovidona',
                'lidocaína',
            ],
            'medicamentos_base': [
                'anestésico local',
            ],
            'procedimiento_especifico': {
                'tipo': 'TERMOLESION',
                'subtipo': 'facetaria bilateral',
                'parametros_rf': {
                    'temperatura': '80°C',
                    'tiempo': '90 segundos',
                    'impedancia': 'según protocolo'
                }
            }
        }
    }
} 