from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Diretoria, TipoEntidade, TipoServico, TipoInstrumento, TipoObrigacao, TipoAcao, Subunidade

User = get_user_model()


from acoes.models import ConformidadeTemplate

@login_required
def configuracoes(request):
    # Apenas administradores (Perfil 0) podem acessar
    if request.user.perfil != 0:
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, "Acesso negado: apenas administradores podem acessar as configurações globais.")
        return redirect('dashboard')

    context = {
        'diretorias': Diretoria.objects.all(),
        'subunidades': Subunidade.objects.select_related('diretoria').all()[:5], # Listar apenas as 5 primeiras para não poluir
        'tipos_entidade': TipoEntidade.objects.all(),
        'tipos_servico': TipoServico.objects.all(),
        'tipos_instrumento': TipoInstrumento.objects.all(),
        'tipos_obrigacao': TipoObrigacao.objects.all(),
        'tipos_acao': TipoAcao.objects.all(),
        'conformidade_templates': ConformidadeTemplate.objects.filter(ativo=True),
        # Estatísticas de usuários
        'total_usuarios': User.objects.count(),
        'usuarios_ativos': User.objects.filter(is_active=True).count(),
    }
    return render(request, 'core/configuracoes.html', context)
