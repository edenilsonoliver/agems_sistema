from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import Instrumento, Obrigacao


class InstrumentoForm(forms.ModelForm):
    class Meta:
        model = Instrumento
        fields = '__all__'
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
            'data_assinatura': forms.DateInput(attrs={'type': 'date'}),
        }


class ObrigacaoForm(forms.ModelForm):
    class Meta:
        model = Obrigacao
        fields = '__all__'
        widgets = {
            'data_vencimento': forms.DateInput(attrs={'type': 'date'}),
        }
