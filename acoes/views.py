from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required, login_required
from core.views import ModernListView, ModernCreateView, ModernUpdateView, ModernDeleteView
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.db.models import Q
from .models import Acao, ChecklistItem, AcaoMarcador, AcaoFoto
from django.urls import reverse_lazy
from .forms import (
    AcaoForm, ChecklistItemFormSet, AcaoDocumentoFormSet, 
    AcaoFotoFormSet, ConformidadeFormSet
)

from instrumentos.models import Instrumento, Obrigacao
from django.http import JsonResponse
from core.models import TipoAcao
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


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
        queryset = Acao.objects.select_related('responsavel', 'obrigacao', 'obrigacao__instrumento', 'tipo_acao')

        # FILTRO DE ESCOPO: Técnicos veem apenas suas ações (Responsável ou Executor)
        if user.perfil in [3, 4]:
            queryset = queryset.filter(Q(responsavel=user) | Q(executores=user)).distinct()
        
        # Admin e Gestor veem tudo (base queryset já é all())

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

        from acoes.models import TipoAcao
        context['tipos_acao'] = TipoAcao.objects.all().order_by('nome')
        try:
            context['tipo_acao_selecionado'] = int(self.request.GET.get('tipo_acao')) if self.request.GET.get('tipo_acao') else None
        except (ValueError, TypeError):
            context['tipo_acao_selecionado'] = None

        return context


class AcaoCreateView(PermissionRequiredMixin, ModernCreateView):
    permission_required = 'acoes.add_acao'
    model = Acao
    form_class = AcaoForm
    success_url = reverse_lazy('acao_list')
    template_name = 'acoes/acao_form.html'

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


        
        # Contexto para Fiscalização (Fase 5)
        context['fiscalizacao_ids'] = list(TipoAcao.objects.filter(
            nome__icontains='Fiscalização'
        ).values_list('id', flat=True))
        
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
            messages.error(self.request, f"Erro ao salvar arquivos: {str(e)}")
            print(f"CRITICAL ERROR SAVING ASSETS (CREATE): {str(e)}")

    def form_valid(self, form):
        context = self.get_context_data()
        checklist_formset = context['checklist_formset']
        docs_formset = context['docs_formset']
        fotos_formset = context['fotos_formset']
        
        # O Django já validou o 'form' antes de chamar form_valid.
        # Validamos apenas os formsets adicionais.
        formsets_valid = all([
            checklist_formset.is_valid(),
            docs_formset.is_valid(),
            fotos_formset.is_valid()
        ])

        if formsets_valid:
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
            
            # Salvar objeto principal
            self.object = form.save()
            
            # Salvar formsets
            checklist_formset.instance = self.object
            checklist_formset.save()
            
            self.save_assets(self.object, docs_formset, fotos_formset)
            
            messages.success(self.request, f'Ação "{self.object.nome}" criada com sucesso!')
            return redirect(self.success_url)
        else:
            # Coleta erros de tudo para exibição clara
            all_forms = [
                ('Dados Gerais', form),
                ('Checklist', checklist_formset),
                ('Documentação', docs_formset),
                ('Fotos', fotos_formset)
            ]
            for label, fs in all_forms:
                if hasattr(fs, 'errors') and fs.errors:
                    messages.error(self.request, f"Erro em {label}. Verifique os campos.")
            
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
            if 'conformidades-TOTAL_FORMS' in self.request.POST:
                context['conformidade_formset'] = ConformidadeFormSet(self.request.POST, instance=self.object, prefix='conformidades')
            else:
                context['conformidade_formset'] = ConformidadeFormSet(instance=self.object, prefix='conformidades')
        else:
            context['checklist_formset'] = ChecklistItemFormSet(instance=self.object, prefix='checklist_itens')
            context['docs_formset'] = AcaoDocumentoFormSet(instance=self.object, prefix='docs')
            context['fotos_formset'] = AcaoFotoFormSet(instance=self.object, prefix='fotos')
            context['conformidade_formset'] = ConformidadeFormSet(instance=self.object, prefix='conformidades')

            
        # Contexto para Fiscalização (Fase 5)
        context['fiscalizacao_ids'] = list(TipoAcao.objects.filter(
            nome__icontains='Fiscalização'
        ).values_list('id', flat=True))
        
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
            
            # Conformidades são geridas via AJAX na Fase 5
            # Removido conformidades.save() para evitar crash

            messages.success(self.request, f'Ação "{self.object.nome}" atualizada com sucesso!')
            return redirect(self.success_url)
        else:
            # Coleta erros de tudo para exibição clara
            all_forms = [
                ('Dados Gerais', form),
                ('Checklist', checklist_formset),
                ('Documentação', docs_formset),
                ('Fotos', fotos_formset)
            ]
            for label, fs in all_forms:
                if hasattr(fs, 'errors') and fs.errors:
                    messages.error(self.request, f"Erro em {label}. Verifique os campos.")

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
        
        # Processar novas fotos específicas do marcador se enviadas
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
    # Fotos vinculadas não são deletadas, apenas perdem o vínculo com o marcador
    # Isso garante que a evidência de campo continue na aba Fotos.
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
    """Adiciona uma constatação textual a um item."""
    item_id = request.POST.get('item_id')
    texto = request.POST.get('texto')
    
    if not item_id or not texto:
        return JsonResponse({'status': 'error', 'message': 'Item e texto são obrigatórios.'}, status=400)
        
    item = get_object_or_404(ItemConformidade, id=item_id)
    constatacao = Constatacao.objects.create(item=item, texto=texto)
    
    return JsonResponse({
        'status': 'success', 
        'id': constatacao.id, 
        'texto': constatacao.texto,
        'data': constatacao.data_criacao.strftime('%d/%m/%Y %H:%M')
    })


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
    """Lista templates disponíveis."""
    templates = ConformidadeTemplate.objects.filter(ativo=True)
    data = [{'id': t.id, 'nome': t.nome, 'descricao': t.descricao} for t in templates]
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
