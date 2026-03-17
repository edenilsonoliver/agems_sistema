import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

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
