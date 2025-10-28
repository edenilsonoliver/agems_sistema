# acoes/forms.py
from django import forms
from .models import Acao, Tarefa, ChecklistItem
from usuarios.models import Usuario
from django.forms import inlineformset_factory


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


class TarefaForm(forms.ModelForm):
    """Formulário para criação e edição de tarefas"""
    
    class Meta:
        model = Tarefa
        fields = [
            'nome', 'descricao', 'acao',
            'responsavel', 'executores',
            'status', 'percentual_cumprido',
            'data_inicio', 'data_fim', 'data_conclusao',
            'tarefas_predecessoras', 'prioridade', 'observacoes'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
            # Widgets de texto com máscara para campos de data (formato brasileiro)
            'data_inicio': forms.TextInput(
                attrs={
                    'class': 'form-control date-mask',
                    'placeholder': 'dd/mm/aaaa',
                    'maxlength': '10'
                }
            ),
            'data_fim': forms.TextInput(
                attrs={
                    'class': 'form-control date-mask',
                    'placeholder': 'dd/mm/aaaa',
                    'maxlength': '10'
                }
            ),
            'data_conclusao': forms.TextInput(
                attrs={
                    'class': 'form-control date-mask',
                    'placeholder': 'dd/mm/aaaa',
                    'maxlength': '10'
                }
            ),
            # Widget para seleção múltipla de executores
            'executores': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '5'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar formato de entrada de data brasileiro
        self.fields['data_inicio'].input_formats = ['%d/%m/%Y', '%Y-%m-%d']
        self.fields['data_fim'].input_formats = ['%d/%m/%Y', '%Y-%m-%d']
        self.fields['data_conclusao'].input_formats = ['%d/%m/%Y', '%Y-%m-%d']
        
        # Buscar todos os usuários com suas relações
        usuarios = Usuario.objects.select_related('subunidade__diretoria').all()
        
        # Configurar campo Responsável (ForeignKey - apenas 1)
        self.fields['responsavel'].queryset = usuarios
        self.fields['responsavel'].label_from_instance = self.formatar_usuario
        
        # Configurar campo Executores (ManyToMany - vários)
        self.fields['executores'].queryset = usuarios
        self.fields['executores'].label_from_instance = self.formatar_usuario
        
        # Campos opcionais
        self.fields['descricao'].required = False
        self.fields['data_conclusao'].required = False
        self.fields['observacoes'].required = False
        
        # Converter valores de data para formato brasileiro (dd/mm/yyyy) para exibição
        if self.instance and self.instance.pk:
            if self.instance.data_inicio:
                self.initial['data_inicio'] = self.instance.data_inicio.strftime('%d/%m/%Y')
            if self.instance.data_fim:
                self.initial['data_fim'] = self.instance.data_fim.strftime('%d/%m/%Y')
            if self.instance.data_conclusao:
                self.initial['data_conclusao'] = self.instance.data_conclusao.strftime('%d/%m/%Y')

    def formatar_usuario(self, usuario):
        """
        Formata a exibição do usuário no select
        Formato: Nome Completo | Subunidade | Diretoria
        """
        # Nome do usuário
        nome = getattr(usuario, 'nome_completo', None) \
            or getattr(usuario, 'nome', None) \
            or f"{getattr(usuario, 'first_name', '')} {getattr(usuario, 'last_name', '')}".strip() \
            or getattr(usuario, 'username', 'Sem nome')

        # Subunidade
        sub = getattr(usuario.subunidade, 'nome', 'Sem subunidade') \
            if hasattr(usuario, 'subunidade') and usuario.subunidade else 'Sem subunidade'
        
        # Diretoria
        dir = getattr(usuario.subunidade.diretoria, 'sigla', 'Sem diretoria') \
            if hasattr(usuario, 'subunidade') and usuario.subunidade and hasattr(usuario.subunidade, 'diretoria') and usuario.subunidade.diretoria \
            else 'Sem diretoria'

        return f"{nome} | {sub} | {dir}"


ChecklistItemFormSet = inlineformset_factory(
    Tarefa,
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

# Permite que formulários vazios sejam ignorados (não geram erro de validação)
for field in ChecklistItemFormSet.form.base_fields.values():
    field.required = False

