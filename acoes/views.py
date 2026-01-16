from core.views import ModernListView, ModernCreateView, ModernUpdateView, ModernDeleteView
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from .models import Acao, ChecklistItem
from django.urls import reverse_lazy
from .forms import AcaoForm, ChecklistItemFormSet
from instrumentos.models import Instrumento, Obrigacao
from django.http import JsonResponse


# Endpoint AJAX para obrigações (usado na criação de Ações)
def get_obrigacoes_por_instrumento(request):
    instrumento_id = request.GET.get('instrumento_id')
    if not instrumento_id:
        return JsonResponse({'obrigacoes': []})

    obrigacoes = Obrigacao.objects.filter(instrumento_id=instrumento_id).values('id', 'titulo')
    return JsonResponse({'obrigacoes': list(obrigacoes)})


class AcaoListView(ModernListView):
    """
    Lista as Ações (nível de execução vinculado à Obrigação).
    """
    model = Acao
    template_name = 'acoes/acao_list.html'
    icon = "bi bi-lightning-charge"
    create_url = 'acao_create'
    search_fields = ['nome', 'descricao', 'obrigacao__titulo']

    def get_queryset(self):
        instrumento_id = self.request.GET.get('instrumento')
        obrigacao_id = self.request.GET.get('obrigacao')

        queryset = Acao.objects.all()

        if instrumento_id:
            queryset = queryset.filter(obrigacao__instrumento_id=instrumento_id)
        if obrigacao_id:
            queryset = queryset.filter(obrigacao_id=obrigacao_id)

        return queryset.order_by('data_inicio', 'prioridade', 'nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instrumento_id = self.request.GET.get('instrumento')

        context['instrumentos'] = Instrumento.objects.all()
        context['obrigacoes'] = Obrigacao.objects.filter(instrumento_id=instrumento_id) if instrumento_id else Obrigacao.objects.all()
        try:
            context['instrumento_selecionado'] = int(instrumento_id) if instrumento_id else None
        except (ValueError, TypeError):
            context['instrumento_selecionado'] = None

        try:
            context['obrigacao_selecionada'] = int(self.request.GET.get('obrigacao')) if self.request.GET.get('obrigacao') else None
        except (ValueError, TypeError):
            context['obrigacao_selecionada'] = None

        return context


class AcaoCreateView(ModernCreateView):
    model = Acao
    form_class = AcaoForm
    success_url = reverse_lazy('acao_list')
    template_name = 'acoes/acao_form.html'

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
        
        if form.is_valid() and checklist_formset.is_valid():
            self.object = form.save()
            checklist_formset.instance = self.object
            checklist_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AcaoUpdateView(ModernUpdateView):
    model = Acao
    form_class = AcaoForm
    success_url = reverse_lazy('acao_list')
    template_name = 'acoes/acao_form.html'

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

        if form.is_valid() and checklist_formset.is_valid():
            self.object = form.save()
            checklist_formset.instance = self.object
            checklist_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AcaoDeleteView(ModernDeleteView):
    model = Acao
    success_url = reverse_lazy('acao_list')


# Calendário de Ações
class AcaoCalendarioView(TemplateView):
    template_name = 'acoes/acoes_calendario.html'


def acoes_json(request):
    """Retorna as ações em formato JSON para o FullCalendar"""
    acoes = Acao.objects.all()
    eventos = []

    for a in acoes:
        eventos.append({
            "id": a.id,
            "title": a.nome,
            "start": a.data_inicio.isoformat(),
            "end": a.data_fim.isoformat(),
            "color": cor_status(a.status),
            "extendedProps": {
                "responsavel": a.responsavel.get_full_name() or a.responsavel.username,
                "obrigacao": a.obrigacao.titulo,
                "status": a.get_status_display(),
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
