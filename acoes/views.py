from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required, login_required
from core.views import ModernListView, ModernCreateView, ModernUpdateView, ModernDeleteView
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.db.models import Q, Case, When, IntegerField
from .models import Acao, ChecklistItem, AcaoMarcador, AcaoFoto
from django.urls import reverse_lazy
from .forms import (
    AcaoForm, ChecklistItemFormSet, AcaoDocumentoFormSet, 
    AcaoFotoFormSet, ConformidadeFormSet
)

from instrumentos.models import Instrumento, Obrigacao
from entidades.models import Entidade
from django.http import JsonResponse
from core.models import TipoAcao
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


# Ordem canônica dos tipos de ação conforme definido pelo cliente
TIPO_ACAO_ORDEM = [
    'Monitoramento',
    'Análise',
    'Acompanhamento',
    'Fiscalização',
    'Elaboração Normativa',
    'Econômico-Financeira',
    'Projeto',
    'Outros',
]

# Descrições dos tipos de ação para o modal de seleção
TIPO_ACAO_DESCRICOES = {
    'Monitoramento': 'Engloba ações de monitorar se obrigações estão sendo cumpridas, com pouco impacto no dia a dia do monitorado. Aqui enquadra-se a solicitação de documentos, dados e indicadores para realizar uma análise mais analítica e validar desempenho.',
    'Análise': 'Engloba efetivamente investigar indícios apontados na etapa de monitoramento, conduzir análises de causa raiz de problemas específicos e produzir conclusões.',
    'Acompanhamento': 'Se medidas corretivas foram apontadas, este item serve para acompanhar essas medidas, verificar se resoluções propostas a problemas foram resolvidos.',
    'Fiscalização': 'Neste item, é usado efetivamente para ações fiscalizatórias (em campo ou não), instaurar processos administrativos e lavrar termos de notificação.',
    'Elaboração Normativa': 'Ação relacionada a produzir normas, como portarias ou notas técnicas, que formalizem a regulação de certos aspectos ou dê explicações e orientações técnicas sobre pontos específicos sobre a regulação de serviços públicos.',
    'Econômico-Financeira': 'Entram neste item de ação todas as relacionadas com análises contábeis (balanços, balancetes, etc), análises financeiras, definição ou análise de indicadores, análises econômicas que embasem revisões tarifárias, normativos, relatórios, entre outros.',
    'Projeto': 'Tipo de ação que exige o acompanhamento de um projeto proposto pela AGEMS para os regulados.',
    'Outros': 'Todos os demais tipo de ação que não se enquadrem nas anteriores.',
}

# Cores dos botões no modal de seleção
TIPO_ACAO_CORES = {
    'Monitoramento': '#1565C0',
    'Análise': '#6A1B9A',
    'Acompanhamento': '#00838F',
    'Fiscalização': '#C62828',
    'Elaboração Normativa': '#E65100',
    'Econômico-Financeira': '#2E7D32',
    'Projeto': '#F57F17',
    'Outros': '#546E7A',
}


def get_tipos_ordenados():
    """Retorna os TipoAcao na ordem canônica definida pelo cliente, via Case/When."""
    whens = [
        When(nome__icontains=nome, then=i)
        for i, nome in enumerate(TIPO_ACAO_ORDEM)
    ]
    return TipoAcao.objects.annotate(
        custom_order=Case(*whens, default=99, output_field=IntegerField())
    ).order_by('custom_order', 'nome')


# Endpoint AJAX para obrigações (usado na criação de Ações)
def get_obrigacoes_por_instrumento(request):
    instrumento_id = request.GET.get('instrumento_id')
    if not instrumento_id:
        return JsonResponse({'obrigacoes': [], 'entidades': []})

    obrigacoes = Obrigacao.objects.filter(instrumento_id=instrumento_id).values('id', 'titulo')

    # Também retorna as entidades do instrumento para popular o select de Entidade
    try:
        instrumento = Instrumento.objects.get(pk=instrumento_id)
        entidades = list(instrumento.entidades.values('id', 'razao_social'))
    except Instrumento.DoesNotExist:
        entidades = []

    return JsonResponse({'obrigacoes': list(obrigacoes), 'entidades': entidades})


