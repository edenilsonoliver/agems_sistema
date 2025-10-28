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
    """
    Dashboard principal do sistema.
    
    CONFIGURAÇÃO ATUAL: Mostra TODAS as tarefas do sistema (visão geral)
    
    Para mudar para visão individual do usuário, substitua este arquivo por:
    views_OPCAO2_tarefas_usuario.py
    """
    from acoes.models import Acao, Tarefa
    
    usuario = request.user
    hoje = timezone.now().date()

    # Instrumentos vigentes
    total_instrumentos = Instrumento.objects.filter(status='vigente').count()

    # --- Distribuição de Instrumentos por Tipo ---
    instrumentos_por_tipo = list(
        Instrumento.objects
        .values('tipo_instrumento__nome')
        .annotate(total=Count('id'))
        .order_by('tipo_instrumento__nome')
    )

    # ✅ CORREÇÃO: Total de obrigações do SISTEMA (não apenas do usuário)
    total_obrigacoes = Obrigacao.objects.count()

    # ✅ CORREÇÃO: TODAS as tarefas do sistema (não filtrar por usuário)
    tarefas = Tarefa.objects.all()

    tarefas_vencidas = tarefas.filter(
        data_fim__lt=hoje, status__in=['a_iniciar', 'em_andamento']
    ).count()

    tarefas_a_vencer = tarefas.filter(
        data_fim__gte=hoje, data_fim__lte=hoje + timedelta(days=7),
        status__in=['a_iniciar', 'em_andamento']
    ).count()

    # ✅ Obrigações do usuário (através das ações)
    obrigacoes_usuario = Obrigacao.objects.filter(
        acoes__responsavel=usuario
    ).select_related(
        'instrumento',
        'tipo_obrigacao'
    ).prefetch_related(
        'acoes'
    ).distinct().order_by('-data_vencimento')[:10]
    
    # Ações recentes
    acoes_recentes = Acao.objects.select_related(
        'obrigacao', 'tipo_acao', 'responsavel'
    ).order_by('-data_cadastro')[:10]

    # Tarefas por status
    tarefas_por_status = list(
        tarefas.values('status')
        .annotate(total=Count('id'))
        .order_by('status')
    )

    # ✅ LOG para debug
    print(f"=== DEBUG DASHBOARD (TODAS AS TAREFAS DO SISTEMA) ===")
    print(f"Total de tarefas: {tarefas.count()}")
    print(f"Tarefas por status: {tarefas_por_status}")
    print(f"Tarefas vencidas: {tarefas_vencidas}")
    print(f"Tarefas a vencer: {tarefas_a_vencer}")
    print(f"Total de obrigações: {total_obrigacoes}")
    print(f"Instrumentos por tipo: {instrumentos_por_tipo}")
    print(f"======================================================")

    context = {
        'usuario': usuario,
        'total_instrumentos': total_instrumentos,
        'total_obrigacoes': total_obrigacoes,
        'instrumentos_por_tipo': json.dumps(instrumentos_por_tipo),
        'tarefas_por_status': json.dumps(tarefas_por_status),
        'tarefas_a_vencer': tarefas_a_vencer,
        'tarefas_vencidas': tarefas_vencidas,
        'obrigacoes_usuario': obrigacoes_usuario,  # ✅ Nova variável
        'acoes_recentes': acoes_recentes,
    }

    return render(request, 'dashboards/dashboard_modern.html', context)

