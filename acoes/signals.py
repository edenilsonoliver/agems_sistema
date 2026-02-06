import os
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Acao, AcaoFoto, AcaoDocumento

logger = logging.getLogger(__name__)

def _remover_arquivo_fisico(instance, field_name):
    """
    Utilitário para remover fisicamente um arquivo do disco.
    """
    try:
        arquivo_field = getattr(instance, field_name)
        if arquivo_field and hasattr(arquivo_field, 'path'):
            if os.path.isfile(arquivo_field.path):
                os.remove(arquivo_field.path)
    except Exception as e:
        logger.error(f"Erro ao tentar remover arquivo físico do disco ({getattr(instance, 'pk', 'sem pk')}): {str(e)}")

@receiver(post_save, sender=Acao)
def atualizar_status_obrigacao_save(sender, instance, **kwargs):
    """
    Sempre que uma ação for salva, atualiza o status da obrigação pai.
    """
    if instance.obrigacao:
        instance.obrigacao.atualizar_status_por_acoes()

@receiver(post_delete, sender=Acao)
def atualizar_status_obrigacao_delete(sender, instance, **kwargs):
    """
    Sempre que uma ação for removida, atualiza o status da obrigação pai.
    """
    if instance.obrigacao:
        instance.obrigacao.atualizar_status_por_acoes()

@receiver(post_delete, sender=AcaoFoto)
def remover_arquivo_foto_post_delete(sender, instance, **kwargs):
    """
    Remove o arquivo físico da imagem após o registro da foto ser deletado.
    Disparado também em cascata quando a Ação pai é deletada.
    """
    if instance.imagem:
        _remover_arquivo_fisico(instance, 'imagem')

@receiver(post_delete, sender=AcaoDocumento)
def remover_arquivo_doc_post_delete(sender, instance, **kwargs):
    """
    Remove o arquivo físico do documento após o registro ser deletado.
    Disparado também em cascata quando a Ação pai é deletada.
    """
    if instance.arquivo:
        _remover_arquivo_fisico(instance, 'arquivo')