class AcaoListView(PermissionRequiredMixin, ModernListView):

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Você não possui permissão para acessar esta funcionalidade ou excluir este registro.")
            return redirect(getattr(self, 'success_url', 'dashboard'))
        return super().handle_no_permission()

    """
    Lista as Ações (nível de execução vinculado à Obrigação).
    """
    permission_required = 'acoes.view_acao'
    model = Acao
    template_name = 'acoes/acao_list.html'
    icon = "bi bi-lightning-charge"
    subtitle = "Monitore, Fiscalize, Acompanhe, etc"
    create_url = 'acao_create'
    search_fields = ['nome', 'descricao', 'obrigacao__titulo']

    def get_queryset(self):
        instrumento_id = self.request.GET.get('instrumento')
        obrigacao_id = self.request.GET.get('obrigacao')
        user = self.request.user

        queryset = Acao.objects.select_related('responsavel', 'obrigacao', 'obrigacao__instrumento', 'tipo_acao')

        if user.perfil in [3, 4]:
            queryset = queryset.filter(Q(responsavel=user) | Q(executores=user)).distinct()

        if instrumento_id:
            queryset = queryset.filter(obrigacao__instrumento_id=instrumento_id)
        if obrigacao_id:
            queryset = queryset.filter(obrigacao_id=obrigacao_id)

        tipo_acao_id = self.request.GET.get('tipo_acao')
        if tipo_acao_id:
            queryset = queryset.filter(tipo_acao_id=tipo_acao_id)

        return queryset.order_by('data_inicio', 'prioridade', 'nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instrumento_id = self.request.GET.get('instrumento')

        context['instrumentos'] = Instrumento.objects.all()
        context['obrigacoes'] = Obrigacao.objects.filter(instrumento_id=instrumento_id).only('id', 'titulo') if instrumento_id else Obrigacao.objects.all().only('id', 'titulo')
        try:
            context['instrumento_selecionado'] = int(instrumento_id) if instrumento_id else None
        except (ValueError, TypeError):
            context['instrumento_selecionado'] = None

        try:
            context['obrigacao_selecionada'] = int(self.request.GET.get('obrigacao')) if self.request.GET.get('obrigacao') else None
        except (ValueError, TypeError):
            context['obrigacao_selecionada'] = None

        context['tipos_acao'] = get_tipos_ordenados()
        try:
            context['tipo_acao_selecionado'] = int(self.request.GET.get('tipo_acao')) if self.request.GET.get('tipo_acao') else None
        except (ValueError, TypeError):
            context['tipo_acao_selecionado'] = None

        return context


@login_required
def acao_tipo_selector(request):
    """
    Retorna o HTML do modal de seleção de tipo de ação.
    Carregado via fetch() pelo botão 'Adicionar Ação'.
    """
    tipos = get_tipos_ordenados()

    # Enriquecer cada tipo com cor e descrição
    tipos_enriquecidos = []
    for tipo in tipos:
        nome_key = None
        for nome in TIPO_ACAO_ORDEM:
            if nome.lower() in tipo.nome.lower() or tipo.nome.lower() in nome.lower():
                nome_key = nome
                break
        tipos_enriquecidos.append({
            'id': tipo.id,
            'nome': tipo.nome,
            'cor': TIPO_ACAO_CORES.get(nome_key, '#546E7A'),
            'descricao': TIPO_ACAO_DESCRICOES.get(nome_key, tipo.descricao or ''),
        })

    return render(request, 'acoes/acao_tipo_selector.html', {
        'tipos': tipos_enriquecidos,
    })


class AcaoCreateView(PermissionRequiredMixin, ModernCreateView):
    def get_readonly(self):
        # Perfil 4 e 5 são somente leitura para Ações em certos contextos, 
        # mas aqui vamos seguir a regra do cliente: Perfil 4 pode editar se for responsável.
        # Caso queira bloquear edição de Ação para visualizador (5):
        return self.request.user.perfil == 5

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['readonly'] = self.get_readonly()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['readonly'] = self.get_readonly()
        return context


    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Você não possui permissão para acessar esta funcionalidade ou excluir este registro.")
            return redirect(getattr(self, 'success_url', 'dashboard'))
        return super().handle_no_permission()

    permission_required = 'acoes.add_acao'
    model = Acao
    form_class = AcaoForm
    success_url = reverse_lazy('acao_list')
    template_name = 'acoes/acao_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        # Captura parâmetros da URL (útil quando vem de uma Obrigação específica)
        obrigacao_id = self.request.GET.get('obrigacao')
        if obrigacao_id:
            initial['obrigacao'] = obrigacao_id
        
        tipo_acao_id = self.request.GET.get('tipo_acao')
        if tipo_acao_id:
            initial['tipo_acao'] = tipo_acao_id
            
        return initial

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

        # Popula obrigatoriedade no instance para exibição no template quando em criação
        form = context.get('form')
        if form and not form.instance.pk and form.initial.get('obrigacao'):
            try:
                from instrumentos.models import Obrigacao
                form.instance.obrigacao = Obrigacao.objects.get(id=form.initial['obrigacao'])
            except:
                pass

        # Contexto para Fiscalização e Filtros (Fase 5 + develop)
        context['fiscalizacao_ids'] = list(TipoAcao.objects.filter(
            nome__icontains='Fiscalização'
        ).values_list('id', flat=True))
        
        context['instrumentos'] = Instrumento.objects.all()
        context['tipos_acao_ordenados'] = get_tipos_ordenados()

        # Preservar o JSON preenchido caso o form retorne inválido (recarregue na tela)
        if self.request.method == 'POST':
            context['saved_conformidades_json'] = self.request.POST.get('conformidades_json', '[]')
        else:
            context['saved_conformidades_json'] = '[]'
        return context

    def save_assets(self, acao, docs_formset, fotos_formset):
        """Helper para salvar ativos na criação"""
        try:
            docs = docs_formset.save(commit=False)
            for doc in docs:
                doc.acao = acao
                doc.usuario = self.request.user
                doc.save()
            for obj in docs_formset.deleted_objects:
                obj.delete()

            fotos = fotos_formset.save(commit=False)
            for foto in fotos:
                foto.acao = acao
                foto.usuario = self.request.user
                foto.save()
            for obj in fotos_formset.deleted_objects:
                obj.delete()
        except Exception as e:
            messages.error(self.request, f"Erro ao salvar arquivos: {str(e)}")
            print(f"CRITICAL ERROR SAVING ASSETS (CREATE): {str(e)}")

    def form_invalid(self, form):
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"=== FORM INVALID (CREATE) === Errors: {form.errors}")
        logger.error(f"=== POST DATA KEYS: {list(self.request.POST.keys())}")
        logger.error(f"=== FILES KEYS: {list(self.request.FILES.keys())}")
        # Also log formset statuses for complete picture
        context = self.get_context_data(form=form)
        checklist_formset = context.get('checklist_formset')
        docs_formset = context.get('docs_formset')
        fotos_formset = context.get('fotos_formset')
        if checklist_formset:
            logger.error(f"=== CHECKLIST valid={checklist_formset.is_valid()}, errors={checklist_formset.errors}")
        if docs_formset:
            logger.error(f"=== DOCS valid={docs_formset.is_valid()}, errors={docs_formset.errors}")
        if fotos_formset:
            logger.error(f"=== FOTOS valid={fotos_formset.is_valid()}, errors={fotos_formset.errors}")
        return super().form_invalid(form)

    def form_valid(self, form):
        import json
        import logging
        logger = logging.getLogger(__name__)

        print("=" * 60)
        print("=== FORM_VALID CHAMADO (CREATE) ===")

        context = self.get_context_data(form=form)
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
            # Salvar objeto principal
            self.object = form.save()
            
            # Salvar checklist
            checklist_formset.instance = self.object
            checklist_formset.save()
            
            # Processar conformidades pendentes (Fase 5)
            fake_item_mapping = {} # Map 'fake frontend id' -> real ItemConformidade instance
            json_data = self.request.POST.get('conformidades_json')
            if json_data:
                try:
                    conf_list = json.loads(json_data)
                    for g_idx, g_data in enumerate(conf_list):
                        grupo = Conformidade.objects.create(
                            acao=self.object,
                            nome=g_data.get('nome', 'Sem Nome'),
                            constatacao=g_data.get('constatacao', ''),
                            ordem=g_idx
                        )
                        for i_idx, i_data in enumerate(g_data.get('itens', [])):
                            item = ItemConformidade.objects.create(
                                conformidade=grupo,
                                nome=i_data.get('nome', 'Sem Nome'),
                                status=i_data.get('status', 0),
                                ordem=i_idx
                            )
                            # Salvar mapeamento caso front-end tenha enviado o fake ID original
                            fake_id = str(i_data.get('id', ''))
                            if fake_id:
                                fake_item_mapping[fake_id] = item
                except Exception as e:
                    logger.error(f"ERRO AO PROCESSAR CONFORMIDADES JSON: {e}")
                    messages.warning(self.request, "Ação salva, mas ocorreu um erro ao importar as conformidades.")

            # Salvar Ativos (Docs e Fotos) - Usando a lógica de mapeamento para fotos
            self.save_assets(self.object, docs_formset, fotos_formset, fake_item_mapping)

            messages.success(self.request, f'Ação "{self.object.nome}" criada com sucesso!')
            return super().form_valid(form)
        else:
            # Mensagens de erro da develop
            for form_erro in docs_formset.errors:
                if form_erro:
                    for campo, msgs in form_erro.items():
                         for msg in msgs:
                             prefixo = "Erro no arquivo: " if campo == 'arquivo' else ""
                             messages.error(self.request, f"{prefixo}{msg}")

            for form_erro in fotos_formset.errors:
                if form_erro:
                    for campo, msgs in form_erro.items():
                        for msg in msgs:
                            messages.error(self.request, f"Erro na foto: {msg}")

            if not docs_formset.errors and not fotos_formset.errors:
                 messages.error(self.request, "Verifique os dados do formulário.")

            return self.render_to_response(self.get_context_data(form=form))

        # Salvar Ativos
        if docs_valid:
            try:
                docs = docs_formset.save(commit=False)
                for doc in docs:
                    doc.acao = self.object
                    doc.usuario = self.request.user
                    doc.save()
                for obj in docs_formset.deleted_objects:
                    obj.delete()
            except Exception as e:
                logger.error(f"Erro ao salvar documentos: {e}")
                messages.warning(self.request, f"Erro ao salvar documento: {e}")
        else:
            messages.warning(self.request, "Documentos não foram salvos devido a erros de validação.")
            
        if fotos_valid:
            try:
                # Chamar save(commit=False) para popular deleted_objects e preparar instâncias
                fotos_formset.save(commit=False)
                
                for f_form in fotos_formset:
                    if f_form.cleaned_data and not f_form.cleaned_data.get('DELETE'):
                        foto = f_form.save(commit=False)
                        foto.acao = self.object
                        if not foto.pk:
                            foto.usuario = self.request.user
                            
                        # Extrair o fake_id que o form via JS injetou como input hidden
                        fake_item_id_str = str(self.request.POST.get(f"{f_form.prefix}-item_conformidade", ""))
                        if fake_item_id_str in fake_item_mapping:
                            foto.item_conformidade = fake_item_mapping[fake_item_id_str]
                            
                        foto.save()
                        
                for obj in fotos_formset.deleted_objects:
                    obj.delete()
            except Exception as e:
                logger.error(f"Erro ao salvar fotos: {e}")
                import traceback
                traceback.print_exc()
                messages.warning(self.request, f"Erro ao detalhado ao salvar fotos: {e}")
        else:
            errs = fotos_formset.errors
            messages.warning(self.request, f"Fotos ignoradas devido a erro de formato da imagem: verifique se não está enviando formato corrompido.")

        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            print("=== RETORNANDO JSON SUCCESS")
            return JsonResponse({'status': 'success', 'id': self.object.id})
        
        print(f"=== RETORNANDO 302 REDIRECT para {self.success_url}")
        messages.success(self.request, f'Ação "{self.object.nome}" criada com sucesso!')
        return redirect(self.success_url)



