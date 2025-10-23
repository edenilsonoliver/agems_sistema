from core.views import ModernListView, ModernCreateView, ModernUpdateView, ModernDeleteView
from .models import Tarefa, Acao
from django.urls import reverse_lazy


class TarefaListView(ModernListView):
    model = Tarefa
    template_name = 'acoes/tarefa_list.html'
    icon = "bi bi-check2-square"
    create_url = 'tarefa_create'
    search_fields = ['titulo', 'descricao']


class TarefaCreateView(ModernCreateView):
    model = Tarefa
    fields = '__all__'
    success_url = reverse_lazy('tarefa_list')


class TarefaUpdateView(ModernUpdateView):
    model = Tarefa
    fields = '__all__'
    success_url = reverse_lazy('tarefa_list')


class TarefaDeleteView(ModernDeleteView):
    model = Tarefa
    success_url = reverse_lazy('tarefa_list')



class AcaoListView(ModernListView):
    model = Acao
    template_name = 'acoes/acao_list.html'
    icon = "bi bi-lightning"
    create_url = 'acao_create'
    search_fields = ['titulo', 'descricao']


class AcaoCreateView(ModernCreateView):
    model = Acao
    fields = '__all__'
    success_url = reverse_lazy('acao_list')


class AcaoUpdateView(ModernUpdateView):
    model = Acao
    fields = '__all__'
    success_url = reverse_lazy('acao_list')


class AcaoDeleteView(ModernDeleteView):
    model = Acao
    success_url = reverse_lazy('acao_list')

