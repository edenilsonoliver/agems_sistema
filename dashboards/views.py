import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from instrumentos.models import Instrumento, Obrigacao
from indicadores.models import IndicadorContratual, ValorIndicador
from entidades.models import Entidade

# Aliases para compatibilidade
Contrato = Instrumento
ObrigacaoContratual = Obrigacao
Concessionaria = Entidade


@login_required
def dashboard_principal(request):
    """Dashboard principal do sistema."""
    from acoes.models import Acao, Tarefa
    
    usuario = request.user
    hoje = timezone.now().date()

    # Instrumentos vigentes (mantém igual)
    total_instrumentos = Instrumento.objects.filter(status='vigente').count()

    # --- Distribuição de Instrumentos por Tipo ---
    instrumentos_por_tipo = (
        Instrumento.objects
        .values('tipo_instrumento__nome')
        .annotate(total=Count('id'))
        .order_by('tipo_instrumento__nome')
    )

    # Total de obrigações relacionadas ao usuário
    total_obrigacoes = Obrigacao.objects.filter(
        acoes__responsavel=usuario
    ).distinct().count()

    # Tarefas do usuário
    tarefas = Tarefa.objects.filter(responsavel=usuario)

    tarefas_vencidas = tarefas.filter(
        data_fim__lt=hoje, status__in=['a_iniciar', 'em_andamento']
    ).count()

    tarefas_a_vencer = tarefas.filter(
        data_fim__gte=hoje, data_fim__lte=hoje + timedelta(days=7)
    ).count()

    # Ações recentes
    acoes_recentes = Acao.objects.select_related(
        'obrigacao', 'tipo_acao', 'responsavel'
    ).order_by('-data_cadastro')[:10]

    tarefas_por_status = (
        tarefas.values('status')
        .annotate(total=Count('id'))
        .order_by('status')
    )

    context = {
        'usuario': usuario,
        'total_instrumentos': total_instrumentos,
        'total_obrigacoes': total_obrigacoes,
        'instrumentos_por_tipo': json.dumps(list(instrumentos_por_tipo)),
        'tarefas_por_status': json.dumps(list(tarefas_por_status)),
        'tarefas_a_vencer': tarefas_a_vencer,
        'tarefas_vencidas': tarefas_vencidas,
        'acoes_recentes': acoes_recentes,
    }

    return render(request, 'dashboards/dashboard_modern.html', context)
