from django.utils import timezone
from .models import Snapshot, Dataset

class DatasetService:
    """
    Serviço responsável por transformar dados brutos (Snapshots)
    em Datasets estruturados (RF006), prontos para análise e governança.
    """

    @staticmethod
    def processar_snapshot(snapshot_id, nome_dataset=None, descricao='', responsavel=None):
        """
        Gera ou atualiza um Dataset com base no payload de um Snapshot de sucesso.
        """
        snapshot = Snapshot.objects.select_related('endpoint', 'endpoint__fonte', 'endpoint__fonte__diretoria').get(id=snapshot_id)
        
        if snapshot.status != 'sucesso':
            raise ValueError(f"Não é possível criar um Dataset a partir de um snapshot com erro (ID: {snapshot_id}).")

        payload = snapshot.payload_original
        dados_processados = []

        # Tenta padronizar o formato para uma lista de dicionários (tabela)
        if isinstance(payload, list):
            dados_processados = payload
        elif isinstance(payload, dict):
            # Procura por chaves comuns que indicam array de dados ('data', 'items', 'results')
            encontrou_array = False
            for chave in ['data', 'items', 'results', 'registros']:
                if chave in payload and isinstance(payload[chave], list):
                    dados_processados = payload[chave]
                    encontrou_array = True
                    break
            
            # Se não encontrou array, encapsula o dict em uma lista
            if not encontrou_array:
                dados_processados = [payload]
        else:
            # Qualquer outro formato vira string
            dados_processados = [{"valor": str(payload)}]

        # Extrai schema (colunas) se for uma lista de dicionários
        schema = {}
        if dados_processados and isinstance(dados_processados[0], dict):
            # Simplificação: pega as chaves do primeiro registro
            for chave, valor in dados_processados[0].items():
                tipo_dado = type(valor).__name__
                schema[chave] = {
                    'tipo': tipo_dado,
                    'label': chave.replace('_', ' ').title()
                }

        # Define nome padrão se não informado
        nome_final = nome_dataset or f"Dataset: {snapshot.endpoint.nome} - {timezone.now().strftime('%Y-%m-%d')}"
        diretoria_prop = snapshot.endpoint.fonte.diretoria

        # Verifica se já existe dataset vinculado a este endpoint para versionar
        dataset_existente = Dataset.objects.filter(endpoint_origem=snapshot.endpoint).order_by('-versao').first()
        nova_versao = (dataset_existente.versao + 1) if dataset_existente else 1

        # Criação do Dataset
        novo_dataset = Dataset.objects.create(
            nome=nome_final,
            descricao=descricao or f"Gerado automaticamente a partir do Snapshot #{snapshot.id}",
            endpoint_origem=snapshot.endpoint,
            dados=dados_processados,
            schema=schema,
            diretoria_proprietaria=diretoria_prop,
            responsavel=responsavel,
            versao=nova_versao
        )

        return novo_dataset
