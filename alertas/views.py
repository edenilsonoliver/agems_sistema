# ===== SISTEMA DE ALERTAS - VERSÃO 2: SISTEMA COMPLETO =====
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

from acoes.models import Tarefa
from instrumentos.models import Obrigacao
from .models import Notificacao, PreferenciaNotificacao


@login_required
def alertas_usuario(request):
    """
    Retorna os alertas do usuário logado
    
    VERSÃO 2: Sistema Completo com Notificações Persistidas
    """
    user = request.user
    
    # Buscar notificações não lidas
    notificacoes = Notificacao.objects.filter(
        usuario=user,
        lida=False
    ).order_by('-prioridade', '-data_criacao')[:50]  # Limitar a 50
    
    # Agrupar por tipo
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
    
    # Retornar JSON
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
    """Marca uma notificação como lida"""
    notificacao = get_object_or_404(
        Notificacao,
        id=notificacao_id,
        usuario=request.user
    )
    
    notificacao.marcar_como_lida()
    
    return JsonResponse({'success': True})


@login_required
@require_POST
def marcar_todas_como_lidas(request):
    """Marca todas as notificações do usuário como lidas"""
    count = Notificacao.objects.filter(
        usuario=request.user,
        lida=False
    ).update(
        lida=True,
        data_leitura=timezone.now()
    )
    
    return JsonResponse({
        'success': True,
        'count': count
    })


@login_required
def historico_notificacoes(request):
    """Retorna histórico de notificações (incluindo lidas)"""
    user = request.user
    
    # Filtros
    tipo = request.GET.get('tipo')
    lidas = request.GET.get('lidas', 'todas')  # 'sim', 'nao', 'todas'
    limite = int(request.GET.get('limite', 100))
    
    # Query base
    notificacoes = Notificacao.objects.filter(usuario=user)
    
    # Aplicar filtros
    if tipo:
        notificacoes = notificacoes.filter(tipo=tipo)
    
    if lidas == 'sim':
        notificacoes = notificacoes.filter(lida=True)
    elif lidas == 'nao':
        notificacoes = notificacoes.filter(lida=False)
    
    # Ordenar e limitar
    notificacoes = notificacoes.order_by('-data_criacao')[:limite]
    
    # Formatar
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
    """Retorna ou atualiza preferências de notificação do usuário"""
    user = request.user
    
    # Buscar ou criar preferências
    prefs, created = PreferenciaNotificacao.objects.get_or_create(usuario=user)
    
    if request.method == 'POST':
        # Atualizar preferências
        prefs.notificar_tarefa_atrasada = request.POST.get('notificar_tarefa_atrasada') == 'true'
        prefs.notificar_tarefa_vencendo = request.POST.get('notificar_tarefa_vencendo') == 'true'
        prefs.notificar_tarefa_nova = request.POST.get('notificar_tarefa_nova') == 'true'
        prefs.notificar_obrigacao = request.POST.get('notificar_obrigacao') == 'true'
        prefs.notificar_comentario = request.POST.get('notificar_comentario') == 'true'
        prefs.enviar_email = request.POST.get('enviar_email') == 'true'
        prefs.frequencia_email = request.POST.get('frequencia_email', 'diario')
        prefs.tocar_som = request.POST.get('tocar_som') == 'true'
        prefs.mostrar_toast = request.POST.get('mostrar_toast') == 'true'
        prefs.save()
        
        return JsonResponse({'success': True})
    
    # GET: Retornar preferências
    data = {
        'notificar_tarefa_atrasada': prefs.notificar_tarefa_atrasada,
        'notificar_tarefa_vencendo': prefs.notificar_tarefa_vencendo,
        'notificar_tarefa_nova': prefs.notificar_tarefa_nova,
        'notificar_obrigacao': prefs.notificar_obrigacao,
        'notificar_comentario': prefs.notificar_comentario,
        'enviar_email': prefs.enviar_email,
        'frequencia_email': prefs.frequencia_email,
        'tocar_som': prefs.tocar_som,
        'mostrar_toast': prefs.mostrar_toast,
    }
    
    return JsonResponse(data)


# ===== FUNÇÕES AUXILIARES PARA CRIAR NOTIFICAÇÕES =====

def criar_notificacao_tarefa_atrasada(tarefa, usuario):
    """Cria notificação de tarefa atrasada"""
    dias_atraso = (timezone.now().date() - tarefa.data_fim).days if tarefa.data_fim else 0
    
    return Notificacao.criar_notificacao(
        usuario=usuario,
        tipo='tarefa_atrasada',
        titulo=f'Tarefa atrasada: {tarefa.nome}',
        mensagem=f'Esta tarefa está atrasada há {dias_atraso} dias.',
        link=f'/tarefas/{tarefa.id}/editar/',
        tarefa_id=tarefa.id,
        prioridade='alta' if dias_atraso > 7 else 'media',
    )


def criar_notificacao_tarefa_vencendo_hoje(tarefa, usuario):
    """Cria notificação de tarefa vencendo hoje"""
    return Notificacao.criar_notificacao(
        usuario=usuario,
        tipo='tarefa_vencendo_hoje',
        titulo=f'Tarefa vence hoje: {tarefa.nome}',
        mensagem='Esta tarefa vence hoje! Não esqueça de concluí-la.',
        link=f'/tarefas/{tarefa.id}/editar/',
        tarefa_id=tarefa.id,
        prioridade='urgente',
    )


def criar_notificacao_tarefa_a_vencer(tarefa, usuario):
    """Cria notificação de tarefa a vencer"""
    dias_restantes = (tarefa.data_fim - timezone.now().date()).days if tarefa.data_fim else 0
    
    return Notificacao.criar_notificacao(
        usuario=usuario,
        tipo='tarefa_a_vencer',
        titulo=f'Tarefa a vencer: {tarefa.nome}',
        mensagem=f'Esta tarefa vence em {dias_restantes} dias.',
        link=f'/tarefas/{tarefa.id}/editar/',
        tarefa_id=tarefa.id,
        prioridade='media',
    )


def criar_notificacao_obrigacao_vencendo(obrigacao, usuario):
    """Cria notificação de obrigação vencendo"""
    dias_restantes = (obrigacao.data_vencimento - timezone.now().date()).days if obrigacao.data_vencimento else 0
    
    return Notificacao.criar_notificacao(
        usuario=usuario,
        tipo='obrigacao_vencendo',
        titulo=f'Obrigação vencendo: {obrigacao.titulo}',
        mensagem=f'Esta obrigação vence em {dias_restantes} dias.',
        link=f'/instrumentos/{obrigacao.instrumento_id}/editar/' if obrigacao.instrumento_id else '#',
        obrigacao_id=obrigacao.id,
        prioridade='alta' if dias_restantes <= 3 else 'media',
    )


def criar_notificacao_tarefa_nova(tarefa, usuario):
    """Cria notificação de nova tarefa atribuída"""
    return Notificacao.criar_notificacao(
        usuario=usuario,
        tipo='tarefa_nova',
        titulo=f'Nova tarefa atribuída: {tarefa.nome}',
        mensagem=f'Você foi atribuído como responsável/executor desta tarefa.',
        link=f'/tarefas/{tarefa.id}/editar/',
        tarefa_id=tarefa.id,
        prioridade='media',
    )

