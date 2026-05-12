import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse

from instrumentos.models import Instrumento, Obrigacao
from indicadores.models import IndicadorContratual, ValorIndicador
from entidades.models import Entidade
from acoes.models import Acao
from usuarios.mixins import get_diretoria_filter


@login_required
def dashboard_principal(request):
    """
    Dashboard principal do sistema (Versão Unificada 4 Níveis).
    Exibe dados consolidados de Instrumentos, Obrigações e Ações.
    """
    usuario = request.user
    hoje = timezone.now().date()

    # RBAC: Filtros de Diretoria
    # get_diretoria_filter retorna None para Admin (sem filtro)
    f_instrumento = get_diretoria_filter(usuario, prefix='')
    f_obrigacao = get_diretoria_filter(usuario, prefix='instrumento__')
    f_acao = get_diretoria_filter(usuario, prefix='obrigacao__instrumento__')

    # Define se é um Técnico (perfil 3 ou 4) para aplicar filtros de visão adicionais
    is_tecnico = (usuario.perfil in [3, 4])

    # Instrumentos vigentes
    queryset_instrumentos = Instrumento.objects.filter(status='vigente')
    if f_instrumento:
        queryset_instrumentos = queryset_instrumentos.filter(f_instrumento)
        
    if is_tecnico:
        # Filtra instrumentos que têm obrigações com ações deste usuário (Responsável ou Executor)
        queryset_instrumentos = queryset_instrumentos.filter(
            Q(obrigacoes__acoes__responsavel=usuario) | Q(obrigacoes__acoes__executores=usuario)
        ).distinct()
    
    total_instrumentos = queryset_instrumentos.count()

    # Distribuição de Instrumentos por Tipo
    instrumentos_por_tipo = list(
        queryset_instrumentos
        .values('tipo_instrumento__nome')
        .annotate(total=Count('id'))
        .order_by('tipo_instrumento__nome')
    )

    # Total de obrigações do sistema
    queryset_all_obrigacoes = Obrigacao.objects.all()
    if f_obrigacao:
        queryset_all_obrigacoes = queryset_all_obrigacoes.filter(f_obrigacao)
        
    if is_tecnico:
        queryset_all_obrigacoes = queryset_all_obrigacoes.filter(
            Q(acoes__responsavel=usuario) | Q(acoes__executores=usuario)
        ).distinct()
        
    total_obrigacoes = queryset_all_obrigacoes.count()

    # Ações (Executores veem apenas as suas)
    acoes = Acao.objects.all()
    if f_acao:
        acoes = acoes.filter(f_acao)
    
    if is_tecnico:
        # Filtra ações onde o usuário é responsável OU está na lista de executores
        acoes = acoes.filter(
            Q(responsavel=usuario) | Q(executores=usuario)
        ).distinct()

    # Cards de Contagem
    acoes_vencidas = acoes.filter(
        data_fim__lt=hoje, status__in=['a_iniciar', 'em_andamento', 'atrasado']
    ).count()

    acoes_a_vencer = acoes.filter(
        data_fim__gte=hoje, data_fim__lte=hoje + timedelta(days=7),
        status__in=['a_iniciar', 'em_andamento']
    ).count()

    # Minhas Ações (Onde o usuário é Responsável ou Executor)
    minhas_acoes = Acao.objects.filter(
        Q(responsavel=usuario) | Q(executores=usuario)
    ).select_related(
        'obrigacao', 'tipo_acao', 'responsavel'
    ).distinct().order_by('-data_cadastro')

    # Distribuição de Ações por status (Mantém estatística global/diretoria)
    acoes_por_status = list(
        acoes.values('status')
        .annotate(total=Count('id'))
        .order_by('status')
    )

    context = {
        'usuario': usuario,
        'total_instrumentos': total_instrumentos,
        'total_obrigacoes': total_obrigacoes,
        'instrumentos_por_tipo': json.dumps(instrumentos_por_tipo),
        'tarefas_por_status': json.dumps(acoes_por_status),
        'tarefas_a_vencer': acoes_a_vencer,
        'tarefas_vencidas': acoes_vencidas,
        'minhas_acoes': minhas_acoes,
    }

    return render(request, 'dashboards/dashboard_modern.html', context)


