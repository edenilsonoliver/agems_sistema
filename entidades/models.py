from django.db import models
from core.models import TipoEntidade, TipoServico


class Entidade(models.Model):
    """Modelo para representar entidades que se relacionam com a AGEMS 
    (Concessionárias, Órgãos Públicos, Prefeituras, etc)."""
    
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('suspensa', 'Suspensa'),
        ('encerrada', 'Encerrada'),
    ]
    
    # Informações Básicas
    razao_social = models.CharField('Razão Social', max_length=200)
    nome_fantasia = models.CharField('Nome Fantasia', max_length=200, blank=True)
    cnpj = models.CharField('CNPJ', max_length=18, unique=True)
    
    # Tipo e Classificação
    tipo_entidade = models.ForeignKey(
        TipoEntidade, 
        on_delete=models.PROTECT, 
        verbose_name='Tipo de Entidade',
        related_name='entidades'
    )
    tipo_servico = models.ForeignKey(
        TipoServico,
        on_delete=models.PROTECT,
        verbose_name='Tipo de Serviço',
        related_name='entidades',
        null=True,
        blank=True
    )
    
    # Logo
    logo = models.ImageField(
        'Logo da Entidade',
        upload_to='entidades/logos/',
        blank=True,
        null=True,
        help_text='Upload do logo da entidade (PNG, JPG)'
    )
    
    # Status
    status = models.CharField('Status', max_length=10, choices=STATUS_CHOICES, default='ativa')
    
    # Contato
    email = models.EmailField('E-mail Principal')
    telefone = models.CharField('Telefone', max_length=20)
    site = models.URLField('Website', blank=True)
    
    # Endereço
    endereco = models.CharField('Endereço', max_length=200)
    cidade = models.CharField('Cidade', max_length=100, default='Campo Grande')
    estado = models.CharField('Estado', max_length=2, default='MS')
    cep = models.CharField('CEP', max_length=10)
    
    # Representante Legal
    representante_legal = models.CharField('Representante Legal', max_length=200)
    cpf_representante = models.CharField('CPF do Representante', max_length=14)
    email_representante = models.EmailField('E-mail do Representante', blank=True)
    telefone_representante = models.CharField('Telefone do Representante', max_length=20, blank=True)
    
    # Observações e Metadados
    observacoes = models.TextField('Observações', blank=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    
    class Meta:
        verbose_name = 'Entidade'
        verbose_name_plural = 'Entidades'
        ordering = ['razao_social']
    
    def __str__(self):
        return f"{self.razao_social} ({self.tipo_entidade})"


# Manter compatibilidade temporária
Concessionaria = Entidade
