# --- ALERTAS ---
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from acoes.models import Tarefa

@login_required
def alertas_usuario(request):
    """Retorna os alertas do usuário logado"""
    hoje = timezone.now().date()
    user = request.user

    tarefas = Tarefa.objects.filter(responsavel=user)

    atrasadas = tarefas.filter(data_fim__lt=hoje, status__in=['a_iniciar', 'em_andamento'])
    a_vencer = tarefas.filter(data_fim__gte=hoje, data_fim__lte=hoje + timezone.timedelta(days=7))
    novas = tarefas.filter(data_cadastro__gte=timezone.now() - timezone.timedelta(days=3))

    data = {
        "total": atrasadas.count() + a_vencer.count() + novas.count(),
        "atrasadas": list(atrasadas.values("id", "nome", "data_fim")),
        "a_vencer": list(a_vencer.values("id", "nome", "data_fim")),
        "novas": list(novas.values("id", "nome", "data_cadastro")),
    }
    return JsonResponse(data)
