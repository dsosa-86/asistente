from django import forms
from .models import EstudioPrequirurgico, PrequirurgicoPaciente, Operacion

class EstudioPrequirurgicoForm(forms.ModelForm):
    class Meta:
        model = EstudioPrequirurgico
        fields = ['nombre', 'descripcion', 'tipo', 'tipo_cirugia', 'es_obligatorio']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'tipo_cirugia': forms.Select(attrs={'class': 'form-select'}),
            'es_obligatorio': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        help_texts = {
            'nombre': 'Nombre del estudio prequirúrgico',
            'descripcion': 'Descripción detallada del estudio',
            'tipo': 'Tipo de estudio (laboratorio, imagen, etc.)',
            'tipo_cirugia': 'Tipo de cirugía que requiere este estudio',
            'es_obligatorio': 'Indica si el estudio es obligatorio para la cirugía'
        }

class PrequirurgicoPacienteForm(forms.ModelForm):
    class Meta:
        model = PrequirurgicoPaciente
        fields = ['resultado', 'archivo']
        widgets = {
            'resultado': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ingrese el resultado del estudio'
            }),
            'archivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            })
        }
        help_texts = {
            'resultado': 'Describa los resultados del estudio',
            'archivo': 'Adjunte el archivo con los resultados (PDF o imagen)'
        }

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            # Verificar el tamaño del archivo (máximo 5MB)
            if archivo.size > 5 * 1024 * 1024:
                raise forms.ValidationError('El archivo no debe superar los 5MB')
            
            # Verificar la extensión
            ext = archivo.name.split('.')[-1].lower()
            if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
                raise forms.ValidationError('Formato de archivo no permitido')
        
        return archivo

class FiltroEstudioForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar estudio...'
        })
    )
    tipo = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + EstudioPrequirurgico.TIPOS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tipo_cirugia = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="Todas las cirugías",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import TipoCirugia
        self.fields['tipo_cirugia'].queryset = TipoCirugia.objects.all()

class OperacionForm(forms.ModelForm):
    class Meta:
        model = Operacion
        fields = '__all__'