# acoes/forms.py
from django import forms
from .models import Acao
from usuarios.models import Usuario
from django.forms import inlineformset_factory
from .models import Tarefa, ChecklistItem

class AcaoForm(forms.ModelForm):
    class Meta:
        model = Acao
        fields = [
            'nome', 'descricao','instrumento', 'obrigacao', 'tipo_acao',
            'responsavel', 'status', 'percentual_cumprido',
            'periodicidade', 'data_inicio', 'data_fim_prevista', 'data_fim_real',
            'dias_antecedencia_alerta', 'observacoes'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personaliza o campo responsável
        usuarios = Usuario.objects.select_related('subunidade__diretoria').all()
        self.fields['responsavel'].queryset = usuarios
        self.fields['responsavel'].label_from_instance = self.formatar_responsavel
        self.fields['descricao'].required = False  # 🔹 torna o campo opcional

    def formatar_responsavel(self, usuario):
        # Tenta usar o nome completo, se existir, ou combina nome e sobrenome, ou usa username
        nome = getattr(usuario, 'nome_completo', None) \
            or getattr(usuario, 'nome', None) \
            or f"{getattr(usuario, 'first_name', '')} {getattr(usuario, 'last_name', '')}".strip() \
            or getattr(usuario, 'username', 'Sem nome')

        sub = getattr(usuario.subunidade, 'nome', 'Sem subunidade') if hasattr(usuario, 'subunidade') else 'Sem subunidade'
        dir = getattr(usuario.subunidade.diretoria, 'sigla', 'Sem diretoria') \
            if hasattr(usuario, 'subunidade') and hasattr(usuario.subunidade, 'diretoria') else 'Sem diretoria'

        return f"{nome} | {sub} | {dir}"

ChecklistItemFormSet = inlineformset_factory(
    Tarefa, ChecklistItem,
    fields=['nome', 'concluido'],
    extra=1,
    can_delete=True
)