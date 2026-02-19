from django.db import models
from django.core.exceptions import ValidationError
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
    numero = models.CharField('Nome do Instrumento', max_length=50, unique=True)
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
    
    def clean(self):
        """Validações de integridade do instrumento."""
        if self.data_inicio and self.data_fim:
            if self.data_fim < self.data_inicio:
                raise ValidationError({
                    'data_fim': 'A data final da vigência não pode ser anterior à data de início.'
                })
        
        if self.data_assinatura and self.data_inicio:
            # Aviso: Alguns contratos podem ser assinados DEPOIS do início (retroativos), 
            # mas vamos manter apenas a lógica de sanidade básica.
            pass

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
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
        on_delete=models.PROTECT,  # Alterado de CASCADE para PROTECT para segurança
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
    
    # Prazo e Atendimento
    prazo_dias = models.IntegerField(
        'Prazo (Dias)',
        default=0,
        help_text='Número de dias a partir da data de início do instrumento'
    )
    data_vencimento = models.DateField(
        'Data de Vencimento',
        null=True,
        blank=True,
        help_text='Data limite para cumprimento (calculada ou manual)'
    )
    percentual_atendimento = models.IntegerField(
        'Percentual de Atendimento (%)',
        default=0,
        help_text='Média ponderada baseada nos itens de checklist das ações'
    )
    
    # Status
    status = models.CharField('Status', max_length=15, choices=STATUS_CHOICES, default='pendente')
    
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
    
    @property
    def percentual_conclusao(self):
        """Calcula o percentual de conclusão baseado nas ações vinculadas."""
        total = self.acoes.count()
        if total == 0:
            return 0
        concluidas = self.acoes.filter(status='finalizado').count()
        return int((concluidas / total) * 100)

    def atualizar_status_por_acoes(self):
        """
        Atualiza o status e o percentual de atendimento da Obrigação.
        O percentual é a média dos percentuais de conclusão de todas as ações.
        """
        from django.utils import timezone
        hoje = timezone.now().date()
        
        # 1. Cálculo do Percentual de Atendimento (Média das Ações)
        acoes = self.acoes.all()
        total_acoes = acoes.count()
        
        novo_percentual = 0
        if total_acoes > 0:
            soma_percentuais = sum([acao.percentual_cumprido for acao in acoes])
            novo_percentual = int(soma_percentuais / total_acoes)

        from django.utils import timezone
        hoje = timezone.now().date()
        
        # 2. Determinação do Status
        if total_acoes > 0 and novo_percentual >= 100:
            novo_status = 'cumprida'
        elif self.data_vencimento and self.data_vencimento < hoje:
            novo_status = 'vencida'
        elif self.acoes.filter(status__in=['em_andamento', 'atrasado', 'em_validacao']).exists() or novo_percentual > 0:
            novo_status = 'em_andamento'
        else:
            novo_status = 'pendente'

        # 3. Salvar alterações
        campos_alterados = []
        
        if novo_percentual != self.percentual_atendimento:
            self.percentual_atendimento = novo_percentual
            campos_alterados.append('percentual_atendimento')
            
        if novo_status != self.status:
            self.status = novo_status
            campos_alterados.append('status')
        
        if campos_alterados:
            campos_alterados.append('data_atualizacao')
            self.save(update_fields=campos_alterados)

    def clean(self):
        """Validações de integridade da obrigação."""
        if self.data_vencimento and self.instrumento:
            # Verifica se o vencimento está dentro da vigência do instrumento
            # Nota: Obrigação pode vencer no dia final, mas não depois.
            if self.instrumento.data_fim and self.data_vencimento > self.instrumento.data_fim:
                pass 
                # Decisao de design: Permitir obrigação pós-vigência? (Ex: Prestação de Contas Final)
                # Por enquanto, vamos apenas logar ou flexibilizar. Se o usuário quiser restringir:
                # raise ValidationError({'data_vencimento': 'A data de vencimento excede a vigência do instrumento.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


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
