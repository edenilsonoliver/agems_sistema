from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Acao

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
