# ===== SISTEMA DE ALERTAS - VERSÃO 1: CORREÇÃO RÁPIDA =====
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from acoes.models import Tarefa
from instrumentos.models import Obrigacao


@login_required
def alertas_usuario(request):
    """
    Retorna os alertas do usuário logado
    
    VERSÃO 1: Correção Rápida
    - Corrige lógica de filtragem
    - Adiciona "vence hoje"
    - Inclui tarefas como executor
    - Formata datas corretamente
    - Adiciona obrigações
    """
    hoje = timezone.now().date()
    amanha = hoje + timezone.timedelta(days=1)
    proxima_semana = hoje + timezone.timedelta(days=7)
    user = request.user

    # ===== TAREFAS =====
    # Incluir tarefas onde usuário é responsável OU executor
    tarefas = Tarefa.objects.filter(
        Q(responsavel=user) | Q(executores=user)
    ).select_related('acao', 'responsavel').distinct()

    # 1. Tarefas ATRASADAS (vencimento passou)
    atrasadas = tarefas.filter(
        data_fim__lt=hoje,
        status__in=['a_iniciar', 'em_andamento', 'atrasado']
    ).order_by('data_fim')

    # 2. Tarefas VENCENDO HOJE (urgente!)
    vencendo_hoje = tarefas.filter(
        data_fim=hoje,
        status__in=['a_iniciar', 'em_andamento']
    ).order_by('data_fim')

    # 3. Tarefas A VENCER (amanhã até 7 dias)
    a_vencer = tarefas.filter(
        data_fim__gte=amanha,
        data_fim__lte=proxima_semana,
        status__in=['a_iniciar', 'em_andamento']
    ).order_by('data_fim')

    # 4. Tarefas NOVAS (criadas nos últimos 3 dias E não finalizadas)
    novas = tarefas.filter(
        data_cadastro__gte=timezone.now() - timezone.timedelta(days=3),
        status__in=['a_iniciar', 'em_andamento', 'atrasado']
    ).order_by('-data_cadastro')

    # ===== OBRIGAÇÕES =====
    # Obrigações vencendo (onde usuário é responsável pela ação)
    obrigacoes_vencendo = Obrigacao.objects.filter(
        acoes__responsavel=user,
        data_vencimento__lte=proxima_semana,
        data_vencimento__gte=hoje,
        status='pendente'
    ).select_related('instrumento', 'tipo_obrigacao').distinct().order_by('data_vencimento')

    # ===== FORMATAR DADOS =====
    def formatar_tarefa(t):
        """Formata tarefa para JSON com data legível"""
        dias_atraso = 0
        if t.data_fim and t.data_fim < hoje:
            dias_atraso = (hoje - t.data_fim).days
        
        return {
            "id": t.id,
            "nome": t.nome,
            "data_fim": t.data_fim.strftime('%d/%m/%Y') if t.data_fim else None,
            "data_fim_iso": t.data_fim.isoformat() if t.data_fim else None,
            "dias_atraso": dias_atraso,
            "status": t.get_status_display(),
            "acao": t.acao.nome if t.acao else None,
            "responsavel": t.responsavel.get_full_name() if t.responsavel else None,
        }

    def formatar_obrigacao(o):
        """Formata obrigação para JSON"""
        return {
            "id": o.id,
            "titulo": o.titulo,
            "data_vencimento": o.data_vencimento.strftime('%d/%m/%Y') if o.data_vencimento else None,
            "data_vencimento_iso": o.data_vencimento.isoformat() if o.data_vencimento else None,
            "instrumento": o.instrumento.numero if o.instrumento else None,
            "tipo": o.tipo_obrigacao.nome if o.tipo_obrigacao else None,
        }

    # ===== CALCULAR TOTAL =====
    total = (
        atrasadas.count() + 
        vencendo_hoje.count() + 
        a_vencer.count() + 
        novas.count() + 
        obrigacoes_vencendo.count()
    )

    # ===== RETORNAR JSON =====
    data = {
        "total": total,
        "atrasadas": [formatar_tarefa(t) for t in atrasadas[:10]],  # Limitar a 10
        "vencendo_hoje": [formatar_tarefa(t) for t in vencendo_hoje[:10]],
        "a_vencer": [formatar_tarefa(t) for t in a_vencer[:10]],
        "novas": [formatar_tarefa(t) for t in novas[:5]],  # Limitar a 5
        "obrigacoes": [formatar_obrigacao(o) for o in obrigacoes_vencendo[:10]],
    }

    return JsonResponse(data)

