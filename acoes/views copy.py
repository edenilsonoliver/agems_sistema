from core.views import ModernListView, ModernCreateView, ModernUpdateView, ModernDeleteView
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Tarefa, Acao
from django.urls import reverse_lazy
from .forms import AcaoForm
from instrumentos.models import Instrumento

class TarefaListView(ModernListView):
    model = Tarefa
    template_name = 'acoes/tarefa_list.html'
    icon = "bi bi-check2-square"
    create_url = 'tarefa_create'
    search_fields = ['titulo', 'descricao']

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-id')
        instrumento_id = self.request.GET.get('instrumento')
        acao_id = self.request.GET.get('acao')

        if instrumento_id:
            queryset = queryset.filter(acao__instrumento_id=instrumento_id)
        if acao_id:
            queryset = queryset.filter(acao_id=acao_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from instrumentos.models import Instrumento
        from .models import Acao

        instrumento_id = self.request.GET.get('instrumento')
        context['instrumentos'] = Instrumento.objects.all()
        context['acoes'] = Acao.objects.filter(instrumento_id=instrumento_id) if instrumento_id else Acao.objects.none()
        context['instrumento_selecionado'] = instrumento_id
        context['acao_selecionada'] = self.request.GET.get('acao')
        return context

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


#Classes de Ações
class AcaoListView(ModernListView):
    model = Acao
    template_name = 'acoes/acao_list.html'
    icon = "bi bi-lightning"
    create_url = 'acao_create'
    search_fields = ['titulo', 'descricao']


class AcaoCreateView(ModernCreateView):
    model = Acao
    form_class = AcaoForm  # substitui fields='__all__'
    success_url = reverse_lazy('acao_list')

class AcaoUpdateView(ModernUpdateView):
    model = Acao
    form_class = AcaoForm  # substitui fields='__all__'
    success_url = reverse_lazy('acao_list')

class AcaoDeleteView(ModernDeleteView):
    model = Acao
    success_url = reverse_lazy('acao_list')

