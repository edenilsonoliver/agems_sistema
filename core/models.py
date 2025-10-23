from django.db import models


class Diretoria(models.Model):
    """Diretorias da AGEMS"""
    nome = models.CharField('Nome da Diretoria', max_length=200)
    sigla = models.CharField('Sigla', max_length=10, unique=True)
    diretor_responsavel = models.CharField('Diretor Responsável', max_length=200, blank=True)
    descricao = models.TextField('Descrição', blank=True)
    ativa = models.BooleanField('Ativa', default=True)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Diretoria'
        verbose_name_plural = 'Diretorias'
        ordering = ['sigla']
    
    def __str__(self):
        return f"{self.sigla} - {self.nome}"


class TipoEntidade(models.Model):
    """Tipos de entidades (Concessionária, Órgão Público, Prefeitura, etc)"""
    nome = models.CharField('Nome do Tipo', max_length=100, unique=True)
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Tipo de Entidade'
        verbose_name_plural = 'Tipos de Entidade'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class TipoServico(models.Model):
    """Tipos de serviços regulados (Gás, Energia, Saneamento, etc)"""
    nome = models.CharField('Nome do Serviço', max_length=100, unique=True)
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Tipo de Serviço'
        verbose_name_plural = 'Tipos de Serviço'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class TipoInstrumento(models.Model):
    """Tipos de instrumentos jurídicos (Contrato, Convênio, Acordo, etc)"""
    nome = models.CharField('Nome do Tipo', max_length=100, unique=True)
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Tipo de Instrumento'
        verbose_name_plural = 'Tipos de Instrumento'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class TipoObrigacao(models.Model):
    """Tipos de obrigações"""
    nome = models.CharField('Nome do Tipo', max_length=100, unique=True)
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Tipo de Obrigação'
        verbose_name_plural = 'Tipos de Obrigação'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class TipoAcao(models.Model):
    """Tipos de ações (Fiscalização, Análise, Projeto, etc)"""
    nome = models.CharField('Nome do Tipo', max_length=100, unique=True)
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Tipo de Ação'
        verbose_name_plural = 'Tipos de Ação'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
