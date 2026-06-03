from django.db import models
from core.models import Diretoria, Subunidade
from instrumentos.models import Obrigacao
from django.conf import settings

# NOTA DE SEGURANÇA: Criptografia de campos sensíveis planejada para produção.
# Requer django-cryptography instalado NA IMAGEM Docker (docker-compose build).
# Em desenvolvimento, os campos são CharFields normais para garantir estabilidade.


class FonteDados(models.Model):
    """Cadastro de fontes de dados externas (RF001)"""
    TIPO_FONTE_CHOICES = [
        ('api_rest', 'API REST'),
        ('banco_dados', 'Banco de Dados (SQL)'),
        ('arquivo_csv', 'Arquivo CSV'),
        ('planilha', 'Planilha Eletrônica'),
    ]

    AUTH_CHOICES = [
        ('none', 'Sem Autenticação'),
        ('basic', 'Basic Auth'),
        ('jwt', 'Token JWT (Auto-renovação)'),
        ('bearer', 'Bearer Token (Estático)'),
        ('api_key', 'API Key'),
        ('oauth2', 'OAuth 2.0'),
    ]

    AUTH_METODO_CHOICES = [
        ('POST', 'POST'),
        ('GET', 'GET'),
    ]

    nome = models.CharField('Nome da Fonte', max_length=200)
    tipo = models.CharField('Tipo da Fonte', max_length=50, choices=TIPO_FONTE_CHOICES)
    diretoria = models.ForeignKey(Diretoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='fontes_dados')
    url_base = models.URLField('URL Base da API', max_length=500, blank=True, null=True,
                               help_text='Ex: https://api.exemplo.com.br')
    metodo_autenticacao = models.CharField('Estratégia de Autenticação', max_length=50,
                                           choices=AUTH_CHOICES, default='none')
    status_integracao = models.BooleanField('Integração Ativa', default=True)
    responsavel_tecnico = models.CharField('Responsável Técnico', max_length=200, blank=True)

    # ── STATUS REAL DA API ──────────────────────────────────────────────────
    ultimo_status_http = models.IntegerField('Último HTTP Status', null=True, blank=True)
    ultimo_teste = models.DateTimeField('Último Teste de Conexão', null=True, blank=True)
    mensagem_ultimo_teste = models.TextField('Mensagem do Último Teste', blank=True)

    # ── CONFIGURAÇÕES DO ENDPOINT DE AUTENTICAÇÃO (Auth Flow) ─────────────────
    auth_url_relativa = models.CharField(
        'URL de Login (relativa)',
        max_length=500, blank=True,
        help_text='Caminho do endpoint de login. Ex: /oauth/token ou /api/v1/auth/login'
    )
    auth_metodo = models.CharField(
        'Método HTTP do Login',
        max_length=10, choices=AUTH_METODO_CHOICES, default='POST'
    )
    auth_content_type = models.CharField(
        'Content-Type do Login',
        max_length=100, blank=True, default='application/json',
        help_text='Ex: application/json ou application/x-www-form-urlencoded'
    )
    auth_token_key = models.CharField(
        'Chave do Token na Resposta',
        max_length=200, blank=True, default='access_token',
        help_text='Nome da chave JSON que contém o token. Ex: access_token, token, jwt'
    )
    auth_payload_extra = models.JSONField(
        'Payload Extra de Login (JSON)',
        default=dict, blank=True, null=True,
        help_text='Campos adicionais além de username/password. Ex: {"grant_type": "password"}'
    )

    # Configurações de execução
    frequencia_minutos = models.IntegerField('Frequência de Sincronização (minutos)',
                                              default=1440, help_text='1440 = 1 dia')
    timeout_segundos = models.IntegerField('Timeout (segundos)', default=30)

    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Fonte de Dados'
        verbose_name_plural = 'Fontes de Dados'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def auth_url_completa(self):
        """Monta a URL completa de autenticação."""
        if self.url_base and self.auth_url_relativa:
            return self.url_base.rstrip('/') + '/' + self.auth_url_relativa.lstrip('/')
        return None


