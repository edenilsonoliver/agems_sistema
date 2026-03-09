from django import forms
from django.db.models import Count
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.forms import inlineformset_factory
from core.views import ModernListView, ModernCreateView, ModernUpdateView, ModernDeleteView
from core.models import TipoInstrumento, Diretoria, TipoObrigacao
from .models import Instrumento, Obrigacao, ArquivoInstrumento
import csv
import io
import json
from .forms import InstrumentoForm, ObrigacaoForm, ImportacaoObrigacoesForm
from django.contrib import messages
from usuarios.mixins import get_diretoria_filter, verifica_acesso_diretoria

logger = logging.getLogger(__name__)

# Formset para obrigações inline
ObrigacaoFormSet = inlineformset_factory(
    Instrumento,
    Obrigacao,
    form=ObrigacaoForm,
    extra=0,
    can_delete=True
)

class InstrumentoListView(PermissionRequiredMixin, ModernListView):

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Você não possui permissão para acessar esta funcionalidade ou excluir este registro.")
            return redirect(getattr(self, 'success_url', 'dashboard'))
        return super().handle_no_permission()

    permission_required = 'instrumentos.view_instrumento'
    model = Instrumento
    template_name = 'instrumentos/instrumento_list.html'
    icon = "bi bi-file-earmark-text"
    subtitle = "Gerencie Contratos, Convênios, Acordos de Cooperação, etc"
    create_url = 'instrumento_create'
    search_fields = ['numero', 'objeto', 'nup']

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('tipo_instrumento', 'diretoria').prefetch_related('entidades')
        # RBAC: filtrar por diretoria do usuário logado
        user = self.request.user
        q_filter = get_diretoria_filter(user, prefix='')
        if q_filter is not None:
            queryset = queryset.filter(q_filter)
        return queryset

class InstrumentoCreateView(PermissionRequiredMixin, ModernCreateView):

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Você não possui permissão para acessar esta funcionalidade ou excluir este registro.")
            return redirect(getattr(self, 'success_url', 'dashboard'))
        return super().handle_no_permission()

    permission_required = 'instrumentos.view_instrumento'
    model = Instrumento
    form_class = InstrumentoForm
    template_name = 'instrumentos/instrumento_form.html'

    def get_readonly(self):
        return self.request.user.perfil not in [0, 1, 2]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['readonly'] = self.get_readonly()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['readonly'] = self.get_readonly()
        if self.request.POST:
            context['formset'] = ObrigacaoFormSet(self.request.POST, prefix='obrigacoes')
        else:
            context['formset'] = ObrigacaoFormSet(prefix='obrigacoes')
        
        if self.get_readonly():
            for form in context['formset'].forms:
                for field in form.fields.values():
                    field.disabled = True
        
        context['arquivos'] = []
        return context

    def form_valid(self, form):
        if self.get_readonly():
             messages.error(self.request, "Você não tem permissão para salvar alterações.")
             return self.render_to_response(self.get_context_data(form=form))
        
        # RBAC: forçar diretoria do usuário para perfis não-Admin
        user = self.request.user
        if user.perfil != 0:
            inst_diretoria = (
                user.subunidade.diretoria
                if getattr(user, 'subunidade', None) and user.subunidade.diretoria
                else user.diretoria
            )
            if inst_diretoria:
                form.instance.diretoria = inst_diretoria

        context = self.get_context_data()
        formset = context['formset']

        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            
            # Adicionar a subunidade do usuário automaticamente se for perfil restrito
            if user.perfil in [2, 3, 4] and getattr(user, 'subunidade', None):
                self.object.subunidades.add(user.subunidade)
                
            formset.instance = self.object
            formset.save()
            messages.success(self.request, 'Instrumento criado com sucesso!')
            return redirect('instrumento_edit', pk=self.object.pk)
        else:
            return self.form_invalid(form)

class InstrumentoUpdateView(PermissionRequiredMixin, ModernUpdateView):

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Você não possui permissão para acessar esta funcionalidade ou excluir este registro.")
            return redirect(getattr(self, 'success_url', 'dashboard'))
        return super().handle_no_permission()

    permission_required = 'instrumentos.view_instrumento'
    model = Instrumento
    form_class = InstrumentoForm
    template_name = 'instrumentos/instrumento_form.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        from usuarios.mixins import verifica_acesso_unidade
        if not verifica_acesso_unidade(request.user, obj):
            messages.error(request, 'Você não tem permissão para acessar este instrumento.')
            return redirect('instrumento_list')
        return super().dispatch(request, *args, **kwargs)

    def get_readonly(self):
        return self.request.user.perfil not in [0, 1, 2]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['readonly'] = self.get_readonly()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['readonly'] = self.get_readonly()
        if self.request.POST:
            context['formset'] = ObrigacaoFormSet(self.request.POST, instance=self.object, prefix='obrigacoes')
        else:
            queryset = self.object.obrigacoes.annotate(acoes_count=Count('acoes'))
            context['formset'] = ObrigacaoFormSet(instance=self.object, queryset=queryset, prefix='obrigacoes')
        
        if self.get_readonly():
            for form in context['formset'].forms:
                for field in form.fields.values():
                    field.disabled = True
                    
        context['arquivos'] = getattr(self.object, 'arquivos', []).all() if hasattr(self.object, 'arquivos') else []
        return context

    def post(self, request, *args, **kwargs):
        if self.get_readonly():
             self.object = self.get_object()
             messages.error(self.request, "Você não tem permissão para salvar alterações.")
             return self.render_to_response(self.get_context_data(form=self.get_form()))
             
        self.object = self.get_object()
        form = self.get_form()
        queryset = self.object.obrigacoes.annotate(acoes_count=Count('acoes'))
        formset = ObrigacaoFormSet(self.request.POST, instance=self.object, queryset=queryset, prefix='obrigacoes')

        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, 'Instrumento atualizado com sucesso!')
            return redirect('instrumento_edit', pk=self.object.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form, formset=formset))

class InstrumentoDeleteView(PermissionRequiredMixin, ModernDeleteView):

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Você não possui permissão para acessar esta funcionalidade ou excluir este registro.")
            return redirect(getattr(self, 'success_url', 'dashboard'))
        return super().handle_no_permission()

    permission_required = 'instrumentos.delete_instrumento'
    model = Instrumento
    success_url = reverse_lazy('instrumento_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        from usuarios.mixins import verifica_acesso_unidade
        if not verifica_acesso_unidade(request.user, obj):
            messages.error(request, 'Você não tem permissão para acessar este instrumento.')
            return redirect('instrumento_list')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError as e:
            protected_objects = e.protected_objects
            obrigacoes = [obj for obj in protected_objects if isinstance(obj, Obrigacao)]
            if obrigacoes:
                messages.error(self.request, f'Não é possível excluir: {len(obrigacoes)} obrigação(ões) vinculada(s).')
            else:
                messages.error(self.request, f'Não é possível excluir: {len(protected_objects)} registro(s) vinculado(s).')
            return redirect(self.success_url)

@require_POST
@permission_required('instrumentos.add_tipoinstrumento', raise_exception=True)
def tipo_instrumento_create(request):
    nome = request.POST.get('nome')
    if nome:
        tipo = TipoInstrumento.objects.create(nome=nome)
        return JsonResponse({'success': True, 'id': tipo.id, 'nome': tipo.nome})
    return JsonResponse({'success': False, 'error': 'Nome não fornecido'})

@require_POST
@permission_required('core.add_diretoria', raise_exception=True)
def diretoria_create(request):
    sigla = request.POST.get('sigla')
    nome = request.POST.get('nome')
    if sigla and nome:
        diretoria = Diretoria.objects.create(sigla=sigla, nome=nome)
        return JsonResponse({'success': True, 'id': diretoria.id})
    return JsonResponse({'success': False, 'error': 'Dados incompletos'})

@require_POST
@permission_required('instrumentos.change_instrumento', raise_exception=True)
def arquivo_upload(request, instrumento_id):
    import magic
    import zipfile
    instrumento = get_object_or_404(Instrumento, pk=instrumento_id)
    arquivo = request.FILES.get('arquivo')
    nome = request.POST.get('nome_arquivo', '')
    if not arquivo:
        return JsonResponse({'success': False, 'error': 'Nenhum arquivo enviado.'})
    ext = os.path.splitext(arquivo.name)[1].lower()
    allowed_extensions = ['.pdf', '.docx', '.xlsx']
    if ext not in allowed_extensions:
        return JsonResponse({'success': False, 'error': f'Extensão {ext} não permitida.'})
    ALLOWED_MIMES = {'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}
    try:
        initial_pos = arquivo.tell()
        mime_type = magic.from_buffer(arquivo.read(2048), mime=True)
        arquivo.seek(initial_pos)
        if mime_type not in ALLOWED_MIMES:
            return JsonResponse({'success': False, 'error': f'Tipo inválido ({mime_type}).'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'Erro ao validar MIME.'})
    arquivo_obj = ArquivoInstrumento.objects.create(instrumento=instrumento, arquivo=arquivo, nome_arquivo=nome or arquivo.name)
    return JsonResponse({'success': True, 'id': arquivo_obj.id, 'nome': arquivo_obj.nome_arquivo, 'url': arquivo_obj.arquivo.url})

@require_POST
@permission_required('instrumentos.change_instrumento', raise_exception=True)
def arquivo_delete(request, arquivo_id):
    arquivo = get_object_or_404(ArquivoInstrumento, pk=arquivo_id)
    try:
        arquivo.arquivo.delete(save=False)
        arquivo.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Erro ao excluir arquivo: {str(e)}")
        return JsonResponse({'success': False})

@require_POST
@permission_required('instrumentos.add_obrigacao', raise_exception=True)
def importar_obrigacoes_csv(request):
    form = ImportacaoObrigacoesForm(request.POST, request.FILES)
    if form.is_valid():
        arquivo = request.FILES['arquivo_csv']
        try:
            content = arquivo.read().decode('utf-8-sig')
            decoded_file = content.splitlines()
            delimitador = ';' if ';' in decoded_file[0] else ','
            reader = csv.DictReader(decoded_file, delimiter=delimitador, quotechar='"')
            tipos_bd = list(TipoObrigacao.objects.values('id', 'nome'))
            tipos_map = {t['nome'].strip().lower(): t['id'] for t in tipos_bd}
            headers_map = {h.strip().lower(): h for h in reader.fieldnames}
            dados_parseados = []
            for row in reader:
                row_lower = {k.strip().lower(): v for k, v in row.items()}
                titulo = row_lower.get('titulo', '').strip()
                if not titulo: continue
                dados_parseados.append({
                    'titulo': titulo,
                    'descricao': row_lower.get('descricao', '').strip(),
                    'clausula_referencia': row_lower.get('clausula', '').strip(),
                    'tipo_obrigacao': tipos_map.get(row_lower.get('tipo', '').strip().lower())
                })
            return JsonResponse({'status': 'success', 'data': dados_parseados})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Formulário inválido.'}, status=400)
