from django.contrib.auth.mixins import PermissionRequiredMixin
from core.views import ModernListView, ModernCreateView, ModernUpdateView, ModernDeleteView
from .models import Entidade
from .forms import EntidadeForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

class EntidadeListView(PermissionRequiredMixin, ModernListView):

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Você não possui permissão para acessar esta funcionalidade ou excluir este registro.")
            return redirect(getattr(self, 'success_url', 'dashboard'))
        return super().handle_no_permission()

    permission_required = 'entidades.view_entidade'
    model = Entidade
    template_name = 'entidades/entidade_list_v2.html'
    icon = "bi bi-building"
    subtitle = "Gerencie Concessionárias, Permissionárias e Entidades Reguladas"
    create_url = 'entidade_create'
    search_fields = ['razao_social', 'nome_fantasia', 'cnpj']

class EntidadeCreateView(PermissionRequiredMixin, ModernCreateView):

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Você não possui permissão para acessar esta funcionalidade ou excluir este registro.")
            return redirect(getattr(self, 'success_url', 'dashboard'))
        return super().handle_no_permission()

    permission_required = 'entidades.view_entidade'
    model = Entidade
    form_class = EntidadeForm
    template_name = 'entidades/entidade_form.html'
    success_url = reverse_lazy('entidade_list')

    def get_readonly(self):
        return self.request.user.perfil not in [0, 1, 2]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['readonly'] = self.get_readonly()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['readonly'] = self.get_readonly()
        return context

    def form_valid(self, form):
        if self.get_readonly():
             messages.error(self.request, "Você não tem permissão para salvar alterações.")
             return self.render_to_response(self.get_context_data(form=form))
        return super().form_valid(form)

class EntidadeUpdateView(PermissionRequiredMixin, ModernUpdateView):

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Você não possui permissão para acessar esta funcionalidade ou excluir este registro.")
            return redirect(getattr(self, 'success_url', 'dashboard'))
        return super().handle_no_permission()

    permission_required = 'entidades.view_entidade'
    model = Entidade
    form_class = EntidadeForm
    template_name = 'entidades/entidade_form.html'
    success_url = reverse_lazy('entidade_list')

    def get_readonly(self):
        return self.request.user.perfil not in [0, 1, 2]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['readonly'] = self.get_readonly()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['readonly'] = self.get_readonly()
        return context

    def form_valid(self, form):
        if self.get_readonly():
             messages.error(self.request, "Você não tem permissão para salvar alterações.")
             return self.render_to_response(self.get_context_data(form=form))
        return super().form_valid(form)

class EntidadeDeleteView(PermissionRequiredMixin, ModernDeleteView):

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Você não possui permissão para acessar esta funcionalidade ou excluir este registro.")
            return redirect(getattr(self, 'success_url', 'dashboard'))
        return super().handle_no_permission()

    permission_required = 'entidades.delete_entidade'
    model = Entidade
    success_url = reverse_lazy('entidade_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('entidades.delete_entidade'):
            messages.error(request, "Você não tem permissão para excluir registros.")
            return redirect('entidade_list')
        return super().dispatch(request, *args, **kwargs)
