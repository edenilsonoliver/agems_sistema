from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

User = get_user_model()

class UsuarioListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'usuarios/usuario_list.html'
    context_object_name = 'usuarios'


class UsuarioCreateView(LoginRequiredMixin, CreateView):
    model = User
    fields = ['username', 'first_name', 'last_name', 'email', 'subunidade', 'is_active']
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuario_list')


class UsuarioUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['username', 'first_name', 'last_name', 'email', 'subunidade', 'is_active']
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuario_list')


class UsuarioDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'usuarios/usuario_confirm_delete.html'
    success_url = reverse_lazy('usuario_list')