class AcaoUpdateView(PermissionRequiredMixin, ModernUpdateView):
    def get_readonly(self):
        # Perfil 4 e 5 são somente leitura para Ações em certos contextos, 
        # mas aqui vamos seguir a regra do cliente: Perfil 4 pode editar se for responsável.
        # Caso queira bloquear edição de Ação para visualizador (5):
        return self.request.user.perfil == 5

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['readonly'] = self.get_readonly()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['readonly'] = self.get_readonly()
        return context


    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Você não possui permissão para acessar esta funcionalidade ou excluir este registro.")
            return redirect(getattr(self, 'success_url', 'dashboard'))
        return super().handle_no_permission()

    permission_required = 'acoes.change_acao'
    model = Acao
    form_class = AcaoForm
    success_url = reverse_lazy('acao_list')
    template_name = 'acoes/acao_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['checklist_formset'] = ChecklistItemFormSet(self.request.POST, instance=self.object, prefix='checklist_itens')
            context['docs_formset'] = AcaoDocumentoFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix='docs')
            context['fotos_formset'] = AcaoFotoFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix='fotos')
            if 'conformidades-TOTAL_FORMS' in self.request.POST:
                context['conformidade_formset'] = ConformidadeFormSet(self.request.POST, instance=self.object, prefix='conformidades')
            else:
                context['conformidade_formset'] = ConformidadeFormSet(instance=self.object, prefix='conformidades')
        else:
            context['checklist_formset'] = ChecklistItemFormSet(instance=self.object, prefix='checklist_itens')
            context['docs_formset'] = AcaoDocumentoFormSet(instance=self.object, prefix='docs')
            context['fotos_formset'] = AcaoFotoFormSet(instance=self.object, prefix='fotos')
            context['conformidade_formset'] = ConformidadeFormSet(instance=self.object, prefix='conformidades')

        # Contexto para Fiscalização e Filtros (Fase 5 + develop)
        context['fiscalizacao_ids'] = list(TipoAcao.objects.filter(
            nome__icontains='Fiscalização'
        ).values_list('id', flat=True))

        context['instrumentos'] = Instrumento.objects.all()
        context['tipos_acao_ordenados'] = get_tipos_ordenados()

        # Entidades disponíveis filtradas pelo instrumento da obrigação desta ação
        try:
            context['entidades_disponiveis'] = self.object.obrigacao.instrumento.entidades.all()
        except Exception:
            context['entidades_disponiveis'] = Entidade.objects.none()

        return context

    def save_assets(self, acao, docs_formset, fotos_formset, fake_item_mapping=None):
        """Helper para salvar documentos e fotos com injeção de usuário e mapeamento de conformidades"""
        if fake_item_mapping is None:
            fake_item_mapping = {}

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
            fotos_formset.save(commit=False)
            for f_form in fotos_formset:
                if f_form.cleaned_data and not f_form.cleaned_data.get('DELETE'):
                    foto = f_form.save(commit=False)
                    foto.acao = acao
                    if not foto.pk:
                        foto.usuario = self.request.user
                    
                    # Tentar mapear para Item de Conformidade (Fase 5)
                    item_id_str = str(self.request.POST.get(f"{f_form.prefix}-item_conformidade", ""))
                    if item_id_str in fake_item_mapping:
                        foto.item_conformidade = fake_item_mapping[item_id_str]
                    elif item_id_str:
                        try:
                            foto.item_conformidade_id = int(item_id_str)
                        except ValueError:
                            pass
                    
                    foto.save()
            for obj in fotos_formset.deleted_objects:
                obj.delete()
        except Exception as e:
            messages.error(self.request, f"Erro ao salvar arquivos: {str(e)}")

    def form_valid(self, form):
        import logging
        logger = logging.getLogger(__name__)

        context = self.get_context_data(form=form)
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
            self.object = form.save()
            
            # Checklist
            checklist_formset.instance = self.object
            checklist_formset.save()
            
            # Salvar Ativos (Docs e Fotos)
            # Nota: Conformidades no Update são editadas via AJAX na interface,
            # mas fotos podem ser reatribuídas se novos itens surgirem?
            # Por enquanto mantemos a lógica de salvamento padrão.
            self.save_assets(self.object, docs_formset, fotos_formset)

            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'id': self.object.id})

            messages.success(self.request, f'Ação "{self.object.nome}" atualizada com sucesso!')
            return redirect(self.success_url)
        else:
            # Erros de validação (develop style)
            for form_erro in docs_formset.errors:
                if form_erro:
                    for campo, msgs in form_erro.items():
                         for msg in msgs:
                             prefixo = "Erro no arquivo: " if campo == 'arquivo' else ""
                             messages.error(self.request, f"{prefixo}{msg}")

            for form_erro in fotos_formset.errors:
                if form_erro:
                    for campo, msgs in form_erro.items():
                        for msg in msgs:
                            messages.error(self.request, f"Erro na foto: {msg}")

            if not docs_formset.errors and not fotos_formset.errors:
                 messages.error(self.request, "Verifique os dados do formulário.")

            return self.render_to_response(self.get_context_data(form=form))


