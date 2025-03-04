from django import forms
from .models import InsumoMedico

class InsumoMedicoForm(forms.ModelForm):
    class Meta:
        model = InsumoMedico
        fields = '__all__'
