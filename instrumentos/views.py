from django import forms
from django.db.models import Count
import logging

logger = logging.getLogger(__name__)
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.forms import inlineformset_factory
from core.views import ModernListView, ModernCreateView, ModernUpdateView, ModernDeleteView
from core.models import TipoInstrumento, Diretoria, TipoObrigacao
from .models import Instrumento, Obrigacao, ArquivoInstrumento
import csv
import io
import json
from .forms import ImportacaoObrigacoesForm


class InstrumentoForm(forms.ModelForm):
    """Formulário personalizado para Instrumento"""
    class Meta:
        model = Instrumento
        fields = [
            'numero', 'tipo_instrumento', 'diretoria', 'entidades',
            'objeto', 'nup', 'data_assinatura', 'data_inicio', 'data_fim',
            'status', 'periodicidade_revisao_tarifaria', 'data_proxima_revisao',
            'observacoes'
        ]
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_instrumento': forms.Select(attrs={'class': 'form-select'}),
            'diretoria': forms.Select(attrs={'class': 'form-select'}),
            'entidades': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
            'objeto': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nup': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 12345.678901/2024-00'}),
            'data_assinatura': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'data_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'data_fim': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'periodicidade_revisao_tarifaria': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_proxima_revisao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')

        if data_inicio and data_fim and data_fim < data_inicio:
            self.add_error('data_fim', "A data de fim não pode ser anterior à data de início.")
        
        return cleaned_data


class ObrigacaoForm(forms.ModelForm):
    """Formulário para Obrigação inline (sem campo instrumento)"""
    class Meta:
        model = Obrigacao
        fields = ['titulo', 'descricao', 'tipo_obrigacao', 'clausula_referencia', 
                  'data_vencimento', 'status', 'recorrente']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'tipo_obrigacao': forms.Select(attrs={'class': 'form-select'}),
            'clausula_referencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Cláusula 5.2'}),
            'data_vencimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'recorrente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# Formset para obrigações inline
ObrigacaoFormSet = inlineformset_factory(
    Instrumento,
    Obrigacao,
    form=ObrigacaoForm,
    extra=0,  # Não mostrar formulários vazios por padrão
    can_delete=True
)


class InstrumentoListView(ModernListView):
    model = Instrumento
    template_name = 'instrumentos/instrumento_list.html'
    icon = "bi bi-file-earmark-text"
    create_url = 'instrumento_create'
    search_fields = ['numero', 'objeto', 'nup']


class InstrumentoCreateView(ModernCreateView):
    model = Instrumento
    form_class = InstrumentoForm
    template_name = 'instrumentos/instrumento_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ObrigacaoFormSet(self.request.POST, prefix='obrigacoes')
        else:
            context['formset'] = ObrigacaoFormSet(prefix='obrigacoes')
        context['arquivos'] = []
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect('instrumento_edit', pk=self.object.pk)
        else:
            return self.form_invalid(form)

class InstrumentoUpdateView(ModernUpdateView):
    model = Instrumento
    form_class = InstrumentoForm
    template_name = 'instrumentos/instrumento_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ObrigacaoFormSet(self.request.POST, instance=self.object, prefix='obrigacoes')
        else:
            queryset = self.object.obrigacoes.annotate(acoes_count=Count('acoes'))
            context['formset'] = ObrigacaoFormSet(instance=self.object, queryset=queryset, prefix='obrigacoes')
        context['arquivos'] = getattr(self.object, 'arquivos', []).all() if hasattr(self.object, 'arquivos') else []
        return context

    def post(self, request, *args, **kwargs):
        """Sobrescreve post() para permitir salvar o formset mesmo se o form principal não mudar"""
        self.object = self.get_object()
        form = self.get_form()
        queryset = self.object.obrigacoes.annotate(acoes_count=Count('acoes'))
        formset = ObrigacaoFormSet(self.request.POST, instance=self.object, queryset=queryset, prefix='obrigacoes')

        if form.is_valid() and formset.is_valid():
            self.object = form.save(commit=False)
            self.object.save()
            formset.instance = self.object
            formset.save()
            return redirect('instrumento_edit', pk=self.object.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form, formset=formset))

class InstrumentoDeleteView(ModernDeleteView):
    model = Instrumento
    success_url = reverse_lazy('instrumento_list')


# ===== VIEWS API PARA CRUD INLINE =====

@require_POST
def tipo_instrumento_create(request):
    """Criar tipo de instrumento via AJAX"""
    nome = request.POST.get('nome')
    if nome:
        tipo = TipoInstrumento.objects.create(nome=nome)
        return JsonResponse({'success': True, 'id': tipo.id, 'nome': tipo.nome})
    return JsonResponse({'success': False, 'error': 'Nome não fornecido'})


@require_POST
def diretoria_create(request):
    """Criar diretoria via AJAX"""
    sigla = request.POST.get('sigla')
    nome = request.POST.get('nome')
    if sigla and nome:
        diretoria = Diretoria.objects.create(sigla=sigla, nome=nome)
        return JsonResponse({'success': True, 'id': diretoria.id})
    return JsonResponse({'success': False, 'error': 'Dados incompletos'})


import zipfile
import os
from django.utils.text import slugify

