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


@login_required
def dashboard_principal(request):
    """
    Dashboard principal do sistema (Versão Unificada 4 Níveis).
    Exibe dados consolidados de Instrumentos, Obrigações e Ações.
    """
    usuario = request.user
    hoje = timezone.now().date()

    # Instrumentos vigentes
    total_instrumentos = Instrumento.objects.filter(status='vigente').count()

    # Distribuição de Instrumentos por Tipo
    instrumentos_por_tipo = list(
        Instrumento.objects
        .values('tipo_instrumento__nome')
        .annotate(total=Count('id'))
        .order_by('tipo_instrumento__nome')
    )

    # Total de obrigações do sistema
    total_obrigacoes = Obrigacao.objects.count()

    # Ações (Antigas tarefas) - Agora são o nível principal de execução
    acoes = Acao.objects.all()

    acoes_vencidas = acoes.filter(
        data_fim__lt=hoje, status__in=['a_iniciar', 'em_andamento', 'atrasado']
    ).count()

    acoes_a_vencer = acoes.filter(
        data_fim__gte=hoje, data_fim__lte=hoje + timedelta(days=7),
        status__in=['a_iniciar', 'em_andamento']
    ).count()

    # Obrigações recentes
    obrigacoes_recentes = Obrigacao.objects.select_related(
        'instrumento',
        'tipo_obrigacao'
    ).prefetch_related(
        'acoes'
    ).order_by('-data_vencimento')[:10]
    
    # Ações recentes (Antigas Tarefas)
    acoes_recentes = Acao.objects.select_related(
        'obrigacao', 'tipo_acao', 'responsavel'
    ).order_by('-data_cadastro')[:10]

    # Distribuição de Ações por status
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
        'tarefas_por_status': json.dumps(acoes_por_status), # Mantendo nome p/ compatibilidade JS no dashboard
        'tarefas_a_vencer': acoes_a_vencer,
        'tarefas_vencidas': acoes_vencidas,
        'obrigacoes_usuario': obrigacoes_recentes,
        'acoes_recentes': acoes_recentes,
    }

    return render(request, 'dashboards/dashboard_modern.html', context)
