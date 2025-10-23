from django.db import models
from django.conf import settings


class IndicadorContratual(models.Model):
    """Modelo para definir indicadores contratuais a serem monitorados."""
    
    TIPO_CHOICES = [
        ('economico', 'Econômico-Financeiro'),
        ('contabil', 'Contábil'),
        ('tecnico', 'Técnico'),
        ('operacional', 'Operacional'),
        ('qualidade', 'Qualidade do Serviço'),
    ]
    
    FORMA_VISUALIZACAO_CHOICES = [
        ('grafico_barras', 'Gráfico de Barras'),
        ('grafico_linhas', 'Gráfico de Linhas'),
        ('grafico_pizza', 'Gráfico de Pizza'),
        ('tabela', 'Tabela'),
        ('numero', 'Número Simples'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código do Indicador')
    nome = models.CharField(max_length=200, verbose_name='Nome do Indicador')
    descricao = models.TextField(verbose_name='Descrição')
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, verbose_name='Tipo')
    unidade_medida = models.CharField(max_length=50, verbose_name='Unidade de Medida')
    forma_visualizacao = models.CharField(max_length=20, choices=FORMA_VISUALIZACAO_CHOICES, 
                                          verbose_name='Forma de Visualização')
    formula_calculo = models.TextField(blank=True, verbose_name='Fórmula de Cálculo')
    periodicidade = models.CharField(max_length=20, verbose_name='Periodicidade de Coleta')
    ativo = models.BooleanField(default=True, verbose_name='Indicador Ativo')
    ordem_exibicao = models.IntegerField(default=0, verbose_name='Ordem de Exibição')
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Última Atualização')
    
    class Meta:
        verbose_name = 'Indicador Contratual'
        verbose_name_plural = 'Indicadores Contratuais'
        ordering = ['ordem_exibicao', 'nome']
    
    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class ValorIndicador(models.Model):
    """Modelo para armazenar valores coletados dos indicadores."""
    
    indicador = models.ForeignKey(IndicadorContratual, on_delete=models.PROTECT, 
                                  related_name='valores', verbose_name='Indicador')
    contrato = models.ForeignKey('instrumentos.Instrumento', on_delete=models.PROTECT, 
                                 related_name='valores_indicadores', verbose_name='Contrato')
    periodo_referencia = models.DateField(verbose_name='Período de Referência')
    valor = models.DecimalField(max_digits=20, decimal_places=4, verbose_name='Valor')
    valor_meta = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, 
                                     verbose_name='Valor Meta')
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    responsavel_coleta = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                           null=True, verbose_name='Responsável pela Coleta')
    data_coleta = models.DateTimeField(auto_now_add=True, verbose_name='Data de Coleta')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Última Atualização')
    
    class Meta:
        verbose_name = 'Valor de Indicador'
        verbose_name_plural = 'Valores de Indicadores'
        ordering = ['-periodo_referencia']
        unique_together = ['indicador', 'contrato', 'periodo_referencia']
    
    def __str__(self):
        return f"{self.indicador.codigo} - {self.contrato.numero} - {self.periodo_referencia}"


class ImportacaoIndicadores(models.Model):
    """Modelo para registrar importações de indicadores via CSV."""
    
    STATUS_CHOICES = [
        ('processando', 'Processando'),
        ('sucesso', 'Sucesso'),
        ('erro', 'Erro'),
        ('parcial', 'Sucesso Parcial'),
    ]
    
    arquivo = models.FileField(upload_to='importacoes/', verbose_name='Arquivo CSV')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                null=True, verbose_name='Usuário')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='processando', verbose_name='Status')
    total_registros = models.IntegerField(default=0, verbose_name='Total de Registros')
    registros_sucesso = models.IntegerField(default=0, verbose_name='Registros com Sucesso')
    registros_erro = models.IntegerField(default=0, verbose_name='Registros com Erro')
    log_erros = models.TextField(blank=True, verbose_name='Log de Erros')
    data_importacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Importação')
    
    class Meta:
        verbose_name = 'Importação de Indicadores'
        verbose_name_plural = 'Importações de Indicadores'
        ordering = ['-data_importacao']
    
    def __str__(self):
        return f"Importação {self.id} - {self.status}"