class AcaoDeleteView(PermissionRequiredMixin, ModernDeleteView):

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Você não possui permissão para acessar esta funcionalidade ou excluir este registro.")
            return redirect(getattr(self, 'success_url', 'dashboard'))
        return super().handle_no_permission()

    permission_required = 'acoes.delete_acao'
    model = Acao
    success_url = reverse_lazy('acao_list')


# Calendário de Ações
class AcaoCalendarioView(PermissionRequiredMixin, TemplateView):

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Você não possui permissão para acessar esta funcionalidade ou excluir este registro.")
            return redirect(getattr(self, 'success_url', 'dashboard'))
        return super().handle_no_permission()

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
        'a_iniciar': '#f57c00',
        'em_andamento': '#1976d2',
        'atrasado': '#c62828',
        'em_validacao': '#6a1b9a',
        'finalizado': '#2e7d32',
    }
    return cores.get(status, '#607d8b')


# --- ENDPOINTS PARA MAPA (FASE 5) ---

@permission_required('acoes.view_acao', raise_exception=True)
def listar_marcadores_ajax(request, acao_id):
    """Lista todos os marcadores de uma ação específica"""
    acao = get_object_or_404(Acao, id=acao_id)
    marcadores = acao.marcadores.all()

    data = []
    for m in marcadores:
        fotos = m.fotos.all()
        data.append({
            'id': m.id,
            'titulo': m.titulo,
            'descricao': m.descricao,
            'latitude': float(m.latitude),
            'longitude': float(m.longitude),
            'data_criacao': m.data_criacao.strftime('%d/%m/%Y %H:%M'),
            'usuario': m.usuario.get_full_name() if m.usuario else "Sistema",
            'fotos': [{'id': f.id, 'url': f.imagem.url, 'legenda': f.legenda} for f in fotos]
        })

    return JsonResponse({'status': 'success', 'marcadores': data})


@csrf_exempt
@require_POST
@permission_required('acoes.change_acao', raise_exception=True)
def salvar_marcador_ajax(request, acao_id):
    """Cria ou edita um marcador no mapa via AJAX"""
    try:
        acao = get_object_or_404(Acao, id=acao_id)
        marcador_id = request.POST.get('marcador_id')

        titulo = request.POST.get('titulo')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        if not titulo or not latitude or not longitude:
            return JsonResponse({
                'status': 'error',
                'message': 'Título, Latitude e Longitude são obrigatórios.'
            }, status=400)

        if marcador_id:
            marcador = AcaoMarcador.objects.get(id=marcador_id, acao=acao)
        else:
            marcador = AcaoMarcador(acao=acao, usuario=request.user)

        marcador.titulo = titulo
        marcador.descricao = request.POST.get('descricao', '')
        marcador.latitude = latitude
        marcador.longitude = longitude
        marcador.save()

        fotos_count = 0
        if 'fotos' in request.FILES:
            for f in request.FILES.getlist('fotos'):
                AcaoFoto.objects.create(
                    acao=acao,
                    marcador=marcador,
                    imagem=f,
                    usuario=request.user,
                    legenda=f"Foto do marcador: {marcador.titulo}",
                    coordenadas=f"{marcador.latitude}, {marcador.longitude}"
                )
                fotos_count += 1

        return JsonResponse({
            'status': 'success',
            'marcador': {
                'id': marcador.id,
                'titulo': marcador.titulo,
                'latitude': float(marcador.latitude),
                'longitude': float(marcador.longitude),
                'fotos_count': fotos_count
            }
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_POST
@permission_required('acoes.change_acao', raise_exception=True)
def deletar_marcador_ajax(request, marcador_id):
    """Deleta um marcador do mapa"""
    marcador = get_object_or_404(AcaoMarcador, id=marcador_id)
    marcador.delete()
    return JsonResponse({'status': 'success'})
# --- AJAX ENDPOINTS PARA CONFORMIDADES (FASE 5) ---

from .models import Conformidade, ItemConformidade, Constatacao

@permission_required('acoes.view_acao', raise_exception=True)
def conformidades_data_ajax(request, acao_id):
    """Retorna a estrutura completa de conformidades para o frontend."""
    acao = get_object_or_404(Acao, id=acao_id)
    conformidades = acao.conformidades.all().prefetch_related('itens', 'itens__constatacoes')
    
    data = []
    for conf in conformidades:
        itens_data = []
        for item in conf.itens.all():
            constatacoes_data = []
            for const in item.constatacoes.all():
                constatacoes_data.append({
                    'id': const.id,
                    'texto': const.texto,
                    'data': const.data_criacao.strftime('%d/%m/%Y %H:%M')
                })
            
            itens_data.append({
                'id': item.id,
                'nome': item.nome,
                'status': item.status,
                'ordem': item.ordem,
                'constatacoes': constatacoes_data,
                'fotos_count': item.fotos.count()
            })
            
        data.append({
            'id': conf.id,
            'nome': conf.nome,
            'constatacao': conf.constatacao,
            'itens': itens_data
        })
        
    return JsonResponse({'status': 'success', 'data': data})


@csrf_exempt
@require_POST
@permission_required('acoes.change_acao', raise_exception=True)
def update_item_status_ajax(request):
    """Atualiza o status tri-state de um item de conformidade."""
    item_id = request.POST.get('item_id')
    new_status = request.POST.get('status')
    
    if item_id is None or new_status is None:
        return JsonResponse({'status': 'error', 'message': 'Dados incompletos.'}, status=400)
        
    item = get_object_or_404(ItemConformidade, id=item_id)
    try:
        item.status = int(new_status)
        item.save()
        return JsonResponse({'status': 'success', 'item_id': item.id, 'status_value': item.status})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_POST
@permission_required('acoes.change_acao', raise_exception=True)
def add_constatacao_ajax(request):
    """Adiciona ou atualiza a constatação textual de um GRUPO (Conformidade)."""
    conformidade_id = request.POST.get('conformidade_id')
    texto = request.POST.get('texto', '')
    
    if not conformidade_id:
        return JsonResponse({'status': 'error', 'message': 'Grupo é obrigatório.'}, status=400)
        
    conf = get_object_or_404(Conformidade, id=conformidade_id)
    conf.constatacao = texto
    conf.save()
    
    return JsonResponse({
        'status': 'success', 
        'id': conf.id, 
        'texto': conf.constatacao
    })


@csrf_exempt
@require_POST
@permission_required('acoes.change_acao', raise_exception=True)
def update_foto_legenda_ajax(request):
    """Atualiza a legenda de uma foto via AJAX."""
    foto_id = request.POST.get('foto_id')
    legenda = request.POST.get('legenda')
    
    if not foto_id:
        return JsonResponse({'status': 'error', 'message': 'ID da foto não fornecido.'}, status=400)
    
    foto = get_object_or_404(AcaoFoto, id=foto_id)
    foto.legenda = legenda
    foto.save()
    
    return JsonResponse({'status': 'success', 'legenda': foto.legenda})


@csrf_exempt
@require_POST
@permission_required('acoes.change_acao', raise_exception=True)
def upload_foto_item_ajax(request):
    """Realiza upload de foto vinculado a um item de conformidade com validação rigorosa."""
    item_id = request.POST.get('item_id')
    if not item_id or 'imagem' not in request.FILES:
        return JsonResponse({'status': 'error', 'message': 'Dados incompletos.'}, status=400)
    
    imagem = request.FILES['imagem']
    
    # Validação de Extensão
    import os
    ext = os.path.splitext(imagem.name)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
        return JsonResponse({
            'status': 'error', 
            'message': 'Formato de arquivo não permitido. Use apenas JPG, PNG ou WEBP.'
        }, status=400)

    # Validação de Conteúdo (Simples)
    if not imagem.content_type.startswith('image/'):
        return JsonResponse({
            'status': 'error',
            'message': 'O arquivo enviado não é uma imagem válida.'
        }, status=400)
    
    item = get_object_or_404(ItemConformidade, id=item_id)
    
    try:
        foto = AcaoFoto.objects.create(
            acao=item.conformidade.acao,
            item_conformidade=item,
            imagem=imagem,
            usuario=request.user,
            legenda=f"Evidência: {item.nome}"
        )
        return JsonResponse({
            'status': 'success',
            'id': foto.id,
            'url': foto.imagem.url,
            'legenda': foto.legenda
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_POST
@permission_required('acoes.change_acao', raise_exception=True)
def remove_constatacao_ajax(request):
    """Remove uma constatação."""
    const_id = request.POST.get('const_id')
    constatacao = get_object_or_404(Constatacao, id=const_id)
    constatacao.delete()
    return JsonResponse({'status': 'success'})


@csrf_exempt
@require_POST
@permission_required('acoes.change_acao', raise_exception=True)
def rename_item_ajax(request):
    """Renomeia um item de conformidade."""
    item_id = request.POST.get('item_id')
    novo_nome = request.POST.get('nome')
    
    if not item_id or not novo_nome:
        return JsonResponse({'status': 'error', 'message': 'Dados incompletos.'}, status=400)
        
    item = get_object_or_404(ItemConformidade, id=item_id)
    item.nome = novo_nome
    item.save()
    return JsonResponse({'status': 'success', 'nome': item.nome})


from .models import ConformidadeTemplate, ItemConformidadeTemplate

@permission_required('acoes.view_acao', raise_exception=True)
def listar_templates_ajax(request):
    """Lista templates disponíveis com seus respectivos itens."""
    templates = ConformidadeTemplate.objects.filter(ativo=True).prefetch_related('itens')
    data = [
        {
            'id': t.id, 
            'nome': t.nome, 
            'descricao': t.descricao,
            'itens': [{'nome': i.nome, 'ordem': i.ordem} for i in t.itens.all()]
        } for t in templates
    ]
    return JsonResponse({'status': 'success', 'templates': data})


@csrf_exempt
@require_POST
@permission_required('acoes.change_acao', raise_exception=True)
def aplicar_template_ajax(request, acao_id):
    """Aplica um template a uma ação."""
    acao = get_object_or_404(Acao, id=acao_id)
    template_id = request.POST.get('template_id')
    
    if not template_id:
        return JsonResponse({'status': 'error', 'message': 'Template não selecionado.'}, status=400)
    
    template = get_object_or_404(ConformidadeTemplate, id=template_id)
    
    # Criar um grupo de conformidade baseado no template
    conf = Conformidade.objects.create(acao=acao, nome=template.nome)
    for item_t in template.itens.all():
        ItemConformidade.objects.create(
            conformidade=conf,
            nome=item_t.nome,
            ordem=item_t.ordem
        )
        
    return JsonResponse({'status': 'success'})


@csrf_exempt
@require_POST
@permission_required('acoes.change_acao', raise_exception=True)
def salvar_como_template_ajax(request, acao_id):
    """Cria um novo template persistente com base nos itens desta ação."""
    acao = get_object_or_404(Acao, id=acao_id)
    nome = request.POST.get('nome')
    descricao = request.POST.get('descricao', '')
    
    if not nome:
        return JsonResponse({'status': 'error', 'message': 'O título do template é obrigatório.'}, status=400)
        
    try:
        # Criar o template principal
        template = ConformidadeTemplate.objects.create(
            nome=nome,
            descricao=descricao,
            ativo=True
        )
        
        # Buscar itens da ação ordenados por grupo e depois por ordem do item
        # Estamos 'achatando' os grupos em um único template conforme o padrão atual do sistema
        itens = ItemConformidade.objects.filter(
            conformidade__acao=acao
        ).order_by('conformidade__ordem', 'ordem')
        
        for i, item in enumerate(itens):
            ItemConformidadeTemplate.objects.create(
                template=template,
                nome=item.nome,
                ordem=i
            )
            
        return JsonResponse({
            'status': 'success', 
            'message': 'Template criado com sucesso!',
            'template_id': template.id
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_POST
@permission_required('acoes.change_acao', raise_exception=True)
def salvar_template_direto_ajax(request):
    """Cria um template a partir de dados JSON enviados diretamente."""
    nome = request.POST.get('nome')
    descricao = request.POST.get('descricao', '')
    json_data = request.POST.get('conformidades_json')
    
    if not nome or not json_data:
        return JsonResponse({'status': 'error', 'message': 'Dados incompletos.'}, status=400)
        
    import json
    try:
        data = json.loads(json_data)
        template = ConformidadeTemplate.objects.create(
            nome=nome,
            descricao=descricao,
            ativo=True
        )
        
        ordem_cont = 0
        for grupo in data:
            # Por enquanto 'achatamos' os grupos no template
            for item in grupo.get('itens', []):
                ItemConformidadeTemplate.objects.create(
                    template=template,
                    nome=item.get('nome', 'Sem Nome'),
                    ordem=ordem_cont
                )
                ordem_cont += 1
                
        return JsonResponse({'status': 'success', 'template_id': template.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_POST
@permission_required('acoes.change_acao', raise_exception=True)
def criar_grupo_ajax(request, acao_id):
    """Cria um novo grupo (Conformidade) manualmente."""
    acao = get_object_or_404(Acao, id=acao_id)
    nome = request.POST.get('nome')
    
    if not nome:
        return JsonResponse({'status': 'error', 'message': 'Nome é obrigatório.'}, status=400)
        
    conf = Conformidade.objects.create(acao=acao, nome=nome)
    return JsonResponse({'status': 'success', 'id': conf.id, 'nome': conf.nome})


@csrf_exempt
@require_POST
@permission_required('acoes.change_acao', raise_exception=True)
def adicionar_item_ajax(request):
    """Adiciona um item a um grupo existente."""
    conf_id = request.POST.get('conformidade_id')
    nome = request.POST.get('nome')
    
    if not conf_id or not nome:
        return JsonResponse({'status': 'error', 'message': 'Dados incompletos.'}, status=400)
        
    conf = get_object_or_404(Conformidade, id=conf_id)
    item = ItemConformidade.objects.create(conformidade=conf, nome=nome)
    
    return JsonResponse({'status': 'success', 'id': item.id, 'nome': item.nome})


@csrf_exempt
@require_POST
@permission_required('acoes.change_acao', raise_exception=True)
def renomear_grupo_ajax(request):
    """Renomeia um grupo de conformidade."""
    conf_id = request.POST.get('conformidade_id')
    novo_nome = request.POST.get('nome')
    
    if not conf_id or not novo_nome:
        return JsonResponse({'status': 'error', 'message': 'Dados incompletos.'}, status=400)
        
    conf = get_object_or_404(Conformidade, id=conf_id)
    conf.nome = novo_nome
    conf.save()
    return JsonResponse({'status': 'success', 'nome': conf.nome})


@csrf_exempt
@require_POST
@permission_required('acoes.change_acao', raise_exception=True)
def remover_todas_conformidades_ajax(request, acao_id):
    """Remove todos os grupos e itens de conformidade de uma ação."""
    acao = get_object_or_404(Acao, id=acao_id)
    try:
        # Pega todas as conformidades da acao
        conformidades = acao.conformidades.all()
        count = conformidades.count()
        conformidades.delete() # Cascade deleta itens e constatacoes
        
        return JsonResponse({
            'status': 'success', 
            'message': f'{count} grupos removidos com sucesso.'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_POST
@permission_required('acoes.change_acao', raise_exception=True)
def remover_grupo_ajax(request):
    """Remove um grupo de conformidade e todos os seus itens."""
    conf_id = request.POST.get('conformidade_id')
    conf = get_object_or_404(Conformidade, id=conf_id)
    conf.delete()
    return JsonResponse({'status': 'success'})


@csrf_exempt
@require_POST
@permission_required('acoes.change_acao', raise_exception=True)
def remover_item_ajax(request):
    """Remove um item de conformidade."""
    item_id = request.POST.get('item_id')
    item = get_object_or_404(ItemConformidade, id=item_id)
    item.delete()
    return JsonResponse({'status': 'success'})


@csrf_exempt
@require_POST
@permission_required('acoes.change_acao', raise_exception=True)
@login_required
def reordenar_grupos_ajax(request):
    """Atualiza a ordem dos grupos (Conformidade) de uma ação."""
    import json
    try:
        data = json.loads(request.body)
        ordem = data.get('ordem', []) # Lista de IDs na ordem correta
        
        for i, group_id in enumerate(ordem):
            Conformidade.objects.filter(id=group_id).update(ordem=i)
            
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_exempt
@require_POST
@permission_required('acoes.change_acao', raise_exception=True)
def reordenar_itens_ajax(request):
    """Atualiza a ordem dos itens dentro de um grupo."""
    import json
    try:
        data = json.loads(request.body)
        ordem = data.get('ordem', []) # Lista de IDs na ordem correta
        
        for i, item_id in enumerate(ordem):
            ItemConformidade.objects.filter(id=item_id).update(ordem=i)
            
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def listar_obrigacoes_instrumento_ajax(request, instrumento_id):
    from instrumentos.models import Obrigacao
    obrigacoes = Obrigacao.objects.filter(instrumento_id=instrumento_id).values('id', 'titulo')
    return JsonResponse({'status': 'success', 'data': list(obrigacoes)})


# --- GERENCIAMENTO DE TEMPLATES ---

@login_required
@permission_required('acoes.view_conformidadetemplate', raise_exception=True)
def template_list(request):
    templates = ConformidadeTemplate.objects.filter(ativo=True).order_by('nome')
    return render(request, 'acoes/template_list.html', {'templates': templates})

@login_required
@permission_required('acoes.add_conformidadetemplate', raise_exception=True)
def template_create(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao', '')
        if nome:
            template = ConformidadeTemplate.objects.create(nome=nome, descricao=descricao)
            return redirect('template_edit', pk=template.pk)
    return render(request, 'acoes/template_form.html')

@login_required
@permission_required('acoes.change_conformidadetemplate', raise_exception=True)
def template_edit(request, pk):
    template = get_object_or_404(ConformidadeTemplate, pk=pk)
    return render(request, 'acoes/template_form.html', {'template': template})

@csrf_exempt
@require_POST
@login_required
@permission_required('acoes.change_conformidadetemplate', raise_exception=True)
def template_add_item_ajax(request):
    template_id = request.POST.get('template_id')
    nome = request.POST.get('nome')
    if not template_id or not nome:
        return JsonResponse({'status': 'error', 'message': 'Dados incompletos.'}, status=400)
    
    template = get_object_or_404(ConformidadeTemplate, id=template_id)
    # Pegar a última ordem
    ultima_ordem = template.itens.count()
    item = ItemConformidadeTemplate.objects.create(template=template, nome=nome, ordem=ultima_ordem)
    return JsonResponse({'status': 'success', 'id': item.id, 'nome': item.nome})

@csrf_exempt
@require_POST
@login_required
@permission_required('acoes.change_conformidadetemplate', raise_exception=True)
def template_remove_item_ajax(request):
    item_id = request.POST.get('item_id')
    item = get_object_or_404(ItemConformidadeTemplate, id=item_id)
    item.delete()
    return JsonResponse({'status': 'success'})

@csrf_exempt
@require_POST
@login_required
@permission_required('acoes.change_conformidadetemplate', raise_exception=True)
def template_rename_item_ajax(request):
    item_id = request.POST.get('item_id')
    nome = request.POST.get('nome')
    item = get_object_or_404(ItemConformidadeTemplate, id=item_id)
    item.nome = nome
    item.save()
    return JsonResponse({'status': 'success'})


@csrf_exempt
@require_POST
@login_required
@permission_required('acoes.delete_conformidadetemplate', raise_exception=True)
def template_delete_ajax(request, pk):
    """Exclui (soft-delete via ativo=False) um template de conformidade."""
    template = get_object_or_404(ConformidadeTemplate, pk=pk)
    try:
        template.ativo = False
        template.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
