"""
Decorators para controle de permissões baseado em perfis de usuário
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def perfil_required(perfis):
    """
    Decorator que restringe acesso a views baseado no perfil do usuário
    
    Uso:
        @perfil_required([0, 1, 2])  # Apenas Admin, Diretoria e Assessoria
        def minha_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            if request.user.perfil not in perfis:
                messages.error(request, 'Você não tem permissão para acessar esta página.')
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def admin_required(view_func):
    """
    Decorator que restringe acesso apenas para Admin (perfil 0)
    
    Uso:
        @admin_required
        def minha_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if request.user.perfil != 0:
            messages.error(request, 'Acesso restrito a administradores.')
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapped_view


def diretoria_ou_superior(view_func):
    """
    Decorator que permite acesso para Admin e Diretoria (perfis 0 e 1)
    
    Uso:
        @diretoria_ou_superior
        def minha_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if request.user.perfil not in [0, 1]:
            messages.error(request, 'Acesso restrito a administradores e diretoria.')
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapped_view


def pode_criar_usuario(view_func):
    """
    Decorator que verifica se usuário pode criar outros usuários
    Perfis permitidos: 0 (Admin), 1 (Diretoria), 2 (Assessoria), 3 (Coordenação)
    
    Uso:
        @pode_criar_usuario
        def criar_usuario_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if not request.user.pode_criar_usuario():
            messages.error(request, 'Você não tem permissão para criar usuários.')
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapped_view


def pode_editar_entidade(view_func):
    """
    Decorator que verifica se usuário pode criar/editar entidades
    Perfis permitidos: 0 (Admin), 1 (Diretoria), 2 (Assessoria)
    
    Uso:
        @pode_editar_entidade
        def editar_entidade_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if not request.user.pode_editar_entidade():
            messages.error(request, 'Você não tem permissão para editar entidades.')
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapped_view


def pode_editar_instrumento(view_func):
    """
    Decorator que verifica se usuário pode criar/editar instrumentos
    Perfis permitidos: 0 (Admin), 1 (Diretoria), 2 (Assessoria)
    Coordenação NÃO pode editar instrumentos
    
    Uso:
        @pode_editar_instrumento
        def editar_instrumento_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if not request.user.pode_editar_instrumento():
            messages.error(request, 'Você não tem permissão para editar instrumentos.')
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapped_view


def nao_visualizador(view_func):
    """
    Decorator que bloqueia acesso de visualizadores (perfil 5)
    Visualizadores só podem ver, não podem criar/editar
    
    Uso:
        @nao_visualizador
        def criar_algo_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if request.user.perfil == 5:
            messages.error(request, 'Visualizadores não podem criar ou editar conteúdo.')
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapped_view


def verifica_senha_temporaria(view_func):
    """
    Decorator que redireciona usuário para troca de senha se estiver usando senha temporária
    
    Uso:
        @verifica_senha_temporaria
        def dashboard_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if request.user.senha_temporaria:
            # Permitir acesso apenas à página de troca de senha
            if request.path not in ['/trocar-senha/', '/logout/', '/password_change/']:
                messages.warning(
                    request,
                    'Você está usando uma senha temporária. Por favor, altere sua senha antes de continuar.'
                )
                return redirect('password_change')
        return view_func(request, *args, **kwargs)
    return wrapped_view

