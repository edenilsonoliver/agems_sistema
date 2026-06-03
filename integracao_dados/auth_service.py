"""
Serviço de Autenticação para Fontes de Dados Externas (Auth Flow).

Responsabilidade: Ler as configurações de autenticação de uma FonteDados,
executar o ciclo de login (POST/GET) na API de origem, capturar o token
da resposta e salvar de forma criptografada na CredencialFonte.

SEGURANÇA:
  - Credenciais (usuário/senha) são descriptografadas em memória SOMENTE
    durante a requisição HTTP. Nunca são logadas ou expostas.
  - O token capturado é imediatamente criptografado antes de ser salvo.
  - Em caso de falha de conexão, o token existente não é apagado.
"""
import logging
from datetime import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)


class AuthServiceError(Exception):
    """Erro controlado do serviço de autenticação."""
    pass


def renovar_token(fonte):
    """
    Executa o fluxo de autenticação para uma FonteDados e salva o token renovado.

    Args:
        fonte: Instância de integracao_dados.models.FonteDados

    Returns:
        str: O token obtido com sucesso.

    Raises:
        AuthServiceError: Se qualquer etapa do fluxo falhar.
    """
    # Importação lazy — evita crash na inicialização do Django se 'requests' não estiver instalado
    try:
        import requests
    except ImportError:
        raise AuthServiceError(
            "A biblioteca 'requests' não está instalada no servidor. "
            "Execute: docker-compose exec web pip install requests"
        )

    # Estratégia 'none' ou 'bearer' estático não têm fluxo de renovação
    if fonte.metodo_autenticacao in ('none', 'bearer', 'api_key'):
        raise AuthServiceError(
            f"A estratégia '{fonte.metodo_autenticacao}' não suporta renovação automática de token. "
            "Configure o token manualmente na aba Credenciais."
        )

    # Garantir que a URL de auth está configurada
    auth_url = fonte.auth_url_completa
    if not auth_url:
        raise AuthServiceError(
            "A URL de login não está configurada. "
            "Preencha 'URL Base' e 'URL de Login (relativa)' na fonte de dados."
        )

    # Buscar credenciais (são descriptografadas automaticamente pelo django-cryptography)
    try:
        cred = fonte.credenciais
    except Exception:
        raise AuthServiceError("Nenhuma credencial cadastrada para esta fonte. Configure-as primeiro.")

    if not cred.usuario_api or not cred.senha_api:
        raise AuthServiceError(
            "Usuário e Senha não configurados nas credenciais desta fonte. "
            "Acesse 'Gerenciar Credenciais' para preenchê-los."
        )

    # Montar payload e headers
    content_type = fonte.auth_content_type or 'application/json'
    payload_extra = fonte.auth_payload_extra or {}

    if 'json' in content_type.lower():
        # Payload JSON
        payload = {'username': cred.usuario_api, 'password': cred.senha_api}
        payload.update(payload_extra)
        request_kwargs = {
            'json': payload,
            'headers': {'Content-Type': content_type},
            'timeout': fonte.timeout_segundos,
        }
    else:
        # Payload form-urlencoded
        payload = {'username': cred.usuario_api, 'password': cred.senha_api}
        payload.update(payload_extra)
        request_kwargs = {
            'data': payload,
            'headers': {'Content-Type': content_type},
            'timeout': fonte.timeout_segundos,
        }

    # Adicionar headers customizados globais
    if cred.headers_customizados:
        request_kwargs['headers'].update(cred.headers_customizados)

    logger.info(f"[AuthService] Iniciando renovação de token para Fonte ID={fonte.pk} ({fonte.nome})")

    # Executar a requisição HTTP
    try:
        metodo_func = getattr(requests, fonte.auth_metodo.lower(), requests.post)
        response = metodo_func(auth_url, **request_kwargs)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise AuthServiceError(f"Não foi possível conectar em '{auth_url}'. Verifique a URL base e conectividade.")
    except requests.exceptions.Timeout:
        raise AuthServiceError(f"Timeout após {fonte.timeout_segundos}s ao tentar autenticar em '{auth_url}'.")
    except requests.exceptions.HTTPError as e:
        raise AuthServiceError(
            f"Erro HTTP {response.status_code} ao autenticar: {response.text[:300]}"
        )
    except Exception as e:
        raise AuthServiceError(f"Erro inesperado durante autenticação: {str(e)}")

    # Extrair o token da resposta
    try:
        data = response.json()
    except Exception:
        raise AuthServiceError(f"A resposta da API não é um JSON válido: {response.text[:300]}")

    token_key = fonte.auth_token_key or 'access_token'
    token = data.get(token_key)

    if not token:
        chaves_disponiveis = list(data.keys())
        raise AuthServiceError(
            f"Chave '{token_key}' não encontrada na resposta. "
            f"Chaves disponíveis: {chaves_disponiveis}. "
            "Ajuste o campo 'Chave do Token na Resposta' na fonte de dados."
        )

    # Salvar token criptografado na CredencialFonte
    cred.token_atual = str(token)
    cred.ultima_renovacao = timezone.now()

    # Tentar extrair expiração se disponível
    expires_in = data.get('expires_in')
    if expires_in:
        from datetime import timedelta
        cred.data_expiracao = timezone.now() + timedelta(seconds=int(expires_in))

    cred.save()
    logger.info(f"[AuthService] Token renovado com sucesso para Fonte ID={fonte.pk} ({fonte.nome})")

    return token


def montar_headers_autenticados(fonte):
    """
    Retorna um dict de headers prontos para uso em requisições a endpoints desta fonte,
    usando o token criptografado armazenado na CredencialFonte.

    Args:
        fonte: Instância de FonteDados

    Returns:
        dict: Headers incluindo Authorization quando aplicável.
    """
    headers = {}

    try:
        cred = fonte.credenciais
    except Exception:
        return headers

    # Adicionar headers globais da fonte
    if cred.headers_customizados:
        headers.update(cred.headers_customizados)

    strategy = fonte.metodo_autenticacao

    if strategy == 'none':
        pass  # Sem auth

    elif strategy == 'basic':
        import base64
        credentials = f"{cred.usuario_api}:{cred.senha_api}"
        encoded = base64.b64encode(credentials.encode()).decode()
        headers['Authorization'] = f"Basic {encoded}"

    elif strategy in ('jwt', 'bearer'):
        if cred.token_atual:
            headers['Authorization'] = f"Bearer {cred.token_atual}"

    elif strategy == 'api_key':
        if cred.token_atual:
            header_name = cred.api_key_header or 'X-API-Key'
            headers[header_name] = cred.token_atual

    return headers
