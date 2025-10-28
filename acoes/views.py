from core.views import ModernListView, ModernCreateView, ModernUpdateView, ModernDeleteView
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Tarefa, Acao, ChecklistItem
from django.urls import reverse_lazy
from .forms import AcaoForm, ChecklistItemFormSet
from instrumentos.models import Instrumento, Obrigacao
from django.http import JsonResponse
from django.forms import inlineformset_factory

# Formset para checklist
ChecklistFormSet = inlineformset_factory(
    Tarefa,
    ChecklistItem,
    fields=('nome', 'concluido'),
    extra=1,
    can_delete=True
)


class TarefaListView(ModernListView):
    model = Tarefa
    template_name = 'acoes/tarefa_list.html'
    icon = "bi bi-check2-square"
    create_url = 'tarefa_create'
    search_fields = ['nome', 'descricao']

    def get_queryset(self):
        instrumento_id = self.request.GET.get('instrumento')
        obrigacao_id = self.request.GET.get('obrigacao')

        queryset = Tarefa.objects.all()

        if instrumento_id:
            queryset = queryset.filter(acao__instrumento_id=instrumento_id)
        if obrigacao_id:
            queryset = queryset.filter(acao__obrigacao_id=obrigacao_id)

        queryset = queryset.order_by('data_inicio', 'prioridade', 'nome')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instrumento_id = self.request.GET.get('instrumento')

        context['instrumentos'] = Instrumento.objects.all()
        context['obrigacoes'] = Obrigacao.objects.filter(instrumento_id=instrumento_id) if instrumento_id else Obrigacao.objects.all()
        context['instrumento_selecionado'] = instrumento_id
        context['obrigacao_selecionada'] = self.request.GET.get('obrigacao')

        return context


# Endpoint AJAX para obrigações
def get_obrigacoes_por_instrumento(request):
    instrumento_id = request.GET.get('instrumento_id')
    if not instrumento_id:
        return JsonResponse({'obrigacoes': []})

    obrigacoes = Obrigacao.objects.filter(instrumento_id=instrumento_id).values('id', 'titulo')
    return JsonResponse({'obrigacoes': list(obrigacoes)})


class TarefaCreateView(ModernCreateView):
    model = Tarefa
    fields = '__all__'
    success_url = reverse_lazy('tarefa_list')
    template_name = 'acoes/tarefa_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['checklist_formset'] = ChecklistItemFormSet(
                self.request.POST,
                prefix='checklist_itens'
            )
        else:
            context['checklist_formset'] = ChecklistItemFormSet(
                prefix='checklist_itens'
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        checklist_formset = context['checklist_formset']
        self.object = form.save(commit=False)

        if checklist_formset.is_valid():
            self.object.save()
            checklist_formset.instance = self.object
            checklist_formset.save()
            return super().form_valid(form)
        else:
            # Renderiza novamente com erros
            context['form'] = form
            return self.render_to_response(context)


class TarefaUpdateView(ModernUpdateView):
    model = Tarefa
    fields = ['nome', 'descricao', 'acao', 'responsavel', 'executores', 'status',
              'percentual_cumprido', 'data_inicio', 'data_fim', 'data_conclusao',
              'tarefas_predecessoras', 'prioridade', 'observacoes']
    success_url = reverse_lazy('tarefa_list')
    template_name = 'acoes/tarefa_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['checklist_formset'] = ChecklistItemFormSet(
                self.request.POST,
                instance=self.object,
                prefix='checklist_itens'
            )
        else:
            context['checklist_formset'] = ChecklistItemFormSet(
                instance=self.object,
                prefix='checklist_itens'
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        checklist_formset = context['checklist_formset']
        self.object = form.save(commit=False)

        if checklist_formset.is_valid():
            self.object.save()
            # Salvar M2M fields
            form.save_m2m()
            checklist_formset.instance = self.object
            checklist_formset.save()
            return super().form_valid(form)
        else:
            # Renderiza novamente com erros
            context['form'] = form
            return self.render_to_response(context)


class TarefaDeleteView(ModernDeleteView):
    model = Tarefa
    success_url = reverse_lazy('tarefa_list')


# Classes de Ações
class AcaoListView(ModernListView):
    model = Acao
    template_name = 'acoes/acao_list.html'
    icon = "bi bi-lightning"
    create_url = 'acao_create'
    search_fields = ['nome', 'descricao']


class AcaoCreateView(ModernCreateView):
    model = Acao
    form_class = AcaoForm
    success_url = reverse_lazy('acao_list')


class AcaoUpdateView(ModernUpdateView):
    model = Acao
    form_class = AcaoForm
    success_url = reverse_lazy('acao_list')


class AcaoDeleteView(ModernDeleteView):
    model = Acao
    success_url = reverse_lazy('acao_list')


# Calendário de Tarefas
class TarefaCalendarioView(TemplateView):
    template_name = 'acoes/tarefas_calendario.html'


def tarefas_json(request):
    """Retorna as tarefas em formato JSON para o FullCalendar"""
    tarefas = Tarefa.objects.all()
    eventos = []

    for t in tarefas:
        eventos.append({
            "id": t.id,
            "title": t.nome,
            "start": t.data_inicio.isoformat(),
            "end": t.data_fim.isoformat(),
            "color": cor_status(t.status),
            "extendedProps": {
                "responsavel": t.responsavel.get_full_name() or t.responsavel.username,
                "acao": t.acao.nome,
                "status": t.get_status_display(),
            }
        })
    return JsonResponse(eventos, safe=False)


def cor_status(status):
    """Define a cor com base no status"""
    cores = {
        'a_iniciar': '#f57c00',       # laranja
        'em_andamento': '#1976d2',    # azul
        'atrasado': '#c62828',        # vermelho
        'em_validacao': '#6a1b9a',    # roxo
        'finalizado': '#2e7d32',      # verde
    }
    return cores.get(status, '#607d8b')