@login_required
def lista_instrumentos_json(request):
    """Retorna lista de instrumentos vigentes para o modal de seleção."""
    usuario = request.user
    f_instrumento = get_diretoria_filter(usuario, prefix='')
    
    queryset = Instrumento.objects.filter(status='vigente')
    if f_instrumento:
        queryset = queryset.filter(f_instrumento)
        
    if usuario.perfil in [3, 4]:
        queryset = queryset.filter(
            Q(obrigacoes__acoes__responsavel=usuario) | Q(obrigacoes__acoes__executores=usuario)
        ).distinct()
        
    instrumentos = []
    for inst in queryset.select_related('tipo_instrumento'):
        instrumentos.append({
            'id': inst.id,
            'numero': inst.numero,
            'tipo': inst.tipo_instrumento.nome
        })
        
    return JsonResponse({'success': True, 'instrumentos': instrumentos})


@login_required
def dashboard_por_contrato(request, instrumento_id):
    """Dashboard gerencial focado em um contrato específico."""
    usuario = request.user
    hoje = timezone.now().date()
    instrumento = get_object_or_404(Instrumento, pk=instrumento_id)
    
    # RBAC: Verificar se o usuário tem acesso à diretoria deste instrumento
    from usuarios.mixins import verifica_acesso_unidade
    if not verifica_acesso_unidade(usuario, instrumento):
        from django.contrib import messages
        messages.error(request, "Você não tem permissão para acessar este dashboard.")
        return redirect('dashboard')
    
    obrigacoes = instrumento.obrigacoes.all()
    total_obrigacoes = obrigacoes.count()
    
    obrigacoes_finalizadas = obrigacoes.filter(status='cumprida').count()
    obrigacoes_em_andamento = obrigacoes.filter(status='em_andamento').count()
    obrigacoes_atrasadas = obrigacoes.filter(status='vencida').count()
    
    # % de atendimento do contrato (média das obrigações)
    percentual_atendimento_contrato = obrigacoes.aggregate(Avg('percentual_atendimento'))['percentual_atendimento__avg'] or 0
    percentual_atendimento_contrato = round(float(percentual_atendimento_contrato), 1)
    
    # Distribuição de obrigações por status (Pie Chart)
    obrigacoes_por_status = list(
        obrigacoes.values('status')
        .annotate(total=Count('id'))
        .order_by('status')
    )
    
    # Distribuição de ações por usuário (Bar Chart)
    acoes_contrato = Acao.objects.filter(obrigacao__instrumento=instrumento)
    acoes_por_usuario = list(
        acoes_contrato.values('responsavel__first_name', 'responsavel__last_name')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    # Formata nome para o gráfico
    for item in acoes_por_usuario:
        nome_completo = f"{item['responsavel__first_name']} {item['responsavel__last_name']}".strip()
        item['usuario'] = nome_completo if nome_completo else "Não Atribuído"
    
    # Percentual de cada obrigação (Bar Chart)
    dados_percentual_obrigacoes = list(
        obrigacoes.values('titulo', 'percentual_atendimento')
        .order_by('-percentual_atendimento')
    )
    
    # Percentual de ações cumpridas para cada obrigação
    dados_acoes_cumpridas_obrigacao = []
    for obri in obrigacoes.prefetch_related('acoes'):
        acoes_obri = obri.acoes.all()
        total = acoes_obri.count()
        if total > 0:
            finalizadas = acoes_obri.filter(status='finalizado').count()
            percentual = (finalizadas / total) * 100
        else:
            percentual = 0
        dados_acoes_cumpridas_obrigacao.append({
            'titulo': obri.titulo,
            'percentual': round(float(percentual), 1)
        })
    
    # Minhas Ações filtradas por este contrato
    minhas_acoes = acoes_contrato.filter(
        Q(responsavel=usuario) | Q(executores=usuario)
    ).select_related(
        'obrigacao', 'tipo_acao', 'responsavel'
    ).distinct().order_by('-data_cadastro')
    
    context = {
        'instrumento': instrumento,
        'total_obrigacoes': total_obrigacoes,
        'obrigacoes_finalizadas': obrigacoes_finalizadas,
        'obrigacoes_em_andamento': obrigacoes_em_andamento,
        'obrigacoes_atrasadas': obrigacoes_atrasadas,
        'percentual_atendimento_contrato': percentual_atendimento_contrato,
        'obrigacoes_por_status': json.dumps(obrigacoes_por_status),
        'acoes_por_usuario': json.dumps(acoes_por_usuario),
        'dados_percentual_obrigacoes': json.dumps(dados_percentual_obrigacoes),
        'dados_acoes_cumpridas_obrigacao': json.dumps(dados_acoes_cumpridas_obrigacao),
        'minhas_acoes': minhas_acoes,
    }
    
    return render(request, 'dashboards/dashboard_contrato.html', context)
