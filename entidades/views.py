from core.views import ModernListView, ModernCreateView, ModernUpdateView, ModernDeleteView
from .models import Entidade
from django.urls import reverse_lazy


class EntidadeListView(ModernListView):
    model = Entidade
    template_name = 'entidades/entidade_list.html'  # Template específico
    icon = "bi bi-building"
    create_url = 'entidade_create'
    search_fields = ['razao_social', 'nome_fantasia', 'cnpj']


class EntidadeCreateView(ModernCreateView):
    model = Entidade
    fields = '__all__'
    success_url = reverse_lazy('entidade_list')


class EntidadeUpdateView(ModernUpdateView):
    model = Entidade
    fields = '__all__'
    success_url = reverse_lazy('entidade_list')


class EntidadeDeleteView(ModernDeleteView):
    model = Entidade
    success_url = reverse_lazy('entidade_list')

