from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView


User = get_user_model()


class UsuarioListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'components/list_view.html'  # usa o layout moderno global
    context_object_name = 'usuarios'
    extra_context = {
        'title': 'Usuários',
        'subtitle': 'Gerencie as contas de acesso do sistema',
        'icon': 'bi bi-people',
        'create_url': 'usuario_create',
    }


class UsuarioCreateView(LoginRequiredMixin, CreateView):
    model = User
    fields = ['username', 'first_name', 'last_name', 'email', 'subunidade', 'is_active']
    template_name = 'components/form_view.html'  # reaproveita layout moderno
    success_url = reverse_lazy('usuario_list')

    extra_context = {
        'title': 'Novo Usuário',
        'subtitle': 'Preencha os dados abaixo para cadastrar um novo usuário',
        'icon': 'bi bi-person-plus',
        'list_url': 'usuario_list',
    }


class UsuarioUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['username', 'first_name', 'last_name', 'email', 'subunidade', 'is_active']
    template_name = 'components/form_view.html'
    success_url = reverse_lazy('usuario_list')

    extra_context = {
        'title': 'Editar Usuário',
        'subtitle': 'Atualize os dados do usuário selecionado',
        'icon': 'bi bi-pencil-square',
        'list_url': 'usuario_list',
    }


class UsuarioDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'components/confirm_delete.html'
    success_url = reverse_lazy('usuario_list')

    extra_context = {
        'title': 'Excluir Usuário',
        'subtitle': 'Confirme a exclusão do usuário selecionado',
        'icon': 'bi bi-trash',
        'list_url': 'usuario_list',
    }
