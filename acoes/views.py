from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from core.views import ModernListView, ModernCreateView, ModernUpdateView, ModernDeleteView
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.db.models import Q
from .models import Acao, ChecklistItem
from django.urls import reverse_lazy
from .forms import AcaoForm, ChecklistItemFormSet, AcaoDocumentoFormSet, AcaoFotoFormSet
from instrumentos.models import Instrumento, Obrigacao
from django.http import JsonResponse


# Endpoint AJAX para obrigações (usado na criação de Ações)
def get_obrigacoes_por_instrumento(request):
    instrumento_id = request.GET.get('instrumento_id')
    if not instrumento_id:
        return JsonResponse({'obrigacoes': []})

    obrigacoes = Obrigacao.objects.filter(instrumento_id=instrumento_id).values('id', 'titulo')
    return JsonResponse({'obrigacoes': list(obrigacoes)})


class AcaoListView(PermissionRequiredMixin, ModernListView):
    """
    Lista as Ações (nível de execução vinculado à Obrigação).
    """
    permission_required = 'acoes.view_acao'
    model = Acao
    template_name = 'acoes/acao_list.html'
    icon = "bi bi-lightning-charge"
    create_url = 'acao_create'
    search_fields = ['nome', 'descricao', 'obrigacao__titulo']

    def get_queryset(self):
        instrumento_id = self.request.GET.get('instrumento')
        obrigacao_id = self.request.GET.get('obrigacao')
        user = self.request.user

        # OTIMIZAÇÃO: Carregamento antecipado de chaves estrangeiras
        queryset = Acao.objects.select_related('responsavel', 'obrigacao', 'obrigacao__instrumento')

        # FILTRO DE ESCOPO: Técnicos veem apenas suas ações (Responsável ou Executor)
        if user.perfil in [3, 4]:
            queryset = queryset.filter(Q(responsavel=user) | Q(executores=user)).distinct()
        
        # Admin e Gestor veem tudo (base queryset já é all())

        if instrumento_id:
            queryset = queryset.filter(obrigacao__instrumento_id=instrumento_id)
        if obrigacao_id:
            queryset = queryset.filter(obrigacao_id=obrigacao_id)

        return queryset.order_by('data_inicio', 'prioridade', 'nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instrumento_id = self.request.GET.get('instrumento')

        context['instrumentos'] = Instrumento.objects.all()
        # OTIMIZAÇÃO: Se filtrar obrigações para o dropdown, carregue apenas o necessário
        context['obrigacoes'] = Obrigacao.objects.filter(instrumento_id=instrumento_id).only('id', 'titulo') if instrumento_id else Obrigacao.objects.all().only('id', 'titulo')
        try:
            context['instrumento_selecionado'] = int(instrumento_id) if instrumento_id else None
        except (ValueError, TypeError):
            context['instrumento_selecionado'] = None

        try:
            context['obrigacao_selecionada'] = int(self.request.GET.get('obrigacao')) if self.request.GET.get('obrigacao') else None
        except (ValueError, TypeError):
            context['obrigacao_selecionada'] = None

        return context


class AcaoCreateView(PermissionRequiredMixin, ModernCreateView):
    permission_required = 'acoes.add_acao'
    model = Acao
    form_class = AcaoForm
    success_url = reverse_lazy('acao_list')
    template_name = 'acoes/acao_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['checklist_formset'] = ChecklistItemFormSet(self.request.POST, prefix='checklist_itens')
            context['docs_formset'] = AcaoDocumentoFormSet(self.request.POST, self.request.FILES, prefix='docs')
            context['fotos_formset'] = AcaoFotoFormSet(self.request.POST, self.request.FILES, prefix='fotos')
        else:
            context['checklist_formset'] = ChecklistItemFormSet(prefix='checklist_itens')
            context['docs_formset'] = AcaoDocumentoFormSet(prefix='docs')
            context['fotos_formset'] = AcaoFotoFormSet(prefix='fotos')
        return context

    def save_assets(self, acao, docs_formset, fotos_formset):
        """Helper para salvar ativos na criação"""
        try:
            # Documentos
            docs = docs_formset.save(commit=False)
            for doc in docs:
                doc.acao = acao
                doc.usuario = self.request.user
                doc.save()
            for obj in docs_formset.deleted_objects:
                obj.delete()

            # Fotos
            fotos = fotos_formset.save(commit=False)
            for foto in fotos:
                foto.acao = acao
                foto.usuario = self.request.user
                foto.save()
            for obj in fotos_formset.deleted_objects:
                obj.delete()
        except Exception as e:
            from django.contrib import messages
            messages.error(self.request, f"Erro ao salvar arquivos: {str(e)}")
            print(f"CRITICAL ERROR SAVING ASSETS (CREATE): {str(e)}")

    def form_valid(self, form):
        context = self.get_context_data()
        checklist_formset = context['checklist_formset']
        docs_formset = context['docs_formset']
        fotos_formset = context['fotos_formset']
        
        is_valid = all([
            form.is_valid(),
            checklist_formset.is_valid(),
            docs_formset.is_valid(),
            fotos_formset.is_valid()
        ])

        if is_valid:
            # Validar checklist obrigatório (mínimo 1 item válido)
            itens_validos = 0
            for c_form in checklist_formset:
                if c_form.cleaned_data and not c_form.cleaned_data.get('DELETE', False):
                    if c_form.cleaned_data.get('nome', '').strip():
                        itens_validos += 1
            
            if itens_validos == 0:
                messages.error(
                    self.request,
                    'É obrigatório adicionar pelo menos 1 item no checklist de tarefas operativas.'
                )
                return self.render_to_response(self.get_context_data(form=form))
            self.object = form.save()
            
            # Checklist
            checklist_formset.instance = self.object
            checklist_formset.save()
            
            # Ativos
            self.save_assets(self.object, docs_formset, fotos_formset)

            messages.success(self.request, f'Ação "{self.object.nome}" criada com sucesso!')
            return super().form_valid(form)
        else:
            # Tratamento de Erros Amigável (UX)
            # Extrair mensagens de erro dos formsets para exibir no topo como toast/alert
            
            # Erros de Documentos
            for form_erro in docs_formset.errors:
                if form_erro:
                    for campo, msgs in form_erro.items():
                         for msg in msgs:
                             # Se o erro for no campo arquivo, mostra mensagem específica
                             prefixo = "Erro no arquivo: " if campo == 'arquivo' else ""
                             messages.error(self.request, f"{prefixo}{msg}")

            # Erros de Fotos
            for form_erro in fotos_formset.errors:
                if form_erro:
                    for campo, msgs in form_erro.items():
                        for msg in msgs:
                            messages.error(self.request, f"Erro na foto: {msg}")

            if not docs_formset.errors and not fotos_formset.errors:
                 messages.error(self.request, "Verifique os dados do formulário.")
                 
            return self.render_to_response(self.get_context_data(form=form))


class AcaoUpdateView(PermissionRequiredMixin, ModernUpdateView):
    permission_required = 'acoes.change_acao'
    model = Acao
    form_class = AcaoForm
    success_url = reverse_lazy('acao_list')
    template_name = 'acoes/acao_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['checklist_formset'] = ChecklistItemFormSet(self.request.POST, instance=self.object, prefix='checklist_itens')
            context['docs_formset'] = AcaoDocumentoFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix='docs')
            context['fotos_formset'] = AcaoFotoFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix='fotos')
        else:
            context['checklist_formset'] = ChecklistItemFormSet(instance=self.object, prefix='checklist_itens')
            context['docs_formset'] = AcaoDocumentoFormSet(instance=self.object, prefix='docs')
            context['fotos_formset'] = AcaoFotoFormSet(instance=self.object, prefix='fotos')
        return context

    def save_assets(self, acao, docs_formset, fotos_formset):
        """Helper para salvar documentos e fotos com injeção de usuário"""
        try:
            # Documentos
            docs = docs_formset.save(commit=False)
            for doc in docs:
                doc.acao = acao
                if not doc.pk:
                    doc.usuario = self.request.user
                doc.save()
            for obj in docs_formset.deleted_objects:
                obj.delete()

            # Fotos
            fotos = fotos_formset.save(commit=False)
            for foto in fotos:
                foto.acao = acao
                if not foto.pk:
                    foto.usuario = self.request.user
                foto.save()
            for obj in fotos_formset.deleted_objects:
                obj.delete()
        except Exception as e:
            messages.error(self.request, f"Erro ao salvar arquivos: {str(e)}")

    def form_valid(self, form):
        context = self.get_context_data()
        checklist_formset = context['checklist_formset']
        docs_formset = context['docs_formset']
        fotos_formset = context['fotos_formset']



        is_valid = all([
            form.is_valid(),
            checklist_formset.is_valid(),
            docs_formset.is_valid(),
            fotos_formset.is_valid()
        ])

        if is_valid:
            # Validar checklist obrigatório (mínimo 1 item válido)
            itens_validos = 0
            for c_form in checklist_formset:
                if c_form.cleaned_data and not c_form.cleaned_data.get('DELETE', False):
                    if c_form.cleaned_data.get('nome', '').strip():
                        itens_validos += 1
            
            if itens_validos == 0:
                messages.error(
                    self.request,
                    'É obrigatório adicionar pelo menos 1 item no checklist de tarefas operativas.'
                )
                return self.render_to_response(self.get_context_data(form=form))
            self.object = form.save()
            
            # Checklist
            checklist_formset.instance = self.object
            checklist_formset.save()
            
            # Ativos (Docs e Fotos)
            self.save_assets(self.object, docs_formset, fotos_formset)

            messages.success(self.request, f'Ação "{self.object.nome}" atualizada com sucesso!')
            return super().form_valid(form)
        else:
            # Tratamento de Erros Amigável (UX) - UpdateView
            
            # Erros de Documentos
            for form_erro in docs_formset.errors:
                if form_erro:
                    for campo, msgs in form_erro.items():
                         for msg in msgs:
                             prefixo = "Erro no arquivo: " if campo == 'arquivo' else ""
                             messages.error(self.request, f"{prefixo}{msg}")

            # Erros de Fotos
            for form_erro in fotos_formset.errors:
                if form_erro:
                    for campo, msgs in form_erro.items():
                        for msg in msgs:
                            messages.error(self.request, f"Erro na foto: {msg}")

            if not docs_formset.errors and not fotos_formset.errors:
                 messages.error(self.request, "Verifique os dados do formulário.")

            return self.render_to_response(self.get_context_data(form=form))


class AcaoDeleteView(PermissionRequiredMixin, ModernDeleteView):
    permission_required = 'acoes.delete_acao'
    model = Acao
    success_url = reverse_lazy('acao_list')


# Calendário de Ações
class AcaoCalendarioView(PermissionRequiredMixin, TemplateView):
    permission_required = 'acoes.view_acao'
    template_name = 'acoes/acoes_calendario.html'


@permission_required('acoes.view_acao', raise_exception=True)
def acoes_json(request):
    """Retorna as ações em formato JSON para o FullCalendar"""
    user = request.user
    
    queryset = Acao.objects.select_related('responsavel', 'obrigacao')
    
    if user.perfil in [3, 4]:
        queryset = queryset.filter(Q(responsavel=user) | Q(executores=user)).distinct()
        
    acoes = queryset.all()
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
