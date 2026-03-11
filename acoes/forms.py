# acoes/forms.py
from django import forms
from .models import Acao, ChecklistItem
from usuarios.models import Usuario
from django.forms import inlineformset_factory
from instrumentos.models import Instrumento
from entidades.models import Entidade
import os
import logging

logger = logging.getLogger(__name__)


class AcaoForm(forms.ModelForm):
    """
    Formulário unificado para Ação.
    """
    # Campo extra (não é campo do model Acao) para filtro dinâmico de Obrigação
    instrumento = forms.ModelChoiceField(
        queryset=Instrumento.objects.all(),
        required=False,
        label='Instrumento',
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_instrumento'})
    )

    class Meta:
        model = Acao
        fields = [
            'nome', 'descricao', 'obrigacao', 'tipo_acao',
            'responsavel', 'executores', 'status',
            'data_inicio', 'data_fim', 'data_conclusao',
            'prioridade', 'periodicidade', 'dias_antecedencia_alerta',
            'observacoes',
            # Novos campos de resultado
            'resultado', 'entidade', 'justificativa_resultado',
            # NOTA: acoes_predecessoras mantido no banco mas removido do formulário
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'justificativa_resultado': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descreva o motivo do resultado informado...'
            }),
            'data_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'data_fim': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'data_conclusao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'executores': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '5'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)

        self.readonly = kwargs.pop('readonly', False)
        self.executor_readonly = kwargs.pop('executor_readonly', False)
        super().__init__(*args, **kwargs)
        
        if self.readonly:
            for field in self.fields.values():
                field.disabled = True
        elif self.executor_readonly:
            allowed_fields = ['status', 'data_conclusao', 'observacoes', 'resultado', 'entidade', 'justificativa_resultado']
            for field_name, field in self.fields.items():
                if field_name not in allowed_fields:
                    field.disabled = True


        # Adicionar form-control em todos os campos que não têm via widget
        for field_name, field in self.fields.items():
            widget = field.widget
            css = widget.attrs.get('class', '')
            if 'form-control' not in css and 'form-check-input' not in css:
                widget.attrs['class'] = ('form-control ' + css).strip()

        # Lógica rigorosa de filtragem de usuários (Diretoria do Instrumento)
        from django.db.models import Q
        
        # 1. Regra Absoluta: NENHUM Admin (perfil=0) pode figurar como Responsável/Executor.
        base_usuarios = Usuario.objects.select_related('subunidade', 'subunidade__diretoria').filter(
            is_active=True
        ).exclude(perfil=0)
        
        # 2. Resolução do Instrumento ativo
        inst = None
        if self.instance and self.instance.pk and getattr(self.instance, 'obrigacao_id', None):
            inst = self.instance.obrigacao.instrumento
        elif self.data and self.data.get('instrumento'):
            try:
                inst = Instrumento.objects.get(pk=self.data.get('instrumento'))
            except:
                pass
                
        # 3. Filtrar pelas Subunidades do Instrumento (se houver), senão cair pro legado da Diretoria
        if inst and inst.diretoria:
            subunidades = inst.subunidades.all()
            if subunidades.exists():
                # Regra: Inclui usuários da subunidade E Gestores (P1/P2) da Diretoria
                usuarios = base_usuarios.filter(
                    Q(subunidade__in=subunidades) | Q(perfil__in=[1, 2], diretoria=inst.diretoria)
                )
            else:
                usuarios = base_usuarios.filter(
                    Q(diretoria=inst.diretoria) | Q(subunidade__diretoria=inst.diretoria)
                )
        else:
            # Caso não haja instrumento selecionado (Formulário Limpo / Nova Ação)
            # Retorna queryset vazia para forçar o usuário a escolher o Instrumento primeiro.
            # E se por acaso já existirem na base legada dados fora disso, o queryset vazio no create garante que 
            # a listagem inicie limpa até o AJAX preencher visualmente, e no post o self.data resolve.
            usuarios = base_usuarios.none()

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
        self.fields['resultado'].required = False
        self.fields['entidade'].required = False
        self.fields['justificativa_resultado'].required = False

        # Se estamos editando uma ação existente, pré-preencher instrumento e filtrar entidades
        if self.instance and self.instance.pk and getattr(self.instance, 'obrigacao_id', None):
            try:
                instrumento = self.instance.obrigacao.instrumento
                self.fields['instrumento'].initial = instrumento
                # Filtrar entidades apenas do instrumento desta ação
                self.fields['entidade'].queryset = instrumento.entidades.all()
            except Exception:
                self.fields['entidade'].queryset = Entidade.objects.none()
        elif self.data and self.data.get('instrumento'):
            # Nova Ação via POST: instrumento já vem no request.POST (self.data)
            try:
                instrumento_id = self.data.get('instrumento')
                instrumento = Instrumento.objects.get(pk=instrumento_id)
                self.fields['entidade'].queryset = instrumento.entidades.all()
            except Exception:
                self.fields['entidade'].queryset = Entidade.objects.none()
        else:
            # Nova ação form vazio: para evitar erro de inicialização se JS manipular antes, abrimos fallback
            # Mas o recomendado para forms vazios antes do usuário mexer é deixar o queryset vazio
            self.fields['entidade'].queryset = Entidade.objects.none()

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
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/x-ole-storage'
        }

        try:
            if self.instance.pk and self.instance.arquivo == arquivo:
                if not os.path.exists(arquivo.path):
                    logger.warning(f"Arquivo legado não encontrado no disco: {arquivo.path}. Pulando validação MIME.")
                    return arquivo

            arquivo.seek(0)
            chunk = arquivo.read(2048)
            arquivo.seek(0)

            mime_type = None
            try:
                import magic
                m = magic.Magic(mime=True)
                mime_type = m.from_buffer(chunk)
            except AttributeError:
                try:
                    mime_type = magic.from_buffer(chunk, mime=True)
                except Exception as e2:
                    logger.error(f"Falha total em detectar MIME: {e2}")

            if mime_type:
                if mime_type not in ALLOWED_MIMES:
                     if ext == '.csv' and mime_type in ['text/plain', 'application/csv']:
                         pass
                     elif ext in ['.zip', '.docx', '.xlsx', '.pptx'] and mime_type == 'application/zip':
                         pass
                     elif ext in ['.doc', '.xls', '.ppt'] and mime_type == 'application/x-ole-storage':
                         pass
                     else:
                        raise forms.ValidationError(f'Arquivo inválido (Tipo detectado: {mime_type}).')
            else:
                logger.warning("Não foi possível detectar o MIME type, mas a extensão é válida. Permitindo por segurança.")

        except forms.ValidationError:
            raise
        except Exception as e:
            logger.error(f"Erro na validação MIME em Acoes: {e}")
            return arquivo

        return arquivo

