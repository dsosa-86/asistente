from django.template.loader import render_to_string
from django.conf import settings
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from datetime import datetime
from django.http import HttpResponse

class GeneradorPDF:
    """
    Clase para generar PDFs de protocolos médicos.
    
    Esta clase utiliza ReportLab para generar PDFs.
    La estructura está diseñada para ser fácilmente personalizable:
    1. Las plantillas HTML están en templates/informes/
    2. Los estilos CSS están en static/css/informes/
    3. Cada tipo de protocolo puede tener su propia plantilla y estilo
    """

    def __init__(self, informe):
        self.informe = informe

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

    def generar(self):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="informe_{self.informe.id}.pdf"'

        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Título del documento
        elements.append(Paragraph(f"Informe: {self.informe.titulo}", styles['Title']))

        # Tabla de contenido
        data = [
            ['Campo', 'Valor'],
            ['Paciente', self.informe.paciente.nombre],
            ['Fecha', self.informe.fecha.strftime('%d/%m/%Y')],
            # Agregar más campos según sea necesario
        ]
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)

        # Generar el PDF
        doc.build(elements)
        return response

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