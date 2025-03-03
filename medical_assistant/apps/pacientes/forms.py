from django import forms
from django.core.exceptions import ValidationError
from .models import Paciente
from datetime import date

class PacienteForm(forms.ModelForm):
    # Campos personalizados con widgets mejorados
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'max': date.today().strftime('%Y-%m-%d')
            }
        ),
        help_text='Formato: DD-MM-AAAA'
    )

    fecha_hora_ingreso = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }
        )
    )

    observaciones = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Ingrese observaciones relevantes...'
            }
        ),
        required=False
    )

    class Meta:
        model = Paciente
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del paciente'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido del paciente'}),
            'dni': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DNI sin puntos ni espacios'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'obra_social': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_afiliacion': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+54-XXX-XXXXXXX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@email.com'}),
            'sanatorio': forms.Select(attrs={'class': 'form-select'}),
            'procedimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'medico': forms.TextInput(attrs={'class': 'form-control'}),
            'anti_coagulantes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'instrumentador': forms.TextInput(attrs={'class': 'form-control'}),
            'anestesia': forms.Select(attrs={'class': 'form-select'}),
            'autorizacion': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cx': forms.TextInput(attrs={'class': 'form-control'}),
            'protocolo': forms.TextInput(attrs={'class': 'form-control'}),
            'derivado': forms.TextInput(attrs={'class': 'form-control'})
        }

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if not dni.isdigit():
            raise ValidationError("El DNI debe contener solo números.")
        return dni

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and not telefono.replace('+', '').replace('-', '').isdigit():
            raise ValidationError("El teléfono debe contener solo números, '+' y '-'.")
        return telefono

    def clean(self):
        cleaned_data = super().clean()
        fecha_nacimiento = cleaned_data.get('fecha_nacimiento')
        
        if fecha_nacimiento and fecha_nacimiento > date.today():
            raise ValidationError("La fecha de nacimiento no puede ser futura.")
        
        return cleaned_data


class ArchivoExcelForm(forms.Form):
    archivo = forms.FileField(
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'accept': '.xlsx,.xls'
            }
        ),
        help_text='Seleccione un archivo Excel (.xlsx o .xls)'
    )

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            extension = archivo.name.split('.')[-1].lower()
            if extension not in ['xlsx', 'xls']:
                raise ValidationError("El archivo debe ser un archivo Excel (.xlsx o .xls)")
        return archivo

