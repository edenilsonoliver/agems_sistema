from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Diretoria, TipoEntidade, TipoServico, TipoInstrumento, TipoObrigacao, TipoAcao


@login_required
def configuracoes(request):
    context = {
        'diretorias': Diretoria.objects.all(),
        'tipos_entidade': TipoEntidade.objects.all(),
        'tipos_servico': TipoServico.objects.all(),
        'tipos_instrumento': TipoInstrumento.objects.all(),
        'tipos_obrigacao': TipoObrigacao.objects.all(),
        'tipos_acao': TipoAcao.objects.all(),
    }
    return render(request, 'core/configuracoes.html', context)
