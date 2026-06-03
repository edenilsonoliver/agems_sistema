"""
Mixins para controle de permissões em Class-Based Views
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied


class PerfilRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin que restringe acesso baseado em perfis
    
    Uso:
        class MinhaView(PerfilRequiredMixin, ListView):
            perfis_permitidos = [0, 1, 2]  # Admin, Diretoria, Assessoria
            ...
    """
    perfis_permitidos = []
    
    def test_func(self):
        return self.request.user.perfil in self.perfis_permitidos
    
    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para acessar esta página.')
        raise PermissionDenied


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin que restringe acesso apenas para Admin
    
    Uso:
        class MinhaView(AdminRequiredMixin, ListView):
            ...
    """
    def test_func(self):
        return self.request.user.perfil == 0
    
    def handle_no_permission(self):
        messages.error(self.request, 'Acesso restrito a administradores.')
        raise PermissionDenied


class DiretoriaOuSuperiorMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin que permite acesso para Admin e Diretoria
    
    Uso:
        class MinhaView(DiretoriaOuSuperiorMixin, ListView):
            ...
    """
    def test_func(self):
        return self.request.user.perfil in [0, 1]
    
    def handle_no_permission(self):
        messages.error(self.request, 'Acesso restrito a administradores e diretoria.')
        raise PermissionDenied


class PodeCriarUsuarioMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin que verifica se usuário pode criar outros usuários
    
    Uso:
        class UsuarioCreateView(PodeCriarUsuarioMixin, CreateView):
            ...
    """
    def test_func(self):
        return self.request.user.pode_criar_usuario()
    
    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para criar usuários.')
        raise PermissionDenied


class PodeEditarEntidadeMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin que verifica se usuário pode editar entidades
    
    Uso:
        class EntidadeCreateView(PodeEditarEntidadeMixin, CreateView):
            ...
    """
    def test_func(self):
        return self.request.user.pode_editar_entidade()
    
    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para editar entidades.')
        raise PermissionDenied


class PodeEditarInstrumentoMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin que verifica se usuário pode editar instrumentos
    
    Uso:
        class InstrumentoCreateView(PodeEditarInstrumentoMixin, CreateView):
            ...
    """
    def test_func(self):
        return self.request.user.pode_editar_instrumento()
    
    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para editar instrumentos.')
        raise PermissionDenied


class NaoVisualizadorMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin que bloqueia visualizadores de criar/editar
    
    Uso:
        class AlgoCreateView(NaoVisualizadorMixin, CreateView):
            ...
    """
    def test_func(self):
        return self.request.user.perfil != 5
    
    def handle_no_permission(self):
        messages.error(self.request, 'Visualizadores não podem criar ou editar conteúdo.')
        raise PermissionDenied


class DatasetManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin que restringe o acesso apenas para usuários com perfil de Dataset Manager (is_dataset_manager=True)
    ou Administradores do sistema (perfil 0).
    """
    def test_func(self):
        return getattr(self.request.user, 'is_dataset_manager', False) or self.request.user.perfil == 0
    
    def handle_no_permission(self):
        messages.error(self.request, 'Acesso restrito ao perfil de Dataset Manager.')
        raise PermissionDenied


class VerificaSenhaTemporariaMixin(LoginRequiredMixin):
    """
    Mixin que redireciona para troca de senha se senha for temporária
    
    Uso:
        class DashboardView(VerificaSenhaTemporariaMixin, TemplateView):
            ...
    """
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.senha_temporaria:
            # Permitir acesso apenas à página de troca de senha
            if request.path not in ['/trocar-senha/', '/logout/', '/password_change/', '/password_change/done/']:
                messages.warning(
                    request,
                    'Você está usando uma senha temporária. Por favor, altere sua senha antes de continuar.'
                )
                return redirect('password_change')
        return super().dispatch(request, *args, **kwargs)


def get_diretoria_filter(user, prefix=''):
    """
    Função utilitária que retorna um Q-filter de isolamento por diretoria.

    Reutilizável em qualquer view ou queryset. O 'prefix' define a cadeia
    de lookups até o campo 'diretoria' do modelo alvo. Exemplos:
      - prefix=''                              → Instrumento.diretoria
      - prefix='instrumento__'                 → Obrigacao → instrumento → diretoria
      - prefix='obrigacao__instrumento__'      → Acao → obrigacao → instrumento → diretoria
      - prefix='contrato__'                    → ValorIndicador → contrato → diretoria

    Retorna None para Admin (sem restrição) ou queryset vazio (sem diretoria configurada).
    """
    from django.db.models import Q
    
    if not user or not user.is_authenticated:
        return Q(pk__in=[])

    if user.perfil == 0:
        # Admin: sem restrição — retorna None para indicar "não filtrar"
        return None

    diretoria_field = f'{prefix}diretoria'

    if user.perfil == 1:
        # Diretor: filtra pela sua diretoria
        if user.diretoria:
            return Q(**{diretoria_field: user.diretoria})

    elif user.perfil in [2, 3, 4]:
        # Assessor/Coordenador/Executor: filtra rigidamente pela Subunidade
        # Com Múltiplas Subunidades: O usuário vê o objeto se a sua subunidade estiver na lista de gestoras.
        if user.subunidade:
            return Q(**{f'{prefix}subunidades': user.subunidade})
        elif user.diretoria:
            # Fallback apenas para diretoria se o usuário não tiver subunidade (ex: Assessor Geral)
            return Q(**{diretoria_field: user.diretoria})

    elif user.perfil == 5:
        # Visualizador: filtra pelas diretorias autorizadas
        diretorias = user.diretorias_visualizacao.all()
        if diretorias.exists():
            return Q(**{f'{prefix}diretoria__in': diretorias})

    # Sem diretoria configurada: retorna filtro impossível (nenhum resultado)
    return Q(pk__in=[])


def verifica_acesso_unidade(user, obj):
    """
    Verifica se o usuário tem acesso a um objeto específico (Instrumento ou Ação).
    Considera Diretoria e Subunidade (múltiplas) conforme o perfil.
    """
    if not user or not user.is_authenticated:
        return False

    if user.perfil == 0:  # Admin
        return True
    
    # Extrair diretoria e subunidades do objeto
    from instrumentos.models import Instrumento
    from acoes.models import Acao
    
    obj_diretoria = None
    obj_subunidades = None
    
    if isinstance(obj, Instrumento):
        obj_diretoria = obj.diretoria
        obj_subunidades = obj.subunidades
    elif isinstance(obj, Acao):
        # Ação -> Obrigação -> Instrumento
        try:
            instrumento = obj.obrigacao.instrumento
            obj_diretoria = instrumento.diretoria
            obj_subunidades = instrumento.subunidades
        except AttributeError:
            return False
    else:
        obj_diretoria = getattr(obj, 'diretoria', None)
        obj_subunidades = getattr(obj, 'subunidades', None)

    if user.perfil == 1:  # Diretor
        return user.diretoria == obj_diretoria

    if user.perfil in [2, 3, 4]:  # Assessor, Coordenador, Executor
        if user.subunidade:
            # Se o usuário tem subunidade, ele acessa se a subunidade dele estiver entre as gestoras
            if obj_subunidades:
                try:
                    return obj_subunidades.filter(pk=user.subunidade.pk).exists()
                except (ValueError, TypeError):
                    return False
            return False
        return user.diretoria == obj_diretoria

    if user.perfil == 5:  # Visualizador
        if obj_diretoria:
            return user.diretorias_visualizacao.filter(pk=obj_diretoria.pk).exists()
    
    return False


def verifica_acesso_diretoria(user, obj_diretoria):
    """MANTIDO POR COMPATIBILIDADE MAS RECOMENDA-SE verifica_acesso_unidade"""
    if not user or not user.is_authenticated:
        return False
        
    if user.perfil == 0:
        return True
    if user.perfil == 1:
        return user.diretoria == obj_diretoria
    if user.perfil in [2, 3, 4]:
        user_diretoria = user.subunidade.diretoria if user.subunidade else user.diretoria
        return user_diretoria == obj_diretoria
    if user.perfil == 5:
        return user.diretorias_visualizacao.filter(pk=obj_diretoria.pk).exists()
    return False


class FiltrarPorDiretoriaMixin:
    """
    Mixin que filtra queryset baseado na diretoria do usuário.
    Usa get_diretoria_filter() internamente.

    Uso:
        class MinhaListView(FiltrarPorDiretoriaMixin, ListView):
            diretoria_lookup_prefix = ''  # default: campo 'diretoria' direto
            ...
    """
    # Subclasses podem sobrescrever este atributo para definir o prefixo de lookup
    diretoria_lookup_prefix = ''

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        q_filter = get_diretoria_filter(user, prefix=self.diretoria_lookup_prefix)

        if q_filter is None:
            # Admin: sem filtro
            return queryset
        return queryset.filter(q_filter)