@require_POST
def arquivo_upload(request, instrumento_id):
    """Upload de arquivo para instrumento via AJAX com validação de segurança"""
    instrumento = get_object_or_404(Instrumento, pk=instrumento_id)
    arquivo = request.FILES.get('arquivo')
    nome = request.POST.get('nome_arquivo', '')
    
    if not arquivo:
        return JsonResponse({'success': False, 'error': 'Nenhum arquivo enviado.'})

    # 1. Validação de Extensão
    ext = os.path.splitext(arquivo.name)[1].lower()
    allowed_extensions = ['.pdf', '.docx', '.xlsx']
    
    if ext not in allowed_extensions:
        return JsonResponse({
            'success': False, 
            'error': f'Extensão {ext} não permitida. Use apenas PDF, DOCX ou XLSX.'
        })

    # 2. Verificação de Macros (para arquivos Office)
    if ext in ['.docx', '.xlsx']:
        try:
            # Arquivos Office modernos são ZIPs. Macros ficam em vbaProject.bin
            with zipfile.ZipFile(arquivo) as z:
                # Se encontrar qualquer arquivo .bin suspeito ou vbaProject
                if any(item.filename.endswith('.bin') for item in z.infolist()):
                    return JsonResponse({
                        'success': False, 
                        'error': 'O arquivo contém macros ou conteúdo binário não permitido por segurança.'
                    })
        except zipfile.BadZipFile:
            return JsonResponse({'success': False, 'error': 'Arquivo corrompido ou inválido.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Erro ao processar arquivo: {str(e)}'})

    try:
        # 3. Salvamento Seguro
        # O Django já cuida de evitar sobrescrita, mas vamos garantir um nome limpo
        arquivo_obj = ArquivoInstrumento.objects.create(
            instrumento=instrumento,
            arquivo=arquivo,
            nome_arquivo=nome or arquivo.name
        )
        return JsonResponse({
            'success': True,
            'id': arquivo_obj.id,
            'nome': arquivo_obj.nome_arquivo,
            'url': arquivo_obj.arquivo.url
        })
    except Exception as e:
        logger.error(f"Erro no upload de arquivo: {str(e)}")
        return JsonResponse({'success': False, 'error': f'Erro ao salvar no banco de dados: {str(e)}'})

@require_POST
def arquivo_delete(request, arquivo_id):
    """Excluir arquivo de instrumento via AJAX"""
    arquivo = get_object_or_404(ArquivoInstrumento, pk=arquivo_id)
    try:
        # Remove fisicamente o arquivo se desejar, ou apenas o registro
        # O default do FileField.delete() é apagar o arquivo do sistema
        arquivo.arquivo.delete(save=False)
        arquivo.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Erro ao excluir arquivo {arquivo_id}: {str(e)}")

@require_POST
def importar_obrigacoes_csv(request):
    """
    Processa upload de CSV e retorna dados JSON das obrigações.
    NÃO salva no banco. Apenas parseia para preenchimento do formulário.
    """
    form = ImportacaoObrigacoesForm(request.POST, request.FILES)
    if form.is_valid():
        arquivo = request.FILES['arquivo_csv']
        try:
            # Lê e decodifica o arquivo
            content = arquivo.read().decode('utf-8-sig')
            decoded_file = content.splitlines()
            
            if not decoded_file:
                 return JsonResponse({'status': 'error', 'message': 'Arquivo CSV vazio ou inválido.'})

            # Detecção inteligente de delimitador
            # Verifica o primeiro caractere separador comum na primeira linha
            primeira_linha = decoded_file[0]
            delimitador = ';' if ';' in primeira_linha else ','
            
            reader = csv.DictReader(decoded_file, delimiter=delimitador, quotechar='"')
            
            # Normalizar headers
            if not reader.fieldnames:
                 return JsonResponse({'status': 'error', 'message': 'Não foi possível ler os cabeçalhos do arquivo.'})

            headers_map = {h.strip().lower(): h for h in reader.fieldnames}
            headers_lower = headers_map.keys()
            
            # Validação de colunas mínimas
            esperados = ['titulo', 'descricao', 'clausula', 'tipo']
            faltantes = [campo for campo in esperados if campo not in headers_lower]
            
            if faltantes:
                 encontrados = list(headers_lower)
                 msg_debug = f" (Encontrado: {', '.join(encontrados)})" if encontrados else ""
                 return JsonResponse({
                     'status': 'error', 
                     'message': f'Colunas obrigatórias faltando: {", ".join(faltantes)}.{msg_debug}'
                 }, status=400)
            
            # Cache de Tipos de Obrigação
            tipos_bd = list(TipoObrigacao.objects.values('id', 'nome'))
            tipos_map = {t['nome'].strip().lower(): t['id'] for t in tipos_bd}
            
            dados_parseados = []
            
            for idx, row in enumerate(reader, start=1):
                # Normaliza linha usando o mapa de headers original para garantir acesso correto
                row_lower = {}
                for header_clean, header_original in headers_map.items():
                    if header_original in row:
                        row_lower[header_clean] = row[header_original]

                titulo = row_lower.get('titulo', '').strip()
                tipo_nome = row_lower.get('tipo', '').strip()
                
                if not titulo:
                    continue 

                tipo_id = None
                if tipo_nome:
                    tipo_id = tipos_map.get(tipo_nome.lower())
                
                # Tratamento básico de aspas extras na descrição se vierem sujas do Excel
                descricao = row_lower.get('descricao', '').strip()
                
                dados_parseados.append({
                    'titulo': titulo,
                    'descricao': descricao,
                    'clausula_referencia': row_lower.get('clausula', '').strip(),
                    'tipo_obrigacao': tipo_id,
                    'tipo_obrigacao_nome': tipo_nome
                })
            
            return JsonResponse({'status': 'success', 'data': dados_parseados})

        except UnicodeDecodeError:
            return JsonResponse({'status': 'error', 'message': 'O arquivo não está em UTF-8. Salve como "CSV UTF-8" no Excel.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Erro ao processar linha {reader.line_num if "reader" in locals() else "?"}: {str(e)}'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Formulário inválido.'}, status=400)

