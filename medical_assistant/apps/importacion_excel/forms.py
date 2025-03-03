from django import forms
from .models import ExcelImport, MapeoColumnas, ReglaCorreccion

class ArchivoExcelForm(forms.ModelForm):
    """Formulario para la carga inicial del archivo Excel"""
    class Meta:
        model = ExcelImport
        fields = ['archivo', 'tipo_importacion']
        widgets = {
            'archivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.xlsx,.xls',
                'data-max-size': '5242880'  # 5MB en bytes
            }),
            'tipo_importacion': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        help_texts = {
            'archivo': 'Seleccione un archivo Excel (.xlsx, .xls). Tamaño máximo: 5MB',
            'tipo_importacion': 'Seleccione el tipo de datos que contiene el archivo'
        }

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            # Verificar extensión
            ext = archivo.name.split('.')[-1].lower()
            if ext not in ['xlsx', 'xls']:
                raise forms.ValidationError('El archivo debe ser un Excel (.xlsx, .xls)')
            
            # Verificar tamaño
            if archivo.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError('El archivo no debe superar los 5MB')
        
        return archivo

class MapeoColumnasForm(forms.ModelForm):
    """Formulario para configurar el mapeo de columnas"""
    class Meta:
        model = MapeoColumnas
        fields = ['nombre_columna_excel', 'campo_modelo', 'transformacion', 
                 'funcion_transformacion', 'es_requerido', 'valor_defecto']
        widgets = {
            'nombre_columna_excel': forms.TextInput(attrs={'class': 'form-control'}),
            'campo_modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'transformacion': forms.Select(attrs={'class': 'form-select'}),
            'funcion_transformacion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'def transformar(valor):\n    return valor.upper()'
            }),
            'es_requerido': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'valor_defecto': forms.TextInput(attrs={'class': 'form-control'})
        }

class ReglaCorreccionForm(forms.ModelForm):
    """Formulario para crear/editar reglas de corrección"""
    class Meta:
        model = ReglaCorreccion
        fields = ['campo', 'patron_original', 'correccion', 'activa']
        widgets = {
            'campo': forms.TextInput(attrs={'class': 'form-control'}),
            'patron_original': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Expresión regular o patrón a buscar'
            }),
            'correccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Valor de reemplazo'
            }),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        help_texts = {
            'patron_original': 'Puede usar expresiones regulares (ej: [0-9]{8})',
            'correccion': 'Valor que reemplazará al patrón encontrado'
        }

class CorreccionManualForm(forms.Form):
    """Formulario para correcciones manuales durante la revisión"""
    valor_original = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True})
    )
    valor_corregido = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    justificacion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Razón de la corrección'
        })
    )