AcaoDocumentoFormSet = inlineformset_factory(
    Acao,
    AcaoDocumento,
    form=AcaoDocumentoForm,
    extra=0,
    can_delete=True
)


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
            'application/octet-stream',
            'application/x-ole-storage'
        }

        try:
            if self.instance.pk and self.instance.imagem == imagem:
                if not os.path.exists(imagem.path):
                    logger.warning(f"Foto legada não encontrada no disco: {imagem.path}. Pulando validação MIME.")
                    return imagem

            imagem.seek(0)
            chunk = imagem.read(2048)
            imagem.seek(0)

            mime_type = None
            try:
                import magic
                m = magic.Magic(mime=True)
                mime_type = m.from_buffer(chunk)
            except AttributeError:
                try:
                    mime_type = magic.from_buffer(chunk, mime=True)
                except Exception as e2:
                    logger.error(f"Falha total em detectar MIME de Imagem: {e2}")

            if mime_type:
                if ext in ['.heic', '.heif'] and mime_type in ['application/octet-stream', 'application/x-ole-storage']:
                    pass
                elif mime_type not in ALLOWED_MIMES:
                    raise forms.ValidationError(f'Arquivo inválido. Tipo de imagem detectado: {mime_type}')
            else:
                logger.warning("Não foi possível detectar o MIME da imagem, permitindo pela extensão.")

        except forms.ValidationError:
            raise
        except Exception as e:
            logger.error(f"Erro na validação MIME de Foto: {e}")
            return imagem

        return imagem

AcaoFotoFormSet = inlineformset_factory(
    Acao,
    AcaoFoto,
    form=AcaoFotoForm,
    extra=0,
    can_delete=True
)