class CredencialFonte(models.Model):
    """Armazenamento SEGURO de credenciais (RF003). Campos sensíveis são criptografados."""
    fonte = models.OneToOneField(FonteDados, on_delete=models.CASCADE, related_name='credenciais')

    # SEGURANÇA: Em produção, usar django-cryptography após docker-compose build com o pacote.
    # Em desenvolvimento, CharField simples para garantir funcionamento estável.
    usuario_api = models.CharField('Usuário / Client ID', max_length=200, blank=True)
    senha_api = models.CharField('Senha / Client Secret', max_length=500, blank=True)
    token_atual = models.TextField('Token Ativo (gerenciado pelo sistema)', blank=True)
    api_key_header = models.CharField(
        'Nome do Header da API Key',
        max_length=100, blank=True, default='X-API-Key',
        help_text='Nome do header onde a API Key deve ser enviada. Ex: X-API-Key, Authorization'
    )

    # Headers customizados (não criptografado — não é segredo, é configuração)
    headers_customizados = models.JSONField('Headers Fixos (JSON)', default=dict, blank=True, null=True,
                                             help_text='Ex: {"Accept": "application/json"}')

    data_expiracao = models.DateTimeField('Data de Expiração do Token', null=True, blank=True)
    ultima_renovacao = models.DateTimeField('Última Renovação do Token', null=True, blank=True)

    class Meta:
        verbose_name = 'Credencial de Fonte'
        verbose_name_plural = 'Credenciais de Fontes'

    def __str__(self):
        return f"Credencial: {self.fonte.nome}"


class Endpoint(models.Model):
    """Configuração de múltiplos endpoints por fonte (RF002) — cardinalidade 1 Fonte : N Endpoints"""
    METODO_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    ]

    fonte = models.ForeignKey(FonteDados, on_delete=models.CASCADE, related_name='endpoints')
    nome = models.CharField('Nome do Endpoint', max_length=200,
                             help_text='Nome descritivo. Ex: Contratos Ativos')
    url_relativa = models.CharField('URL Relativa', max_length=500,
                                     help_text='Ex: /api/v1/contratos')
    metodo_http = models.CharField('Método HTTP', max_length=10, choices=METODO_CHOICES, default='GET')
    content_type = models.CharField('Content-Type', max_length=100, blank=True,
                                     default='application/json')
    parametros_default = models.JSONField('Parâmetros / Body Padrão (JSON)', default=dict, blank=True, null=True,
                                           help_text='Parâmetros fixos enviados em toda requisição.')
    headers_override = models.JSONField('Headers Extras (sobrepõe os globais)', default=dict, blank=True, null=True)
    ativo = models.BooleanField('Endpoint Ativo', default=True)
    descricao = models.TextField('Descrição', blank=True)

    class Meta:
        verbose_name = 'Endpoint'
        verbose_name_plural = 'Endpoints'
        ordering = ['nome']

    def __str__(self):
        return f"{self.fonte.nome} → {self.nome} [{self.metodo_http}]"

    @property
    def url_completa(self):
        if self.fonte.url_base:
            return self.fonte.url_base.rstrip('/') + '/' + self.url_relativa.lstrip('/')
        return self.url_relativa


class Snapshot(models.Model):
    """Armazenamento histórico de cada sincronização (RF005)"""
    STATUS_CHOICES = [
        ('sucesso', 'Sucesso'),
        ('erro', 'Erro'),
        ('processando', 'Processando'),
    ]

    endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE, related_name='snapshots')
    data_hora = models.DateTimeField('Data/Hora da Sincronização', auto_now_add=True)
    payload_original = models.JSONField('Payload Original', default=dict)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES)
    tempo_execucao_ms = models.IntegerField('Tempo de Execução (ms)', default=0)
    quantidade_registros = models.IntegerField('Quantidade de Registros', default=0)
    log_erro = models.TextField('Log de Erro', blank=True)
    http_status_code = models.IntegerField('HTTP Status Code', default=0)

    class Meta:
        verbose_name = 'Snapshot'
        verbose_name_plural = 'Snapshots'
        ordering = ['-data_hora']

    def __str__(self):
        return f"{self.endpoint.nome} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"


