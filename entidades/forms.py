from django import forms
from .models import Entidade

class EntidadeForm(forms.ModelForm):
    class Meta:
        model = Entidade
        fields = '__all__'
        widgets = {
            'cnpj': forms.TextInput(attrs={'placeholder': '00.000.000/0000-00'}),
            'cep': forms.TextInput(attrs={'placeholder': '00000-000'}),
        }

    def __init__(self, *args, **kwargs):
        self.readonly = kwargs.pop('readonly', False)
        super().__init__(*args, **kwargs)
        if self.readonly:
            for field in self.fields.values():
                field.disabled = True
