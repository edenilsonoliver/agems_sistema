# acoes/forms.py
from django import forms
from .models import Acao, ChecklistItem
from usuarios.models import Usuario
from django.forms import inlineformset_factory
import magic
import os
import logging

logger = logging.getLogger(__name__)


class AcaoForm(forms.ModelForm):
    """
    Formulário unificado para Ação (substitui Acao e Tarefa antigos).
    """
    
    class Meta:
        model = Acao
        fields = [
            'nome', 'descricao', 'obrigacao', 'tipo_acao',
            'responsavel', 'executores', 'status', 
            'data_inicio', 'data_fim', 'data_conclusao',
            'prioridade', 'periodicidade', 'dias_antecedencia_alerta',
            'acoes_predecessoras', 'observacoes'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
            'data_inicio': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'data_fim': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'data_conclusao': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'executores': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '5'
            }),
            'acoes_predecessoras': forms.CheckboxSelectMultiple(),
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
        
        # Remover 'Finalizado' das opções manuais (será automático pelo checklist)
        self.fields['status'].choices = [
            choice for choice in self.fields['status'].choices 
            if choice[0] != 'finalizado'
        ]

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')

        if data_inicio and data_fim and data_fim < data_inicio:
            self.add_error('data_fim', "A data de fim não pode ser anterior à data de início.")
        
        return cleaned_data
        


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
    fields=['nome', 'concluido', 'ordem'],
    extra=0,
    can_delete=True,
    widgets={
        'nome': forms.TextInput(attrs={
            'class': 'form-control me-2',
            'placeholder': 'Novo item'
        }),
        'concluido': forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        'ordem': forms.HiddenInput(attrs={
            'class': 'checklist-order-field'
        }),
    }
)

# Ajuste global para tornar campos do checklist opcionais na validação de formulário novo
for field in ChecklistItemFormSet.form.base_fields.values():
    field.required = False


# Forms e FormSets para Documentos e Fotos (Fase 5)
from .models import AcaoDocumento, AcaoFoto

# Formset para Documentos
# Formset para Documentos

class AcaoDocumentoForm(forms.ModelForm):
    class Meta:
        model = AcaoDocumento
        fields = ['arquivo', 'descricao']
        widgets = {
            'arquivo': forms.FileInput(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição do arquivo', 'required': False}),
        }

    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        if not arquivo:
            return arquivo

        # Check for DELETE action to skip validation if deleting
        if self.cleaned_data.get('DELETE'):
            return arquivo
            
        # 1. Validação de Extensão
        ext = os.path.splitext(arquivo.name)[1].lower()
        allowed_extensions = {'.pdf', '.docx', '.xlsx', '.doc', '.xls', '.ppt', '.pptx', '.txt', '.csv', '.zip', '.rar'}
        
        if ext not in allowed_extensions:
             raise forms.ValidationError(f'Extensão {ext} não permitida.')

        # 2. Validação de MIME Type Real
        ALLOWED_MIMES = {
            'application/pdf',
            'application/msword', 
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/plain',
            'text/csv',
            'application/csv',
            'application/zip',
            'application/x-rar-compressed',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        }

        try:
            # Lê o início do arquivo para detectar o tipo
            initial_pos = arquivo.tell()
            mime_type = magic.from_buffer(arquivo.read(2048), mime=True)
            arquivo.seek(initial_pos) # Reseta o ponteiro de leitura
            
            if mime_type not in ALLOWED_MIMES:
                 # Verificações extras para casos ambíguos
                 if ext == '.csv' and mime_type in ['text/plain', 'application/csv']:
                     pass # OK
                 elif ext in ['.zip', '.docx', '.xlsx'] and mime_type == 'application/zip':
                     pass # OK
                 else:
                    raise forms.ValidationError(f'Arquivo inválido (Tipo detectado: {mime_type}).')

        except Exception as e:
            logger.error(f"Erro na validação MIME em Acoes: {e}")
            raise forms.ValidationError('Erro ao validar integridade do arquivo.')

        return arquivo

AcaoDocumentoFormSet = inlineformset_factory(
    Acao,
    AcaoDocumento,
    form=AcaoDocumentoForm,
    extra=0,
    can_delete=True
)

# Formset para Fotos
# Formset para Fotos
class AcaoFotoForm(forms.ModelForm):
    class Meta:
        model = AcaoFoto
        fields = ['imagem', 'legenda', 'coordenadas', 'data_registro']
        widgets = {
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'legenda': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Legenda da foto'}),
            'coordenadas': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Latitude, Longitude'}),
            'data_registro': forms.HiddenInput(),
        }

    def clean_imagem(self):
        imagem = self.cleaned_data.get('imagem')
        if not imagem:
            return imagem

        # Check for DELETE action
        if self.cleaned_data.get('DELETE'):
            return imagem
            
        # 1. Validação de Extensão
        ext = os.path.splitext(imagem.name)[1].lower()
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif'}
        
        if ext not in allowed_extensions:
             raise forms.ValidationError(f'Extensão {ext} não permitida para fotos.')

        # 2. Validação de MIME Type Real
        ALLOWED_MIMES = {
            'image/jpeg',
            'image/png',
            'image/webp',
            'image/heic', 
            'image/heif',
            'application/octet-stream' # Algumas variantes de HEIC podem vir assim
        }

        try:
            initial_pos = imagem.tell()
            mime_type = magic.from_buffer(imagem.read(2048), mime=True)
            imagem.seek(initial_pos)
            
            # Tratamento especial para HEIC/HEIF que as vezes é detectado como octet-stream ou application/x-ole-storage
            if ext in ['.heic', '.heif'] and mime_type in ['application/octet-stream', 'application/x-ole-storage']:
                pass # Aceitar, pois libmagic pode não ter assinatura exata para toda variante de HEIC
            elif mime_type not in ALLOWED_MIMES:
                raise forms.ValidationError(f'Arquivo inválido. Tipo de imagem detectado: {mime_type}')

        except Exception as e:
            logger.error(f"Erro na validação MIME de Foto: {e}")
            raise forms.ValidationError('Erro ao validar integridade da imagem.')

        return imagem

AcaoFotoFormSet = inlineformset_factory(
    Acao,
    AcaoFoto,
    form=AcaoFotoForm,
    extra=0,
    can_delete=True
)
