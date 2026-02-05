# ===== SISTEMA DE ALERTAS - VERSÃO 2: SISTEMA COMPLETO =====
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

from acoes.models import Acao
from instrumentos.models import Obrigacao
from .models import Notificacao, PreferenciaNotificacao


@login_required
def alertas_usuario(request):
    """
    Retorna os alertas do usuário logado
    """
    user = request.user
    
    # Buscar notificações não lidas
    notificacoes = Notificacao.objects.filter(
        usuario=user,
        lida=False
    ).order_by('-prioridade', '-data_criacao')[:50]
    
    por_tipo = {}
    for notif in notificacoes:
        tipo = notif.tipo
        if tipo not in por_tipo:
            por_tipo[tipo] = []
        
        por_tipo[tipo].append({
            'id': notif.id,
            'titulo': notif.titulo,
            'mensagem': notif.mensagem,
            'link': notif.link,
            'prioridade': notif.prioridade,
            'data_criacao': notif.data_criacao.strftime('%d/%m/%Y %H:%M'),
            'tipo': notif.get_tipo_display(),
        })
    
    data = {
        'total': notificacoes.count(),
        'notificacoes': por_tipo,
        'todas': [
            {
                'id': n.id,
                'titulo': n.titulo,
                'mensagem': n.mensagem,
                'link': n.link,
                'prioridade': n.prioridade,
                'tipo': n.get_tipo_display(),
                'data_criacao': n.data_criacao.strftime('%d/%m/%Y %H:%M'),
            }
            for n in notificacoes
        ]
    }
    
    return JsonResponse(data)


@login_required
@require_POST
def marcar_como_lida(request, notificacao_id):
    notificacao = get_object_or_404(Notificacao, id=notificacao_id, usuario=request.user)
    notificacao.marcar_como_lida()
    return JsonResponse({'success': True})


@login_required
@require_POST
def marcar_todas_como_lidas(request):
    count = Notificacao.objects.filter(usuario=request.user, lida=False).update(
        lida=True,
        data_leitura=timezone.now()
    )
    return JsonResponse({'success': True, 'count': count})


@login_required
def historico_notificacoes(request):
    user = request.user
    tipo = request.GET.get('tipo')
    lidas = request.GET.get('lidas', 'todas')
    limite = int(request.GET.get('limite', 100))
    
    notificacoes = Notificacao.objects.filter(usuario=user)
    if tipo:
        notificacoes = notificacoes.filter(tipo=tipo)
    if lidas == 'sim':
        notificacoes = notificacoes.filter(lida=True)
    elif lidas == 'nao':
        notificacoes = notificacoes.filter(lida=False)
    
    notificacoes = notificacoes.order_by('-data_criacao')[:limite]
    
    data = {
        'total': notificacoes.count(),
        'notificacoes': [
            {
                'id': n.id,
                'titulo': n.titulo,
                'mensagem': n.mensagem,
                'link': n.link,
                'tipo': n.get_tipo_display(),
                'prioridade': n.prioridade,
                'lida': n.lida,
                'data_criacao': n.data_criacao.strftime('%d/%m/%Y %H:%M'),
                'data_leitura': n.data_leitura.strftime('%d/%m/%Y %H:%M') if n.data_leitura else None,
            }
            for n in notificacoes
        ]
    }
    return JsonResponse(data)


@login_required
def preferencias_notificacao(request):
    user = request.user
    prefs, created = PreferenciaNotificacao.objects.get_or_create(usuario=user)
    
    if request.method == 'POST':
        prefs.notificar_acao_atrasada = request.POST.get('notificar_acao_atrasada') == 'true'
        prefs.notificar_acao_vencendo = request.POST.get('notificar_acao_vencendo') == 'true'
        prefs.notificar_acao_nova = request.POST.get('notificar_acao_nova') == 'true'
        prefs.notificar_obrigacao = request.POST.get('notificar_obrigacao') == 'true'
        prefs.notificar_comentario = request.POST.get('notificar_comentario') == 'true'
        prefs.enviar_email = request.POST.get('enviar_email') == 'true'
        prefs.frequencia_email = request.POST.get('frequencia_email', 'diario')
        prefs.tocar_som = request.POST.get('tocar_som') == 'true'
        prefs.mostrar_toast = request.POST.get('mostrar_toast') == 'true'
        prefs.save()
        return JsonResponse({'success': True})
    
    data = {
        'notificar_acao_atrasada': prefs.notificar_acao_atrasada,
        'notificar_acao_vencendo': prefs.notificar_acao_vencendo,
        'notificar_acao_nova': prefs.notificar_acao_nova,
        'notificar_obrigacao': prefs.notificar_obrigacao,
        'notificar_comentario': prefs.notificar_comentario,
        'enviar_email': prefs.enviar_email,
        'frequencia_email': prefs.frequencia_email,
        'tocar_som': prefs.tocar_som,
        'mostrar_toast': prefs.mostrar_toast,
    }
    return JsonResponse(data)


# ===== FUNÇÕES AUXILIARES =====

def criar_notificacao_acao_atrasada(acao, usuario):
    dias_atraso = (timezone.now().date() - acao.data_fim).days if acao.data_fim else 0
    return Notificacao.criar_notificacao(
        usuario=usuario,
        tipo='acao_atrasada',
        titulo=f'Ação atrasada: {acao.nome}',
        mensagem=f'Esta ação está atrasada há {dias_atraso} dias.',
        link=f'/acoes/{acao.id}/editar/',
        acao_id=acao.id,
        prioridade='alta' if dias_atraso > 7 else 'media',
    )

def criar_notificacao_acao_vencendo_hoje(acao, usuario):
    return Notificacao.criar_notificacao(
        usuario=usuario,
        tipo='acao_vencendo_hoje',
        titulo=f'Ação vence hoje: {acao.nome}',
        mensagem='Esta ação vence hoje!',
        link=f'/acoes/{acao.id}/editar/',
        acao_id=acao.id,
        prioridade='urgente',
    )

def criar_notificacao_acao_a_vencer(acao, usuario):
    dias_restantes = (acao.data_fim - timezone.now().date()).days if acao.data_fim else 0
    return Notificacao.criar_notificacao(
        usuario=usuario,
        tipo='acao_a_vencer',
        titulo=f'Ação a vencer: {acao.nome}',
        mensagem=f'Esta ação vence em {dias_restantes} dias.',
        link=f'/acoes/{acao.id}/editar/',
        acao_id=acao.id,
        prioridade='media',
    )

def criar_notificacao_obrigacao_vencendo(obrigacao, usuario):
    dias_restantes = (obrigacao.data_vencimento - timezone.now().date()).days if obrigacao.data_vencimento else 0
    return Notificacao.criar_notificacao(
        usuario=usuario,
        tipo='obrigacao_vencendo',
        titulo=f'Obrigação vencendo: {obrigacao.titulo}',
        mensagem=f'Esta obrigação vence em {dias_restantes} dias.',
        link=f'/instrumentos/{obrigacao.instrumento_id}/editar/',
        obrigacao_id=obrigacao.id,
        prioridade='alta' if dias_restantes <= 3 else 'media',
    )

def criar_notificacao_acao_nova(acao, usuario):
    return Notificacao.criar_notificacao(
        usuario=usuario,
        tipo='acao_nova',
        titulo=f'Nova ação atribuída: {acao.nome}',
        mensagem=f'Você foi atribuído como responsável desta ação.',
        link=f'/acoes/{acao.id}/editar/',
        acao_id=acao.id,
        prioridade='media',
    )
