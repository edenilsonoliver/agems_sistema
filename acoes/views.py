from core.views import ModernListView, ModernCreateView, ModernUpdateView, ModernDeleteView
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Tarefa, Acao, ChecklistItem
from django.urls import reverse_lazy
from .forms import AcaoForm
from instrumentos.models import Instrumento

from core.views import ModernListView, ModernCreateView, ModernUpdateView, ModernDeleteView
from django.http import JsonResponse
from django.urls import reverse_lazy
from instrumentos.models import Instrumento, Obrigacao
from .models import Tarefa
from .forms import AcaoForm
from acoes.models import Tarefa
from .forms import ChecklistItemFormSet
from django.forms import inlineformset_factory

# --- CALENDÁRIO DE TAREFAS (FullCalendar.js) ---
from django.views.generic import TemplateView
from django.http import JsonResponse

# logo abaixo das importações e antes das views de tarefa
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
    search_fields = ['titulo', 'descricao']

    def get_queryset(self):
        from acoes.models import Tarefa

        instrumento_id = self.request.GET.get('instrumento')
        obrigacao_id = self.request.GET.get('obrigacao')

        queryset = Tarefa.objects.all()

        if instrumento_id:
            queryset = queryset.filter(acao__instrumento_id=instrumento_id)
        if obrigacao_id:
            queryset = queryset.filter(acao_id=obrigacao_id)

        queryset = queryset.order_by('id')

        print("DEBUG >>> Ordem aplicada:", list(queryset.values_list('id', flat=True)))
        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instrumento_id = self.request.GET.get('instrumento')

        context['instrumentos'] = Instrumento.objects.all()
        context['obrigacoes'] = Obrigacao.objects.filter(instrumento_id=instrumento_id) if instrumento_id else Obrigacao.objects.all()
        context['instrumento_selecionado'] = instrumento_id
        context['obrigacao_selecionada'] = self.request.GET.get('obrigacao')

        return context


# --- Endpoint AJAX ---
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

        print("---- DEBUG FORMSET POST ----")
        print("TOTAL_FORMS:", self.request.POST.get('checklist_itens-TOTAL_FORMS'))
        print("INITIAL_FORMS:", self.request.POST.get('checklist_itens-INITIAL_FORMS'))

        for k in sorted(self.request.POST.keys()):
            if k.startswith('checklist_itens-'):
                print(k, "=>", self.request.POST.get(k))
        print("---- END DEBUG ----")

        # DEBUG fino: confere IDs esperados x recebidos
        try:
            pref = 'checklist_itens'
            total = int(self.request.POST.get(f'{pref}-TOTAL_FORMS') or 0)
            initial = int(self.request.POST.get(f'{pref}-INITIAL_FORMS') or 0)
            print(f"[CHK] total_forms={total} initial_forms={initial}")

            for i in range(total):
                id_val   = self.request.POST.get(f'{pref}-{i}-id')
                nome_val = self.request.POST.get(f'{pref}-{i}-nome')
                conc_val = self.request.POST.get(f'{pref}-{i}-concluido')
                print(f"[CHK] i={i} id={id_val!r} nome={nome_val!r} concluido={conc_val!r}")
        except Exception as e:
            print("[CHK] erro ao inspecionar POST:", e)

        if checklist_formset.is_valid():
            self.object.save()
            checklist_formset.instance = self.object
            checklist_formset.save()
            return super().form_valid(form)
        else:
            # Mantém a tela com os erros do formset, sem “limpar” o formulário
            print("⚠️ FORMSET INVÁLIDO EM:", self.__class__.__name__)
            print("ERROS GERAIS:", checklist_formset.non_form_errors())
            for i, f in enumerate(checklist_formset.forms):
                print(f"  → Form {i} errors:", f.errors)
            context['form'] = form
            return self.render_to_response(context)


class TarefaUpdateView(ModernUpdateView):
    model = Tarefa
    fields = ['nome', 'descricao', 'acao', 'responsavel', 'status',
              'percentual_cumprido', 'data_inicio', 'data_fim', 'prioridade']
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

        print("---- DEBUG FORMSET POST ----")
        print("TOTAL_FORMS:", self.request.POST.get('checklist_itens-TOTAL_FORMS'))
        print("INITIAL_FORMS:", self.request.POST.get('checklist_itens-INITIAL_FORMS'))

        for k in sorted(self.request.POST.keys()):
            if k.startswith('checklist_itens-'):
                print(k, "=>", self.request.POST.get(k))
        print("---- END DEBUG ----")

        # DEBUG fino: confere IDs esperados x recebidos
        try:
            pref = 'checklist_itens'
            total = int(self.request.POST.get(f'{pref}-TOTAL_FORMS') or 0)
            initial = int(self.request.POST.get(f'{pref}-INITIAL_FORMS') or 0)
            print(f"[CHK] total_forms={total} initial_forms={initial}")

            for i in range(total):
                id_val   = self.request.POST.get(f'{pref}-{i}-id')
                nome_val = self.request.POST.get(f'{pref}-{i}-nome')
                conc_val = self.request.POST.get(f'{pref}-{i}-concluido')
                print(f"[CHK] i={i} id={id_val!r} nome={nome_val!r} concluido={conc_val!r}")
        except Exception as e:
            print("[CHK] erro ao inspecionar POST:", e)

        if checklist_formset.is_valid():
            self.object.save()
            checklist_formset.instance = self.object
            checklist_formset.save()
            return super().form_valid(form)
        else:
            print("⚠️ FORMSET INVÁLIDO EM:", self.__class__.__name__)
            print("ERROS GERAIS:", checklist_formset.non_form_errors())
            for i, f in enumerate(checklist_formset.forms):
                print(f"  → Form {i} errors:", f.errors)
            context['form'] = form
            return self.render_to_response(context)


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
