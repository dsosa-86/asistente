from django import forms
from .models import ObraSocial

class ObraSocialForm(forms.ModelForm):
    class Meta:
        model = ObraSocial
        fields = '__all__'
