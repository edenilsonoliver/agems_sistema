from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q

from .models import Tarefa
from .forms import TarefaForm, ChecklistItemFormSet


@login_required
def tarefa_kanban_view(request):
    """
    View para visualização Kanban das tarefas.
    
    Configuração: Mostra TODAS as tarefas do sistema (visão geral)
    Para filtrar por usuário, descomente a linha comentada abaixo.
    """
    # ✅ OPÇÃO 1: Todas as tarefas do sistema
    tarefas = Tarefa.objects.select_related(
        'acao',
        'responsavel'
    ).prefetch_related(
        'executores',
        'checklist_itens'
    ).order_by('-data_cadastro')
    
    # ✅ OPÇÃO 2: Apenas tarefas do usuário (descomente se quiser)
    # tarefas = Tarefa.objects.filter(
    #     Q(responsavel=request.user) | Q(executores=request.user)
    # ).select_related(
    #     'acao',
    #     'responsavel'
    # ).prefetch_related(
    #     'executores',
    #     'checklist_itens'
    # ).distinct().order_by('-data_cadastro')
    
    # Preparar dados para JSON
    tarefas_json = []
    for tarefa in tarefas:
        # Contar itens do checklist
        checklist_total = tarefa.checklist_itens.count()
        checklist_concluidos = tarefa.checklist_itens.filter(concluido=True).count()
        
        tarefas_json.append({
            'id': tarefa.id,
            'nome': tarefa.nome,
            'status': tarefa.status,
            'responsavel': tarefa.responsavel.get_full_name() if tarefa.responsavel else '-',
            'data_fim': tarefa.data_fim.strftime('%d/%m/%Y') if tarefa.data_fim else None,
            'percentual_cumprido': tarefa.percentual_cumprido,
            'acao': tarefa.acao.nome if tarefa.acao else None,
            'checklist_total': checklist_total,
            'checklist_concluidos': checklist_concluidos,
        })
    
    context = {
        'tarefas_json': tarefas_json,
    }
    
    return render(request, 'acoes/tarefa_kanban.html', context)


@login_required
@require_POST
def tarefa_update_status(request, pk):
    """
    View para atualizar o status de uma tarefa via AJAX (drag & drop).
    
    Recebe JSON com o novo status e atualiza no banco.
    """
    import json
    
    try:
        tarefa = get_object_or_404(Tarefa, pk=pk)
        data = json.loads(request.body)
        new_status = data.get('status')
        
        # Validar status
        valid_statuses = ['a_iniciar', 'em_andamento', 'atrasado', 'em_validacao', 'finalizado']
        if new_status not in valid_statuses:
            return JsonResponse({
                'success': False,
                'error': f'Status inválido: {new_status}'
            }, status=400)
        
        # Atualizar status
        old_status = tarefa.status
        tarefa.status = new_status
        tarefa.save()
        
        # Log para debug
        print(f"======================================================")
        print(f"Tarefa #{tarefa.id} '{tarefa.nome}' mudou de '{old_status}' para '{new_status}'")
        print(f"======================================================")
        
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
def tarefa_edit_ajax(request, pk):
    """
    View para carregar e processar o formulário de edição via AJAX no modal.
    
    GET: Retorna HTML do formulário
    POST: Processa o formulário e retorna sucesso/erro
    """
    tarefa = get_object_or_404(Tarefa, pk=pk)
    
    if request.method == 'POST':
        # Processar formulário
        form = TarefaForm(request.POST, instance=tarefa)
        checklist_formset = ChecklistItemFormSet(
            request.POST,
            instance=tarefa,
            prefix='checklist_itens'
        )
        
        if form.is_valid() and checklist_formset.is_valid():
            # Salvar tarefa
            tarefa = form.save(commit=False)
            tarefa.save()
            form.save_m2m()  # Salvar M2M (executores)
            
            # Salvar checklist
            checklist_formset.instance = tarefa
            checklist_formset.save()
            
            # Se for AJAX, retornar JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            # Senão, redirecionar
            from django.shortcuts import redirect
            return redirect('tarefa_kanban')
        else:
            # Se houver erros, renderizar formulário com erros
            context = {
                'tarefa': tarefa,
                'form': form,
                'checklist_formset': checklist_formset,
                'is_ajax': True,
            }
            return render(request, 'acoes/tarefa_form_modal.html', context)
    
    else:
        # GET: Carregar formulário
        form = TarefaForm(instance=tarefa)
        checklist_formset = ChecklistItemFormSet(
            instance=tarefa,
            prefix='checklist_itens'
        )
        
        context = {
            'tarefa': tarefa,
            'form': form,
            'checklist_formset': checklist_formset,
            'is_ajax': True,
        }
        return render(request, 'acoes/tarefa_form_modal.html', context)

