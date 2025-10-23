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
    from acoes.models import Acao
    
    usuario = request.user
    total_instrumentos = Instrumento.objects.filter(status='vigente').count()
    total_entidades = Entidade.objects.filter(status='ativa').count()
    total_indicadores = IndicadorContratual.objects.filter(ativo=True).count()
    
    hoje = timezone.now().date()
    obrigacoes_pendentes = Obrigacao.objects.filter(
        cumprida=False, data_vencimento__gte=hoje
    ).select_related('instrumento', 'tipo_obrigacao').order_by('data_vencimento')[:10]
    
    obrigacoes_pendentes_count = Obrigacao.objects.filter(
        cumprida=False, data_vencimento__gte=hoje
    ).count()
    
    obrigacoes_vencidas = Obrigacao.objects.filter(
        cumprida=False, data_vencimento__lt=hoje
    ).count()
    
    data_limite = hoje + timedelta(days=90)
    instrumentos_vencimento = Instrumento.objects.filter(
        status='vigente', data_fim__lte=data_limite, data_fim__gte=hoje
    ).order_by('data_fim')
    
    # Ações recentes
    acoes_recentes = Acao.objects.select_related(
        'obrigacao', 'tipo_acao', 'responsavel'
    ).order_by('-data_cadastro')[:10]
    
    context = {
        'total_instrumentos': total_instrumentos,
        'total_entidades': total_entidades,
        'total_indicadores': total_indicadores,
        'obrigacoes_pendentes': obrigacoes_pendentes,
        'obrigacoes_pendentes_count': obrigacoes_pendentes_count,
        'obrigacoes_vencidas': obrigacoes_vencidas,
        'instrumentos_vencimento': instrumentos_vencimento,
        'acoes_recentes': acoes_recentes,
        'usuario': usuario,
    }
    
    return render(request, 'dashboards/dashboard_modern.html', context)
