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


class FiltrarPorDiretoriaMixin:
    """
    Mixin que filtra queryset baseado na diretoria do usuário
    
    Uso:
        class MinhaListView(FiltrarPorDiretoriaMixin, ListView):
            ...
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admin vê tudo
        if user.perfil == 0:
            return queryset
        
        # Diretoria vê apenas sua diretoria
        if user.perfil == 1 and user.diretoria:
            if hasattr(queryset.model, 'diretoria'):
                return queryset.filter(diretoria=user.diretoria)
            elif hasattr(queryset.model, 'subunidade'):
                return queryset.filter(subunidade__diretoria=user.diretoria)
        
        # Assessoria, Coordenação e Usuário Comum veem apenas sua subunidade
        if user.perfil in [2, 3, 4] and user.subunidade:
            if hasattr(queryset.model, 'subunidade'):
                return queryset.filter(subunidade=user.subunidade)
            elif hasattr(queryset.model, 'diretoria'):
                return queryset.filter(diretoria=user.subunidade.diretoria)
        
        # Visualizador vê diretorias permitidas
        if user.perfil == 5:
            diretorias = user.diretorias_visualizacao.all()
            if hasattr(queryset.model, 'diretoria'):
                return queryset.filter(diretoria__in=diretorias)
            elif hasattr(queryset.model, 'subunidade'):
                return queryset.filter(subunidade__diretoria__in=diretorias)
        
        return queryset.none()

