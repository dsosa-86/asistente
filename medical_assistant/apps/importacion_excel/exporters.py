import csv
import json
from datetime import datetime
from io import BytesIO, StringIO
import xlsxwriter
from django.http import HttpResponse
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from .models import ExcelImport, CorreccionDatos

class BaseExporter:
    """Clase base para exportadores"""
    def __init__(self, importacion_id):
        self.importacion = ExcelImport.objects.get(id=importacion_id)
        self.correcciones = CorreccionDatos.objects.filter(importacion_id=importacion_id)

    def get_data(self):
        """Obtiene los datos para exportar"""
        datos = {
            'informacion_general': {
                'id': self.importacion.id,
                'fecha_subida': self.importacion.fecha_subida,
                'usuario': self.importacion.usuario.get_full_name(),
                'tipo_importacion': self.importacion.get_tipo_importacion_display(),
                'estado': self.importacion.get_estado_display()
            },
            'estadisticas': {
                'registros_totales': self.importacion.registros_totales,
                'registros_procesados': self.importacion.registros_procesados,
                'registros_con_error': self.importacion.registros_con_error,
                'porcentaje_exito': round((self.importacion.registros_procesados / self.importacion.registros_totales * 100), 2) if self.importacion.registros_totales > 0 else 0
            },
            'correcciones': [
                {
                    'campo': c.campo,
                    'valor_original': c.valor_original,
                    'valor_corregido': c.valor_corregido,
                    'usuario': c.usuario.get_full_name(),
                    'fecha': c.fecha,
                    'justificacion': c.justificacion
                } for c in self.correcciones
            ],
            'log_procesamiento': self.importacion.log_procesamiento or {}
        }
        return datos

class ExcelExporter(BaseExporter):
    """Exportador a formato Excel"""
    def export(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        
        # Formatos
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4F81BD',
            'font_color': 'white',
            'border': 1
        })
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy hh:mm'})
        
        # Hoja de Información General
        self._add_general_info_sheet(workbook, header_format, date_format)
        
        # Hoja de Estadísticas
        self._add_statistics_sheet(workbook, header_format)
        
        # Hoja de Correcciones
        self._add_corrections_sheet(workbook, header_format, date_format)
        
        # Hoja de Log
        self._add_log_sheet(workbook, header_format)
        
        workbook.close()
        output.seek(0)
        return output

    def _add_general_info_sheet(self, workbook, header_format, date_format):
        worksheet = workbook.add_worksheet('Información General')
        data = self.get_data()['informacion_general']
        
        headers = ['Campo', 'Valor']
        rows = [
            ['ID', data['id']],
            ['Fecha de Subida', data['fecha_subida']],
            ['Usuario', data['usuario']],
            ['Tipo de Importación', data['tipo_importacion']],
            ['Estado', data['estado']]
        ]
        
        self._write_sheet(worksheet, headers, rows, header_format)
        worksheet.set_column('B:B', 20)

    def _add_statistics_sheet(self, workbook, header_format):
        worksheet = workbook.add_worksheet('Estadísticas')
        data = self.get_data()['estadisticas']
        
        headers = ['Métrica', 'Valor']
        rows = [
            ['Registros Totales', data['registros_totales']],
            ['Registros Procesados', data['registros_procesados']],
            ['Registros con Error', data['registros_con_error']],
            ['Porcentaje de Éxito', f"{data['porcentaje_exito']}%"]
        ]
        
        self._write_sheet(worksheet, headers, rows, header_format)

    def _add_corrections_sheet(self, workbook, header_format, date_format):
        worksheet = workbook.add_worksheet('Correcciones')
        data = self.get_data()['correcciones']
        
        headers = ['Campo', 'Valor Original', 'Valor Corregido', 'Usuario', 'Fecha', 'Justificación']
        rows = [
            [
                c['campo'],
                c['valor_original'],
                c['valor_corregido'],
                c['usuario'],
                c['fecha'],
                c['justificacion']
            ] for c in data
        ]
        
        self._write_sheet(worksheet, headers, rows, header_format)
        worksheet.set_column('A:F', 15)

    def _add_log_sheet(self, workbook, header_format):
        worksheet = workbook.add_worksheet('Log')
        data = self.get_data()['log_procesamiento']
        
        if isinstance(data, dict):
            headers = ['Tipo', 'Mensaje']
            rows = [[k, str(v)] for k, v in data.items()]
            self._write_sheet(worksheet, headers, rows, header_format)
        
        worksheet.set_column('A:B', 30)

    def _write_sheet(self, worksheet, headers, rows, header_format):
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        for row_idx, row in enumerate(rows, start=1):
            for col_idx, value in enumerate(row):
                worksheet.write(row_idx, col_idx, value)

class CSVExporter(BaseExporter):
    """Exportador a formato CSV"""
    def export(self):
        output = StringIO()
        writer = csv.writer(output)
        data = self.get_data()
        
        # Información General
        writer.writerow(['INFORMACIÓN GENERAL'])
        writer.writerow(['Campo', 'Valor'])
        for key, value in data['informacion_general'].items():
            writer.writerow([key, value])
        
        writer.writerow([])  # Línea en blanco
        
        # Estadísticas
        writer.writerow(['ESTADÍSTICAS'])
        writer.writerow(['Métrica', 'Valor'])
        for key, value in data['estadisticas'].items():
            writer.writerow([key, value])
        
        writer.writerow([])
        
        # Correcciones
        writer.writerow(['CORRECCIONES'])
        writer.writerow(['Campo', 'Valor Original', 'Valor Corregido', 'Usuario', 'Fecha', 'Justificación'])
        for correccion in data['correcciones']:
            writer.writerow([
                correccion['campo'],
                correccion['valor_original'],
                correccion['valor_corregido'],
                correccion['usuario'],
                correccion['fecha'],
                correccion['justificacion']
            ])
        
        return output.getvalue()

class PDFExporter(BaseExporter):
    """Exportador a formato PDF"""
    def export(self):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        data = self.get_data()
        
        # Título
        elements.append(Paragraph(f"Reporte de Importación #{data['informacion_general']['id']}", styles['Title']))
        elements.append(Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        
        # Información General
        elements.append(Paragraph("Información General", styles['Heading1']))
        info_data = [[k, str(v)] for k, v in data['informacion_general'].items()]
        info_table = Table([['Campo', 'Valor']] + info_data)
        info_table.setStyle(TableStyle([
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
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(info_table)
        
        # Estadísticas
        elements.append(Paragraph("Estadísticas", styles['Heading1']))
        stats_data = [[k, str(v)] for k, v in data['estadisticas'].items()]
        stats_table = Table([['Métrica', 'Valor']] + stats_data)
        stats_table.setStyle(TableStyle([
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
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(stats_table)
        
        # Correcciones
        if data['correcciones']:
            elements.append(Paragraph("Correcciones Realizadas", styles['Heading1']))
            corr_data = [
                [c['campo'], c['valor_original'], c['valor_corregido'], 
                 c['usuario'], c['fecha'].strftime('%d/%m/%Y %H:%M'), 
                 c['justificacion']] for c in data['correcciones']
            ]
            corr_table = Table([['Campo', 'Original', 'Corregido', 'Usuario', 'Fecha', 'Justificación']] + corr_data)
            corr_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(corr_table)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer 