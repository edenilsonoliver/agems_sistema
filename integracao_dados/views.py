import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from usuarios.mixins import DatasetManagerRequiredMixin
from .auth_service import AuthServiceError, renovar_token
from .dashboard_service import DashboardAcessoService
from .forms import (CredencialFonteForm, DashboardForm, DatasetForm,
                    EndpointForm, FonteDadosForm)
from .models import CredencialFonte, Dashboard, Dataset, Endpoint, FonteDados

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARDS ANALÍTICOS
# ══════════════════════════════════════════════════════════════════════════════

class DashboardListView(LoginRequiredMixin, ListView):
    """Lista todos os Dashboards aos quais o usuário tem acesso (via serviço RBAC)."""
    model = Dashboard
    template_name = 'integracao_dados/dashboard_list.html'
    context_object_name = 'dashboards'

    def get_queryset(self):
        qs = super().get_queryset().select_related('diretoria_proprietaria', 'criador')
        return [d for d in qs if DashboardAcessoService.pode_acessar(self.request.user, d)]


class DashboardDetailView(LoginRequiredMixin, DetailView):
    """Exibe um Dashboard e seus Widgets."""
    model = Dashboard
    template_name = 'integracao_dados/dashboard_detail.html'
    context_object_name = 'dashboard'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not DashboardAcessoService.pode_acessar(self.request.user, obj):
            raise PermissionDenied("Você não tem acesso a este dashboard analítico.")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['widgets'] = self.object.widgets.select_related('dataset').all()
        return context


class DashboardCreateView(DatasetManagerRequiredMixin, CreateView):
    model = Dashboard
    form_class = DashboardForm
    template_name = 'integracao_dados/dashboard_form.html'
    success_url = reverse_lazy('integracao_dados:dashboard_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module_name'] = 'Dashboards Analíticos'
        context['list_url'] = reverse_lazy('integracao_dados:dashboard_list')
        context['form_title'] = 'Criar Novo Dashboard'
        context['icon'] = 'bi bi-clipboard-data'
        return context

    def form_valid(self, form):
        form.instance.criador = self.request.user
        return super().form_valid(form)


class DashboardUpdateView(DatasetManagerRequiredMixin, UpdateView):
    model = Dashboard
    form_class = DashboardForm
    template_name = 'integracao_dados/dashboard_form.html'
    success_url = reverse_lazy('integracao_dados:dashboard_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module_name'] = 'Dashboards Analíticos'
        context['list_url'] = reverse_lazy('integracao_dados:dashboard_list')
        context['form_title'] = f'Editar Dashboard: {self.object.nome}'
        context['icon'] = 'bi bi-clipboard-data'
        return context


# ══════════════════════════════════════════════════════════════════════════════
# DATASETS
# ══════════════════════════════════════════════════════════════════════════════

class DatasetCreateView(DatasetManagerRequiredMixin, CreateView):
    model = Dataset
    form_class = DatasetForm
    template_name = 'integracao_dados/dataset_form.html'
    success_url = reverse_lazy('integracao_dados:dashboard_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module_name'] = 'Datasets'
        context['list_url'] = reverse_lazy('integracao_dados:dashboard_list')
        context['form_title'] = 'Criar Novo Dataset'
        context['icon'] = 'bi bi-database-add'
        return context

    def form_valid(self, form):
        form.instance.responsavel = self.request.user
        arquivo = self.request.FILES.get('arquivo_importacao')
        if arquivo:
            try:
                dados_json = json.loads(arquivo.read().decode('utf-8'))
                form.instance.dados = dados_json
            except Exception:
                messages.warning(self.request, "Arquivo JSON inválido. Os dados foram ignorados.")
        return super().form_valid(form)


class DatasetUpdateView(DatasetManagerRequiredMixin, UpdateView):
    model = Dataset
    form_class = DatasetForm
    template_name = 'integracao_dados/dataset_form.html'
    success_url = reverse_lazy('integracao_dados:dashboard_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module_name'] = 'Datasets'
        context['list_url'] = reverse_lazy('integracao_dados:dashboard_list')
        context['form_title'] = f'Editar Dataset: {self.object.nome}'
        context['icon'] = 'bi bi-database'
        return context


# ══════════════════════════════════════════════════════════════════════════════
# FONTES DE DADOS — Listagem, Criação, Edição, Dashboard de Detalhes
# ══════════════════════════════════════════════════════════════════════════════

class FonteDadosListView(DatasetManagerRequiredMixin, ListView):
    model = FonteDados
    template_name = 'integracao_dados/fontedados_list.html'
    context_object_name = 'fontes'

    def get_queryset(self):
        qs = super().get_queryset().select_related('diretoria')
        user = self.request.user
        if user.perfil == 0:
            return qs
        if user.diretoria:
            return qs.filter(diretoria=user.diretoria)
        return qs.none()


class FonteDadosCreateView(DatasetManagerRequiredMixin, CreateView):
    model = FonteDados
    form_class = FonteDadosForm
    template_name = 'integracao_dados/fontedados_form.html'

    def get_success_url(self):
        return reverse('integracao_dados:fontedados_manage', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module_name'] = 'Fontes de Dados'
        context['list_url'] = reverse_lazy('integracao_dados:fontedados_list')
        context['form_title'] = 'Cadastrar Nova Fonte de Dados'
        context['icon'] = 'bi bi-hdd-network'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        # Criar uma CredencialFonte vazia automaticamente para a nova fonte
        CredencialFonte.objects.get_or_create(fonte=self.object)
        messages.success(self.request, f'Fonte "{self.object.nome}" criada. Configure agora as credenciais e adicione os Endpoints.')
        return response





class FonteDadosManageView(DatasetManagerRequiredMixin, DetailView):
    """
    Dashboard unificado de gerenciamento da Fonte: abas de Configuração,
    Acesso/Credenciais e Endpoints.
    """
    model = FonteDados
    template_name = 'integracao_dados/fontedados_manage.html'
    context_object_name = 'fonte'

    def _has(self, val):
        return bool(val) and str(val).strip().lower() not in ('null', 'none', '')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fonte = self.object

        context['active_tab'] = kwargs.get('active_tab', 'config')
        context['has_endpoint_errors'] = kwargs.get('has_endpoint_errors', False)
        context['form_fonte'] = kwargs.get('form_fonte') or FonteDadosForm(instance=fonte)
        context['form_endpoint'] = kwargs.get('form_endpoint') or EndpointForm()
        context['endpoints'] = fonte.endpoints.all().order_by('nome')

        cred, _ = CredencialFonte.objects.get_or_create(fonte=fonte)
        context['credencial'] = cred
        
        def _s(val):
            if val is None or str(val).strip().lower() == 'null':
                return ''
            return str(val)

        initial_cred = {
            'usuario_api': _s(cred.usuario_api),
            'senha_api': '********' if self._has(cred.senha_api) else '',
            'api_key_header': _s(cred.api_key_header) or 'X-API-Key',
            'headers_customizados': json.dumps(cred.headers_customizados, indent=2) if cred.headers_customizados else '',
            'token_manual': _s(cred.token_atual),
        }
        context['form_cred'] = kwargs.get('form_cred') or CredencialFonteForm(initial=initial_cred)
        
        context['tem_usuario'] = self._has(cred.usuario_api)
        context['tem_senha'] = self._has(cred.senha_api)
        context['tem_token'] = self._has(cred.token_atual)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = request.POST.get('action')

        if action == 'save_config':
            form = FonteDadosForm(request.POST, instance=self.object)
            if form.is_valid():
                form.save()
                messages.success(request, '✅ Configuração da Fonte salva com sucesso.')
                return redirect(f"{reverse('integracao_dados:fontedados_manage', args=[self.object.pk])}#config")
            else:
                messages.error(request, '⚠️ Verifique os erros no formulário de configuração.')
                return self.render_to_response(self.get_context_data(active_tab='config', form_fonte=form))

        elif action == 'save_auth':
            cred, _ = CredencialFonte.objects.get_or_create(fonte=self.object)
            form = CredencialFonteForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                if cd.get('usuario_api'): cred.usuario_api = cd['usuario_api']
                if cd.get('senha_api') and cd['senha_api'] != '********': cred.senha_api = cd['senha_api']
                if cd.get('token_manual'): cred.token_atual = cd['token_manual']
                if cd.get('api_key_header'): cred.api_key_header = cd['api_key_header']
                if cd.get('headers_customizados') is not None: cred.headers_customizados = cd['headers_customizados']
                cred.save()
                messages.success(request, '🔐 Credenciais salvas com segurança.')

                estrategias_auto = ('jwt', 'oauth2', 'basic')
                pode_auto_auth = (
                    self.object.auth_url_relativa and
                    self.object.metodo_autenticacao in estrategias_auto and
                    cred.usuario_api and cred.senha_api
                )
                if pode_auto_auth:
                    try:
                        from .auth_service import renovar_token
                        token = renovar_token(self.object)
                        preview = f"{token[:20]}..." if len(token) > 20 else token
                        messages.success(request, f'✅ Conectado à API com sucesso! Token: <code>{preview}</code>')
                    except Exception as e:
                        messages.warning(request, f'⚠️ Conexão automática falhou: {str(e)}')
                
                return redirect(f"{reverse('integracao_dados:fontedados_manage', args=[self.object.pk])}#auth")
            else:
                messages.error(request, '⚠️ Verifique os erros no formulário de credenciais.')
                return self.render_to_response(self.get_context_data(active_tab='auth', form_cred=form))

        elif action == 'save_endpoint':
            form = EndpointForm(request.POST)
            if form.is_valid():
                ep = form.save(commit=False)
                ep.fonte = self.object
                ep.save()
                messages.success(request, '✅ Novo endpoint adicionado.')
                return redirect(f"{reverse('integracao_dados:fontedados_manage', args=[self.object.pk])}#endpoints")
            else:
                messages.error(request, '⚠️ Verifique os erros no formulário do endpoint.')
                return self.render_to_response(self.get_context_data(active_tab='endpoints', form_endpoint=form, has_endpoint_errors=True))

        return redirect('integracao_dados:fontedados_manage', pk=self.object.pk)


@login_required
def testar_conexao_view(request, pk):
    """Testa a conexão real com a API via requisição HTTP."""
    from django.utils import timezone
    import requests
    from .auth_service import renovar_token, montar_headers_autenticados

    if request.method != 'POST':
        return JsonResponse({'error': 'Apenas POST'}, status=405)
    
    fonte = get_object_or_404(FonteDados, pk=pk)
    status_code = 0
    mensagem = ""
    conectado = False

    try:
        if fonte.auth_url_relativa and fonte.metodo_autenticacao in ('jwt', 'oauth2', 'basic'):
            renovar_token(fonte)
            status_code = 200
            conectado = True
            mensagem = "Login efetuado e token obtido com sucesso."
        else:
            endpoint = fonte.endpoints.filter(ativo=True).first()
            if not endpoint:
                raise ValueError("Nenhum endpoint ativo para testar e nenhuma URL de login configurada.")
            
            headers = montar_headers_autenticados(fonte)
            if endpoint.headers_override:
                headers.update(endpoint.headers_override)
            
            url = fonte.url_base.rstrip('/') + '/' + endpoint.url_relativa.lstrip('/')
            
            if endpoint.metodo_http == 'GET':
                response = requests.get(url, headers=headers, params=endpoint.parametros_default, timeout=10)
            else:
                response = requests.post(url, headers=headers, json=endpoint.parametros_default, timeout=10)
            
            status_code = response.status_code
            conectado = (200 <= status_code < 300)
            mensagem = f"Teste no endpoint '{endpoint.nome}': HTTP {status_code}."
            
    except Exception as e:
        conectado = False
        status_code = getattr(e, 'status_code', 500) if hasattr(e, 'status_code') else 0
        mensagem = f"Erro na conexão: {str(e)}"
    
    fonte.ultimo_status_http = status_code
    fonte.ultimo_teste = timezone.now()
    fonte.mensagem_ultimo_teste = str(mensagem)
    fonte.save(update_fields=['ultimo_status_http', 'ultimo_teste', 'mensagem_ultimo_teste'])

    return JsonResponse({
        'conectado': conectado,
        'status_code': status_code,
        'mensagem': mensagem
    })


# ══════════════════════════════════════════════════════════════════════════════
# AUTH FLOW — Renovação automática de token via POST
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def renovar_token_view(request, fonte_pk):
    """
    Trigger manual do Auth Flow: chama auth_service.renovar_token()
    e redireciona de volta para o detalhe da Fonte com mensagem de status.
    """
    if not (getattr(request.user, 'is_dataset_manager', False) or request.user.perfil == 0):
        raise PermissionDenied("Acesso restrito a Gerentes de Dados.")

    if request.method != 'POST':
        return redirect('integracao_dados:fontedados_manage', pk=fonte_pk)

    fonte = get_object_or_404(FonteDados, pk=fonte_pk)

    try:
        token = renovar_token(fonte)
        # Mostra apenas os primeiros 20 chars do token por segurança
        preview = f"{token[:20]}..." if len(token) > 20 else token
        messages.success(request, f'✅ Token renovado com sucesso! Prévia: {preview}')
    except AuthServiceError as e:
        messages.error(request, f'❌ Falha na autenticação: {e}')
    except Exception as e:
        logger.exception(f"Erro inesperado ao renovar token da Fonte {fonte_pk}")
        messages.error(request, f'❌ Erro interno ao renovar token. Contate o administrador.')

    return redirect('integracao_dados:fontedados_manage', pk=fonte_pk)


# ══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS — CRUD atrelado a uma Fonte (1:N)
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def endpoint_criar(request, fonte_pk):
    """Cria um novo Endpoint vinculado a uma Fonte de Dados."""
    if not (getattr(request.user, 'is_dataset_manager', False) or request.user.perfil == 0):
        raise PermissionDenied("Acesso restrito a Gerentes de Dados.")

    fonte = get_object_or_404(FonteDados, pk=fonte_pk)

    if request.method == 'POST':
        form = EndpointForm(request.POST)
        if form.is_valid():
            endpoint = form.save(commit=False)
            endpoint.fonte = fonte
            endpoint.save()
            messages.success(request, f'Endpoint "{endpoint.nome}" criado com sucesso.')
            return redirect('integracao_dados:fontedados_manage', pk=fonte_pk)
    else:
        form = EndpointForm()

    return render(request, 'integracao_dados/endpoint_form.html', {
        'form': form,
        'fonte': fonte,
        'titulo': f'Novo Endpoint — {fonte.nome}',
        # Variáveis para form_view.html
        'module_name': fonte.nome,
        'list_url': reverse('integracao_dados:fontedados_manage', kwargs={'pk': fonte_pk}),
        'form_title': f'Novo Endpoint',
        'icon': 'bi bi-diagram-3',
    })


@login_required
def endpoint_editar(request, pk):
    """Edita um Endpoint existente."""
    if not (getattr(request.user, 'is_dataset_manager', False) or request.user.perfil == 0):
        raise PermissionDenied("Acesso restrito a Gerentes de Dados.")

    endpoint = get_object_or_404(Endpoint, pk=pk)
    fonte = endpoint.fonte

    if request.method == 'POST':
        form = EndpointForm(request.POST, instance=endpoint)
        if form.is_valid():
            form.save()
            messages.success(request, f'Endpoint "{endpoint.nome}" atualizado.')
            return redirect('integracao_dados:fontedados_manage', pk=fonte.pk)
    else:
        form = EndpointForm(instance=endpoint)

    return render(request, 'integracao_dados/endpoint_form.html', {
        'form': form,
        'fonte': fonte,
        'endpoint': endpoint,
        'titulo': f'Editar Endpoint — {endpoint.nome}',
        # Variáveis para form_view.html
        'module_name': fonte.nome,
        'list_url': reverse('integracao_dados:fontedados_manage', kwargs={'pk': fonte.pk}),
        'form_title': f'Editar: {endpoint.nome}',
        'icon': 'bi bi-diagram-3',
    })


# ══════════════════════════════════════════════════════════════════════════════
# API INTERNA — Dados de Dataset para Chart.js
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def dataset_dados_api(request, dataset_id):
    """Retorna os dados JSON de um Dataset para widgets (Chart.js)."""
    dataset = get_object_or_404(Dataset, id=dataset_id)

    user = request.user
    if not (getattr(user, 'is_dataset_manager', False) or user.perfil == 0):
        if not user.diretoria or user.diretoria_id != dataset.diretoria_proprietaria_id:
            raise PermissionDenied("Acesso restrito ao dataset.")

    return JsonResponse({
        'nome': dataset.nome,
        'schema': dataset.schema,
        'dados': dataset.dados
    })
