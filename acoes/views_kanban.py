from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q

from .models import Acao
from .forms import AcaoForm, ChecklistItemFormSet


@login_required
def acao_kanban_view(request):
    """
    View para visualização Kanban das Ações.
    """
    acoes = Acao.objects.select_related(
        'obrigacao',
        'responsavel'
    ).prefetch_related(
        'executores',
        'checklist_itens'
    ).order_by('-data_cadastro')
    
    # Preparar dados para JSON
    acoes_json = []
    for acao in acoes:
        # Contar itens do checklist
        checklist_total = acao.checklist_itens.count()
        checklist_concluidos = acao.checklist_itens.filter(concluido=True).count()
        
        acoes_json.append({
            'id': acao.id,
            'nome': acao.nome,
            'status': acao.status,
            'responsavel': acao.responsavel.get_full_name() if acao.responsavel else '-',
            'data_fim': acao.data_fim.strftime('%d/%m/%Y') if acao.data_fim else None,
            'percentual_cumprido': acao.percentual_cumprido,
            'obrigacao': acao.obrigacao.titulo if acao.obrigacao else None,
            'checklist_total': checklist_total,
            'checklist_concluidos': checklist_concluidos,
        })
    
    context = {
        'tarefas_json': acoes_json, 
        'status_choices': Acao.STATUS_CHOICES,
    }
    
    return render(request, 'acoes/acao_kanban.html', context)


@login_required
@require_POST
def acao_update_status(request, pk):
    """
    View para atualizar o status de uma ação via AJAX (drag & drop).
    """
    import json
    
    try:
        acao = get_object_or_404(Acao, pk=pk)
        data = json.loads(request.body)
        new_status = data.get('status')
        
        valid_statuses = ['a_iniciar', 'em_andamento', 'atrasado', 'em_validacao', 'finalizado']
        if new_status not in valid_statuses:
            return JsonResponse({
                'success': False,
                'error': f'Status inválido: {new_status}'
            }, status=400)
        
        old_status = acao.status
        acao.status = new_status
        acao.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Status atualizado de {old_status} para {new_status}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def acao_edit_ajax(request, pk):
    """
    View para carregar e processar o formulário de edição via AJAX no modal do Kanban.
    """
    acao = get_object_or_404(Acao, pk=pk)
    
    if request.method == 'POST':
        form = AcaoForm(request.POST, instance=acao)
        checklist_formset = ChecklistItemFormSet(
            request.POST,
            instance=acao,
            prefix='checklist_itens'
        )
        
        if form.is_valid() and checklist_formset.is_valid():
            acao = form.save()
            checklist_formset.instance = acao
            checklist_formset.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            from django.shortcuts import redirect
            return redirect('acao_kanban')
        else:
            context = {
                'acao': acao,
                'form': form,
                'checklist_formset': checklist_formset,
                'is_ajax': True,
            }
            return render(request, 'acoes/acao_form_modal.html', context)
    
    else:
        form = AcaoForm(instance=acao)
        checklist_formset = ChecklistItemFormSet(
            instance=acao,
            prefix='checklist_itens'
        )
        
        context = {
            'acao': acao,
            'form': form,
            'checklist_formset': checklist_formset,
            'is_ajax': True,
        }
        return render(request, 'acoes/acao_form_modal.html', context)
