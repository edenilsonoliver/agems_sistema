from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Q

from .forms import UsuarioCreateForm, UsuarioUpdateForm
from .mixins import (
    PodeCriarUsuarioMixin, 
    FiltrarPorDiretoriaMixin,
    VerificaSenhaTemporariaMixin
)

User = get_user_model()


class UsuarioListView(VerificaSenhaTemporariaMixin, FiltrarPorDiretoriaMixin, ListView):
    """Lista usuários com filtro baseado no perfil do usuário logado"""
    model = User
    template_name = 'components/list_view.html'
    context_object_name = 'usuarios'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Usuários',
            'subtitle': 'Gerencie as contas de acesso do sistema',
            'icon': 'bi bi-people',
            'create_url': 'usuario_create' if self.request.user.pode_criar_usuario() else None,
            'can_create': self.request.user.pode_criar_usuario(),
        })
        return context
    
    def get_queryset(self):
        """Filtra usuários baseado no perfil do usuário logado"""
        queryset = User.objects.select_related('diretoria', 'subunidade').all()
        user = self.request.user
        
        # Admin vê todos
        if user.perfil == 0:
            pass  # Não aplica filtro
        
        # Diretoria vê usuários da sua diretoria
        elif user.perfil == 1 and user.diretoria:
            queryset = queryset.filter(
                Q(diretoria=user.diretoria) | 
                Q(subunidade__diretoria=user.diretoria)
            )
        
        # Assessoria e Coordenação veem usuários da sua subunidade
        elif user.perfil in [2, 3] and user.subunidade:
            queryset = queryset.filter(subunidade=user.subunidade)
        
        # Usuário Comum e Visualizador não podem ver lista de usuários
        else:
            return User.objects.none()
        
        return queryset.order_by('first_name', 'last_name')


class UsuarioCreateView(VerificaSenhaTemporariaMixin, PodeCriarUsuarioMixin, CreateView):
    """Cria novo usuário com formulário customizado"""
    model = User
    form_class = UsuarioCreateForm
    template_name = 'components/form_view.html'
    success_url = reverse_lazy('usuario_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Novo Usuário',
            'subtitle': 'Preencha os dados abaixo para cadastrar um novo usuário',
            'icon': 'bi bi-person-plus',
            'list_url': 'usuario_list',
            'form_title': 'Novo Usuário',
            'module_name': 'Usuários',
        })
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request_user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Usuário "{self.object.get_full_name()}" criado com sucesso!'
        )
        return response


class UsuarioUpdateView(VerificaSenhaTemporariaMixin, LoginRequiredMixin, UpdateView):
    """Edita usuário existente com controle de permissões"""
    model = User
    form_class = UsuarioUpdateForm
    template_name = 'components/form_view.html'
    success_url = reverse_lazy('usuario_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Editar Usuário',
            'subtitle': f'Atualize os dados de {self.object.get_full_name()}',
            'icon': 'bi bi-pencil-square',
            'list_url': 'usuario_list',
            'form_title': 'Editar Usuário',
            'module_name': 'Usuários',
        })
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request_user'] = self.request.user
        return kwargs
    
    def dispatch(self, request, *args, **kwargs):
        """Verifica se usuário pode editar este usuário específico"""
        self.object = self.get_object()
        
        # Verificar se pode editar este usuário
        if not request.user.pode_editar_usuario(self.object):
            messages.error(request, 'Você não tem permissão para editar este usuário.')
            return redirect('usuario_list')
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Usuário "{self.object.get_full_name()}" atualizado com sucesso!'
        )
        return response


class UsuarioDeleteView(VerificaSenhaTemporariaMixin, LoginRequiredMixin, DeleteView):
    """Exclui usuário com controle de permissões"""
    model = User
    template_name = 'components/confirm_delete.html'
    success_url = reverse_lazy('usuario_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Excluir Usuário',
            'subtitle': f'Confirme a exclusão de {self.object.get_full_name()}',
            'icon': 'bi bi-trash',
            'list_url': 'usuario_list',
        })
        return context
    
    def dispatch(self, request, *args, **kwargs):
        """Verifica se usuário pode excluir este usuário específico"""
        self.object = self.get_object()
        
        # Verificar se pode editar (e portanto excluir) este usuário
        if not request.user.pode_editar_usuario(self.object):
            messages.error(request, 'Você não tem permissão para excluir este usuário.')
            return redirect('usuario_list')
        
        # Impedir auto-exclusão
        if self.object == request.user:
            messages.error(request, 'Você não pode excluir sua própria conta.')
            return redirect('usuario_list')
        
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        nome_usuario = self.get_object().get_full_name()
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Usuário "{nome_usuario}" excluído com sucesso!')
        return response


# View adicional para gerenciar diretorias de visualização (apenas para perfil 5)
class UsuarioVisualizadorView(VerificaSenhaTemporariaMixin, LoginRequiredMixin, UpdateView):
    """View específica para configurar diretorias de visualização"""
    model = User
    fields = ['diretorias_visualizacao']
    template_name = 'usuarios/visualizador_form.html'
    success_url = reverse_lazy('usuario_list')
    
    def dispatch(self, request, *args, **kwargs):
        """Apenas admin pode configurar visualizadores"""
        if request.user.perfil != 0:
            messages.error(request, 'Apenas administradores podem configurar visualizadores.')
            return redirect('usuario_list')
        
        self.object = self.get_object()
        if self.object.perfil != 5:
            messages.error(request, 'Esta função é apenas para usuários com perfil Visualizador.')
            return redirect('usuario_list')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Configurar Visualizador',
            'subtitle': f'Defina as diretorias que {self.object.get_full_name()} pode visualizar',
            'icon': 'bi bi-eye',
            'list_url': 'usuario_list',
        })
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Diretorias de visualização configuradas para {self.object.get_full_name()}!'
        )
        return response
