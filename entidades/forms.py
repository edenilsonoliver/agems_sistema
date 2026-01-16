from django import forms
from .models import Entidade

class EntidadeForm(forms.ModelForm):
    class Meta:
        model = Entidade
        fields = '__all__'
        widgets = {
            'cnpj': forms.TextInput(attrs={'placeholder': '00.000.000/0000-00'}),
            'cep': forms.TextInput(attrs={'placeholder': '00.000-000'}),
        }
