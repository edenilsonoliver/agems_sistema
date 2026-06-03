from celery import shared_task
from django.utils import timezone
from .models import Endpoint, FonteDados
from .services import IntegradorAPI
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def sincronizar_endpoint_task(self, endpoint_id):
    """
    Tarefa Celery para sincronizar um endpoint específico (RF004).
    Possui retry automático em caso de falha de conexão.
    """
    logger.info(f"Iniciando sincronização automática do endpoint ID {endpoint_id}")
    try:
        integrador = IntegradorAPI(endpoint_id)
        snapshot = integrador.sincronizar()
        
        if snapshot.status == 'erro':
            logger.warning(f"Erro na sincronização do endpoint {endpoint_id}: {snapshot.log_erro}")
            # Tenta novamente em 5 minutos em caso de erro
            raise self.retry(countdown=300)
            
        logger.info(f"Sincronização concluída com sucesso para o endpoint {endpoint_id}")
        return f"Snapshot {snapshot.id} criado com {snapshot.quantidade_registros} registros."
        
    except Endpoint.DoesNotExist:
        logger.error(f"Endpoint ID {endpoint_id} não encontrado.")
    except Exception as exc:
        logger.error(f"Exceção inesperada na sincronização: {exc}")
        # Retry para erros de rede ou timeouts que possam ter escapado do request
        raise self.retry(exc=exc, countdown=300)

@shared_task
def agendar_sincronizacoes_ativas():
    """
    Tarefa que verifica quais endpoints precisam ser sincronizados com base na frequência.
    Pode ser chamada pelo Celery Beat a cada 5 minutos.
    """
    # Encontra todos os endpoints ativos cujas fontes também estão ativas
    endpoints_ativos = Endpoint.objects.filter(ativo=True, fonte__status_integracao=True)
    
    agendados = 0
    for endpoint in endpoints_ativos:
        # A lógica real verificaria o último Snapshot e a frequencia_minutos.
        # Para simplificar, estamos agendando todos os ativos.
        # Numa implementação completa, comparar (timezone.now() - ultimo_snapshot.data_hora) > frequencia_minutos
        
        ultimo_snapshot = endpoint.snapshots.order_by('-data_hora').first()
        precisa_sincronizar = False
        
        if not ultimo_snapshot:
            precisa_sincronizar = True
        else:
            delta = timezone.now() - ultimo_snapshot.data_hora
            if delta.total_seconds() / 60 >= endpoint.fonte.frequencia_minutos:
                precisa_sincronizar = True
                
        if precisa_sincronizar:
            sincronizar_endpoint_task.delay(endpoint.id)
            agendados += 1
            
    return f"{agendados} endpoints agendados para sincronização."
