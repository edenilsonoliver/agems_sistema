
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, permission_required
from .models import Acao, AcaoFoto
from .forms import AcaoFotoFormSet # Used only for validation if needed, but we used manual creation here

@login_required
@permission_required('acoes.change_acao', raise_exception=True)
@require_POST
def acao_foto_upload(request, pk):
    """
    Upload assíncrono de foto para uma Ação existente.
    """
    acao = get_object_or_404(Acao, pk=pk)
    
    if 'imagem' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'Nenhuma imagem enviada.'}, status=400)
    
    imagem = request.FILES['imagem']
    
    # 1. Validação de Extensão
    import os
    ext = os.path.splitext(imagem.name)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
        return JsonResponse({'success': False, 'error': 'Formato não permitido. Use apenas JPG, PNG ou WEBP.'}, status=400)

    # 2. Validação de Conteúdo (Simples)
    if not imagem.content_type.startswith('image/'):
        return JsonResponse({'success': False, 'error': 'O arquivo não é uma imagem.'}, status=400)
    
    nome = request.POST.get('nome', '')
    descricao = request.POST.get('descricao', '')
    coordenadas = request.POST.get('coordenadas', '')
    
    try:
        foto = AcaoFoto(
            acao=acao,
            imagem=imagem,
            legenda=nome or descricao, # Usar legenda em vez de nome/descricao (estavam ausentes no model?)
            coordenadas=coordenadas,
            usuario=request.user
        )
        foto.save()
        
        # Preparar dados de retorno
        timestamp_str = foto.timestamp.strftime('%d/%m/%Y %H:%M') if foto.timestamp else None
        created_at_str = foto.data_envio.strftime('%d/%m/%Y %H:%M')
        
        data = {
            'success': True,
            'foto': {
                'id': foto.id,
                'url': foto.imagem.url,
                'nome': foto.nome,
                'descricao': foto.descricao,
                'timestamp': timestamp_str,
                'created_at': created_at_str,
                'coordenadas': foto.coordenadas
            }
        }
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@permission_required('acoes.change_acao', raise_exception=True)
@require_POST
def acao_foto_delete(request, foto_id):
    """
    Exclusão assíncrona de foto.
    """
    foto = get_object_or_404(AcaoFoto, pk=foto_id)
    try:
        foto.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


from .models import AcaoDocumento

@login_required
@permission_required('acoes.change_acao', raise_exception=True)
@require_POST
def acao_documento_upload(request, pk):
    """
    Upload assíncrono de documento.
    """
    acao = get_object_or_404(Acao, pk=pk)
    
    if 'arquivo' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'Nenhum arquivo enviado.'}, status=400)
    
    arquivo = request.FILES['arquivo']
    descricao = request.POST.get('descricao', '')
    
    try:
        doc = AcaoDocumento(
            acao=acao,
            arquivo=arquivo,
            descricao=descricao,
            usuario=request.user
        )
        doc.save()
        
        # Preparar data para retorno
        data = {
            'success': True,
            'doc': {
                'id': doc.id,
                'url': doc.arquivo.url,
                'name': doc.arquivo.name.split('/')[-1], # Basename simples
                'descricao': doc.descricao,
                'created_at': doc.data_envio.strftime('%d/%m/%Y %H:%M')
            }
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@permission_required('acoes.change_acao', raise_exception=True)
@require_POST
def acao_documento_delete(request, doc_id):
    """
    Exclusão assíncrona de documento.
    """
    doc = get_object_or_404(AcaoDocumento, pk=doc_id)
    try:
        doc.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
