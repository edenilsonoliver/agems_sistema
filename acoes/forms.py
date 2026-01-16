# acoes/forms.py
from django import forms
from .models import Acao, ChecklistItem
from usuarios.models import Usuario
from django.forms import inlineformset_factory


class AcaoForm(forms.ModelForm):
    """
    Formulário unificado para Ação (substitui Acao e Tarefa antigos).
    """
    
    class Meta:
        model = Acao
        fields = [
            'nome', 'descricao', 'obrigacao', 'tipo_acao',
            'responsavel', 'executores', 'status', 'percentual_cumprido',
            'data_inicio', 'data_fim', 'data_conclusao',
            'prioridade', 'periodicidade', 'dias_antecedencia_alerta',
            'acoes_predecessoras', 'observacoes'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
            'executores': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '5'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Buscar usuários com relações
        usuarios = Usuario.objects.select_related('subunidade__diretoria').all()
        
        # Configurar campos de usuários
        self.fields['responsavel'].queryset = usuarios
        self.fields['responsavel'].label_from_instance = self.formatar_usuario
        self.fields['executores'].queryset = usuarios
        self.fields['executores'].label_from_instance = self.formatar_usuario
        
        # Campos opcionais
        self.fields['descricao'].required = False
        self.fields['data_conclusao'].required = False
        self.fields['observacoes'].required = False
        self.fields['tipo_acao'].required = False
        


    def formatar_usuario(self, usuario):
        """Formata a exibição do usuário no select"""
        nome = getattr(usuario, 'nome_completo', None) \
            or f"{getattr(usuario, 'first_name', '')} {getattr(usuario, 'last_name', '')}".strip() \
            or getattr(usuario, 'username', 'Sem nome')

        sub = getattr(usuario.subunidade, 'nome', 'Sem subunidade') if hasattr(usuario, 'subunidade') and usuario.subunidade else 'Sem subunidade'
        dir = getattr(usuario.subunidade.diretoria, 'sigla', 'Sem diretoria') \
            if hasattr(usuario, 'subunidade') and usuario.subunidade and hasattr(usuario.subunidade, 'diretoria') and usuario.subunidade.diretoria \
            else 'Sem diretoria'

        return f"{nome} | {sub} | {dir}"


# Formset para o Checklist (Sub-tarefas da Ação)
ChecklistItemFormSet = inlineformset_factory(
    Acao,
    ChecklistItem,
    fields=['nome', 'concluido'],
    extra=1,
    can_delete=True,
    widgets={
        'nome': forms.TextInput(attrs={
            'class': 'form-control me-2',
            'placeholder': 'Novo item'
        }),
        'concluido': forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
    }
)

# Ajuste global para tornar campos do checklist opcionais na validação de formulário novo
for field in ChecklistItemFormSet.form.base_fields.values():
    field.required = False
