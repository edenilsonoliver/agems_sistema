from django.db import models
from core.models import Diretoria, TipoInstrumento, TipoObrigacao
from entidades.models import Entidade


class Instrumento(models.Model):
    """Modelo para representar instrumentos jurídicos (Contratos, Convênios, Acordos, etc)."""
    
    STATUS_CHOICES = [
        ('vigente', 'Vigente'),
        ('suspenso', 'Suspenso'),
        ('encerrado', 'Encerrado'),
        ('em_renovacao', 'Em Renovação'),
    ]
    
    # Informações Básicas
    numero = models.CharField('Número do Instrumento', max_length=50, unique=True)
    tipo_instrumento = models.ForeignKey(
        TipoInstrumento,
        on_delete=models.PROTECT,
        verbose_name='Tipo de Instrumento',
        related_name='instrumentos'
    )
    
    # Relacionamentos
    diretoria = models.ForeignKey(
        Diretoria,
        on_delete=models.PROTECT,
        verbose_name='Diretoria Responsável',
        related_name='instrumentos'
    )
    entidades = models.ManyToManyField(
        Entidade,
        verbose_name='Entidades Vinculadas',
        related_name='instrumentos',
        help_text='Selecione uma ou mais entidades vinculadas a este instrumento'
    )
    
    # NUP (E-MS)
    nup = models.CharField(
        'NUP (E-MS)',
        max_length=50,
        blank=True,
        help_text='Número Único de Protocolo do sistema E-MS'
    )
    
    # Detalhes do Instrumento
    objeto = models.TextField('Objeto do Instrumento')
    data_assinatura = models.DateField('Data de Assinatura')
    data_inicio = models.DateField('Data de Início da Vigência')
    data_fim = models.DateField('Data de Fim da Vigência')
    valor = models.DecimalField(
        'Valor (R$)',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Valor do instrumento, se aplicável'
    )
    status = models.CharField('Status', max_length=15, choices=STATUS_CHOICES, default='vigente')
    
    # Arquivo
    arquivo = models.FileField(
        'Arquivo do Instrumento',
        upload_to='instrumentos/',
        null=True,
        blank=True,
        help_text='Upload do PDF do instrumento'
    )
    
    # Revisão Tarifária (se aplicável)
    periodicidade_revisao_tarifaria = models.IntegerField(
        'Periodicidade de Revisão Tarifária (meses)',
        default=12,
        null=True,
        blank=True
    )
    data_proxima_revisao = models.DateField(
        'Data da Próxima Revisão Tarifária',
        null=True,
        blank=True
    )
    
    # Observações e Metadados
    observacoes = models.TextField('Observações', blank=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    
    class Meta:
        verbose_name = 'Instrumento'
        verbose_name_plural = 'Instrumentos'
        ordering = ['-data_inicio']
    
    def __str__(self):
        return f"{self.numero} - {self.tipo_instrumento}"
    
    def get_entidades_display(self):
        """Retorna lista de entidades vinculadas"""
        return ", ".join([e.razao_social for e in self.entidades.all()])


class Obrigacao(models.Model):
    """Modelo para representar obrigações de um instrumento."""
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em Andamento'),
        ('cumprida', 'Cumprida'),
        ('vencida', 'Vencida'),
    ]
    
    # Informações Básicas
    titulo = models.CharField('Título da Obrigação', max_length=200)
    descricao = models.TextField('Descrição')
    clausula_referencia = models.CharField(
        'Cláusula de Referência',
        max_length=50,
        blank=True,
        help_text='Ex: Cláusula 5.2, Item 3.4, etc'
    )
    
    # Relacionamento
    instrumento = models.ForeignKey(
        Instrumento,
        on_delete=models.CASCADE,
        verbose_name='Instrumento',
        related_name='obrigacoes'
    )
    
    # Tipo
    tipo_obrigacao = models.ForeignKey(
        TipoObrigacao,
        on_delete=models.PROTECT,
        verbose_name='Tipo de Obrigação',
        related_name='obrigacoes'
    )
    
    # Características
    recorrente = models.BooleanField(
        'Obrigação Recorrente',
        default=False,
        help_text='Se marcado, esta obrigação não será marcada como cumprida automaticamente'
    )
    
    # Prazo
    data_vencimento = models.DateField(
        'Data de Vencimento',
        null=True,
        blank=True,
        help_text='Data limite para cumprimento (se aplicável)'
    )
    
    # Status
    status = models.CharField('Status', max_length=15, choices=STATUS_CHOICES, default='pendente')
    cumprida = models.BooleanField('Cumprida', default=False)
    data_cumprimento = models.DateField('Data de Cumprimento', null=True, blank=True)
    
    # Alertas
    dias_antecedencia_alerta = models.IntegerField(
        'Dias de Antecedência para Alerta',
        default=30,
        help_text='Número de dias antes do vencimento para gerar alerta'
    )
    
    # Observações e Metadados
    observacoes = models.TextField('Observações', blank=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    
    class Meta:
        verbose_name = 'Obrigação'
        verbose_name_plural = 'Obrigações'
        ordering = ['data_vencimento', 'titulo']
    
    def __str__(self):
        return f"{self.titulo} - {self.instrumento.numero}"
    
    def verificar_cumprimento_automatico(self):
        """Verifica se a obrigação deve ser marcada como cumprida automaticamente"""
        if self.recorrente:
            return False
        
        # Verifica se todas as ações estão finalizadas
        acoes = self.acoes.all()
        if acoes.exists():
            return all(acao.status == 'finalizado' for acao in acoes)
        return False


# Manter compatibilidade temporária
Contrato = Instrumento
ObrigacaoContratual = Obrigacao


class ArquivoInstrumento(models.Model):
    """Modelo para múltiplos arquivos de um instrumento"""
    instrumento = models.ForeignKey(
        Instrumento,
        on_delete=models.CASCADE,
        related_name='arquivos',
        verbose_name='Instrumento'
    )
    arquivo = models.FileField(
        'Arquivo',
        upload_to='instrumentos/arquivos/'
    )
    nome_arquivo = models.CharField(
        'Nome do Arquivo',
        max_length=255,
        blank=True
    )
    data_upload = models.DateTimeField(
        'Data de Upload',
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = 'Arquivo do Instrumento'
        verbose_name_plural = 'Arquivos do Instrumento'
        ordering = ['-data_upload']
    
    def __str__(self):
        return f"{self.nome_arquivo or self.arquivo.name} - {self.instrumento}"
