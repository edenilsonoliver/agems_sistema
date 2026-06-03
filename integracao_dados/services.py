import requests
import json
from django.utils import timezone
from requests.exceptions import RequestException, Timeout
from .models import Endpoint, Snapshot, CredencialFonte

class IntegradorAPI:
    """
    Serviço para consumo de APIs REST, focado na DGE (ex: MSGás).
    Implementa as regras de RF003, RF004 e RF005.
    """

    def __init__(self, endpoint_id):
        self.endpoint = Endpoint.objects.select_related('fonte', 'fonte__credenciais').get(id=endpoint_id)
        self.fonte = self.endpoint.fonte
        self.credenciais = getattr(self.fonte, 'credenciais', None)

    def _obter_headers(self):
        """Prepara os headers da requisição, incluindo autenticação."""
        headers = {'Content-Type': 'application/json'}
        
        if self.credenciais and self.credenciais.headers_customizados:
            headers.update(self.credenciais.headers_customizados)

        if self.fonte.metodo_autenticacao == 'jwt':
            token = self._obter_token_jwt()
            if token:
                headers['Authorization'] = f'Bearer {token}'
        elif self.fonte.metodo_autenticacao == 'api_key':
            if self.credenciais and self.credenciais.token_atual:
                headers['x-api-key'] = self.credenciais.token_atual

        return headers

    def _obter_token_jwt(self):
        """Gerencia o token JWT (reaproveita se válido, renova se expirado)."""
        if not self.credenciais:
            return None

        # TODO: Se o token estiver expirado, implementar a chamada para o endpoint de login da fonte.
        # Por enquanto, usa o token estático salvo.
        return self.credenciais.token_atual

    def _construir_url(self):
        """Constrói a URL completa baseada na Fonte e no Endpoint."""
        base = self.fonte.url_base.rstrip('/') if self.fonte.url_base else ''
        relativa = self.endpoint.url_relativa.lstrip('/')
        return f"{base}/{relativa}"

    def sincronizar(self, usuario=None):
        """
        Executa a chamada para a API e salva o Snapshot.
        """
        if not self.fonte.status_integracao or not self.endpoint.ativo:
            return None

        url = self._construir_url()
        headers = self._obter_headers()
        inicio = timezone.now()
        status_final = 'sucesso'
        payload_resposta = {}
        log_erro = ''
        qtd_registros = 0

        try:
            resposta = requests.request(
                method=self.endpoint.metodo_http,
                url=url,
                headers=headers,
                params=self.endpoint.parametros_default if self.endpoint.metodo_http == 'GET' else None,
                json=self.endpoint.parametros_default if self.endpoint.metodo_http == 'POST' else None,
                timeout=self.fonte.timeout_segundos
            )
            resposta.raise_for_status()  # Levanta erro para status 4xx e 5xx
            
            # Tenta decodificar JSON
            try:
                payload_resposta = resposta.json()
                # Verifica quantos registros vieram (se for lista)
                if isinstance(payload_resposta, list):
                    qtd_registros = len(payload_resposta)
                elif isinstance(payload_resposta, dict) and 'data' in payload_resposta:
                    qtd_registros = len(payload_resposta.get('data', []))
                else:
                    qtd_registros = 1
            except ValueError:
                payload_resposta = {'raw_text': resposta.text}

        except Timeout:
            status_final = 'erro'
            log_erro = f"Timeout após {self.fonte.timeout_segundos} segundos."
        except RequestException as e:
            status_final = 'erro'
            log_erro = f"Erro de conexão/HTTP: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                log_erro += f" | Response: {e.response.text[:500]}"
        except Exception as e:
            status_final = 'erro'
            log_erro = f"Erro inesperado: {str(e)}"

        fim = timezone.now()
        tempo_ms = int((fim - inicio).total_seconds() * 1000)

        # Salva o histórico (Snapshot) garantindo que nada seja sobrescrito (RF005)
        snapshot = Snapshot.objects.create(
            endpoint=self.endpoint,
            payload_original=payload_resposta,
            status=status_final,
            tempo_execucao_ms=tempo_ms,
            quantidade_registros=qtd_registros,
            log_erro=log_erro
        )

        return snapshot