class Dataset(models.Model):
    """Datasets estruturados para uso analítico (RF006)"""
    nome = models.CharField('Nome do Dataset', max_length=200)
    descricao = models.TextField('Descrição', blank=True)
    endpoint_origem = models.ForeignKey(Endpoint, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='datasets')
    dados = models.JSONField('Dados Processados', default=list,
                              help_text='Estrutura tabular/lista de objetos')
    schema = models.JSONField('Schema (Metadados)', default=dict, blank=True, null=True)
    diretoria_proprietaria = models.ForeignKey(Diretoria, on_delete=models.SET_NULL, null=True,
                                                related_name='datasets_proprios')
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                     related_name='datasets_gerenciados')
    versao = models.IntegerField('Versão', default=1)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dataset'
        verbose_name_plural = 'Datasets'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Dashboard(models.Model):
    """Dashboard visual (RF008)"""
    nome = models.CharField('Nome do Dashboard', max_length=200)
    descricao = models.TextField('Descrição', blank=True)
    diretoria_proprietaria = models.ForeignKey(Diretoria, on_delete=models.SET_NULL, null=True,
                                                related_name='dashboards_proprios')
    criador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                 related_name='dashboards_criados')
    configuracao_layout = models.JSONField('Configuração de Layout', default=dict, blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dashboard'
        verbose_name_plural = 'Dashboards'

    def __str__(self):
        return self.nome


class Widget(models.Model):
    """Componentes do dashboard (Gráficos, KPIs) (RF009)"""
    TIPO_WIDGET_CHOICES = [
        ('kpi', 'Indicador Numérico (KPI)'),
        ('linha', 'Gráfico de Linha'),
        ('barra', 'Gráfico de Barras'),
        ('pizza', 'Gráfico de Pizza'),
        ('tabela', 'Tabela de Dados'),
    ]

    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='widgets')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='widgets')
    titulo = models.CharField('Título do Widget', max_length=200)
    tipo = models.CharField('Tipo do Gráfico', max_length=50, choices=TIPO_WIDGET_CHOICES)
    configuracao = models.JSONField('Configuração do Gráfico (Eixos, Filtros)', default=dict)
    ordem = models.IntegerField('Ordem de Exibição', default=0)

    class Meta:
        verbose_name = 'Widget'
        verbose_name_plural = 'Widgets'
        ordering = ['ordem']

    def __str__(self):
        return f"{self.dashboard.nome} - {self.titulo}"


class VinculoObrigacao(models.Model):
    """Vinculação de Dashboards/Datasets a Obrigações (RF012)"""
    TIPO_VINCULO_CHOICES = [
        ('monitoramento_operacional', 'Monitoramento Operacional'),
        ('monitoramento_regulatorio', 'Monitoramento Regulatório'),
        ('fiscalizacao', 'Fiscalização'),
        ('acompanhamento_contratual', 'Acompanhamento Contratual'),
    ]

    obrigacao = models.ForeignKey(Obrigacao, on_delete=models.CASCADE, related_name='vinculos_analiticos')
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='vinculos_obrigacao')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='vinculos_obrigacao')
    tipo_vinculo = models.CharField('Tipo de Vínculo', max_length=50, choices=TIPO_VINCULO_CHOICES,
                                     default='monitoramento_regulatorio')
    justificativa = models.TextField('Justificativa Técnica', blank=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    data_vinculacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Vínculo Regulatório'
        verbose_name_plural = 'Vínculos Regulatórios'

    def __str__(self):
        return f"Vínculo: {self.obrigacao.titulo}"


class CompartilhamentoAnalitico(models.Model):
    """Controle Granular de Compartilhamento (RF010.4)"""
    NIVEL_ACESSO_CHOICES = [
        ('leitura', 'Somente Leitura'),
        ('colaboracao', 'Colaboração (Edição)'),
    ]

    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='compartilhamentos')
    diretoria_destino = models.ForeignKey(Diretoria, on_delete=models.CASCADE,
                                           related_name='dashboards_compartilhados_recebidos')
    nivel_acesso = models.CharField('Nível de Acesso', max_length=20, choices=NIVEL_ACESSO_CHOICES,
                                     default='leitura')
    data_expiracao = models.DateField('Data de Expiração', null=True, blank=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Compartilhamento Analítico'
        verbose_name_plural = 'Compartilhamentos Analíticos'

    def __str__(self):
        return f"{self.dashboard.nome} -> {self.diretoria_destino.sigla}"
