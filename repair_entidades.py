import os
import sys

def repair_entidade_form():
    path = r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\entidades\forms.py'
    content = """from django import forms
from .models import Entidade

class EntidadeForm(forms.ModelForm):
    class Meta:
        model = Entidade
        fields = '__all__'
        widgets = {
            'cnpj': forms.TextInput(attrs={'placeholder': '00.000.000/0000-00'}),
            'cep': forms.TextInput(attrs={'placeholder': '00000-000'}),
        }

    def __init__(self, *args, **kwargs):
        self.readonly = kwargs.pop('readonly', False)
        super().__init__(*args, **kwargs)
        if self.readonly:
            for field in self.fields.values():
                field.disabled = True
"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Reparação: entidades/forms.py corrigido.")

def repair_entidade_views():
    path = r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\entidades\views.py'
    content = """from django.contrib.auth.mixins import PermissionRequiredMixin
from core.views import ModernListView, ModernCreateView, ModernUpdateView, ModernDeleteView
from .models import Entidade
from .forms import EntidadeForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

class EntidadeListView(PermissionRequiredMixin, ModernListView):
    permission_required = 'entidades.view_entidade'
    model = Entidade
    template_name = 'entidades/entidade_list_v2.html'
    icon = "bi bi-building"
    subtitle = "Gerencie Concessionárias, Permissionárias e Entidades Reguladas"
    create_url = 'entidade_create'
    search_fields = ['razao_social', 'nome_fantasia', 'cnpj']

class EntidadeCreateView(PermissionRequiredMixin, ModernCreateView):
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
    permission_required = 'entidades.delete_entidade'
    model = Entidade
    success_url = reverse_lazy('entidade_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('entidades.delete_entidade'):
            messages.error(request, "Você não tem permissão para excluir registros.")
            return redirect('entidade_list')
        return super().dispatch(request, *args, **kwargs)
"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Reparação: entidades/views.py corrigido.")

if __name__ == "__main__":
    repair_entidade_form()
    repair_entidade_views()
    print("Reparação concluída com sucesso.")
