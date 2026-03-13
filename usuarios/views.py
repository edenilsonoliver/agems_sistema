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
    FiltrarPorDiretoriaMixin
)

User = get_user_model()


class UsuarioListView(LoginRequiredMixin, ListView):
    """Lista usuários com filtro baseado no perfil do usuário logado"""
    model = User
    template_name = 'usuarios/usuario_list.html'
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
        """Filtra usuários baseado no perfil do usuário logado e filtros de busca"""
        user = self.request.user
        queryset = User.objects.select_related('diretoria', 'subunidade').all()
        
        # 1. Filtro de Permissão (Quem pode ver o quê)
        if user.is_superuser or user.perfil == 0:
            # Admin vê todos
            pass
        elif user.perfil == 1 and user.diretoria:
            # Diretoria vê usuários da sua diretoria
            queryset = queryset.filter(
                Q(diretoria=user.diretoria) | 
                Q(subunidade__diretoria=user.diretoria)
            )
        elif user.perfil in [2, 3] and user.subunidade:
            # Assessoria e Coordenação veem usuários da sua subunidade
            queryset = queryset.filter(subunidade=user.subunidade)
        else:
            # Usuário Comum e Visualizador não podem ver lista de usuários
            return User.objects.none()
        
        # 2. Filtros de Busca e Interface
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(username__icontains=q) |
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(email__icontains=q)
            )
            
        perfil_filtro = self.request.GET.get('perfil')
        if perfil_filtro:
            queryset = queryset.filter(perfil=perfil_filtro)
            
        status_filtro = self.request.GET.get('status')
        if status_filtro == 'ativo':
            queryset = queryset.filter(is_active=True)
        elif status_filtro == 'inativo':
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('first_name', 'last_name')


class UsuarioCreateView(PodeCriarUsuarioMixin, CreateView):
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


class UsuarioUpdateView(LoginRequiredMixin, UpdateView):
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


class UsuarioDeleteView(LoginRequiredMixin, DeleteView):
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
class UsuarioVisualizadorView(LoginRequiredMixin, UpdateView):
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

class UsuarioPerfilView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UsuarioUpdateForm
    template_name = 'usuarios/usuario_perfil.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Meu Perfil',
            'subtitle': 'Visualize e atualize seus dados cadastrais',
            'icon': 'bi bi-person-circle',
            'form_title': 'Dados do Meu Perfil',
        })
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Usuários comuns não podem alterar o próprio perfil ou diretoria
        if self.request.user.perfil != 0:
            if 'perfil' in form.fields: form.fields['perfil'].disabled = True
            if 'diretoria' in form.fields: form.fields['diretoria'].disabled = True
            if 'subunidade' in form.fields: form.fields['subunidade'].disabled = True
            if 'username' in form.fields: form.fields['username'].disabled = True
        return form

    def form_valid(self, form):
        messages.success(self.request, "Perfil atualizado com sucesso!")
        return super().form_valid(form)
