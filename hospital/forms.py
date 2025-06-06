from django import forms
from .models import * 

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nombre', 'apellido', 'edad', 'sexo', 'sintomas']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'edad': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '0', 
                'max': '90', 
                'placeholder': 'Edad'
            }),
            'sexo': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'sintomas': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe los síntomas'}),
        }
        
    def clean_edad(self):
        edad = self.cleaned_data.get('edad')
        if edad < 0 or edad > 90:
            raise forms.ValidationError("La edad debe estar entre 0 y 90 años.")
        return edad
