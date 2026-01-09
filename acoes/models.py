from django.db import models
from django.conf import settings
from core.models import TipoAcao
from instrumentos.models import Instrumento, Obrigacao


class Acao(models.Model):
    """
    Novo Modelo de Ação (Antiga Tarefa).
    Representa o nível de execução direta vinculado a uma Obrigação.
    """

    STATUS_CHOICES = [
        ('a_iniciar', 'A Iniciar'),
        ('em_andamento', 'Em Andamento'),
        ('atrasado', 'Atrasado'),
        ('em_validacao', 'Em Validação'),
        ('finalizado', 'Finalizado'),
    ]

    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]

    PERIODICIDADE_CHOICES = [
        ('unica', 'Única'),
        ('mensal', 'Mensal'),
        ('bimestral', 'Bimestral'),
        ('trimestral', 'Trimestral'),
        ('quadrimestral', 'Quadrimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ]

    # Informações Básicas
    nome = models.CharField('Nome da Ação', max_length=200)
    descricao = models.TextField('Descrição', blank=True)

    # Relacionamentos
    obrigacao = models.ForeignKey(
        Obrigacao,
        on_delete=models.CASCADE,
        verbose_name='Obrigação',
        related_name='acoes'
    )
    tipo_acao = models.ForeignKey(
        TipoAcao,
        on_delete=models.PROTECT,
        verbose_name='Tipo de Ação',
        related_name='acoes_v2',
        null=True,
        blank=True
    )
    
    # Responsabilidade
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name='Responsável',
        related_name='acoes_responsavel',
        help_text='Responsável pela ação (apenas 1)'
    )
    executores = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name='Executores',
        related_name='acoes_executor',
        blank=True,
        help_text='Usuários que executam a ação (pode ser vários)'
    )

    # Status e Progresso
    status = models.CharField('Status', max_length=15, choices=STATUS_CHOICES, default='a_iniciar')
    percentual_cumprido = models.IntegerField(
        'Percentual Cumprido (%)', 
        default=0, 
        help_text='Percentual de conclusão da ação (0-100)'
    )

    # Datas
    data_inicio = models.DateField('Data de Início')
    data_fim = models.DateField('Data de Fim')
    data_conclusao = models.DateField('Data de Conclusão Real', null=True, blank=True)

    # Configurações Extras (Herança da Ação antiga)
    periodicidade = models.CharField('Periodicidade', max_length=15, choices=PERIODICIDADE_CHOICES, default='unica')
    prioridade = models.CharField('Prioridade', max_length=10, choices=PRIORIDADE_CHOICES, default='media')
    
    # Alertas
    dias_antecedencia_alerta = models.IntegerField(
        'Dias de Antecedência para Alerta',
        null=True,
        blank=True,
        default=None,
        help_text='Número de dias antes do prazo para gerar alerta (opcional)'
    )

    # Dependências
    acoes_predecessoras = models.ManyToManyField(
        'self',
        symmetrical=False,
        verbose_name='Ações Predecessoras',
        related_name='acoes_sucessoras',
        blank=True,
        help_text='Ações que devem ser concluídas antes desta'
    )

    # Observações e Metadados
    observacoes = models.TextField('Observações', blank=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)

    class Meta:
        verbose_name = 'Ação'
        verbose_name_plural = 'Ações'
        ordering = ['data_inicio', 'prioridade', 'nome']

    def __str__(self):
        return f"{self.nome} - {self.obrigacao.titulo}"

    def verificar_status_automatico(self):
        """Atualiza o status com base nas datas e percentual"""
        from django.utils import timezone
        hoje = timezone.now().date()
        
        if self.percentual_cumprido >= 100 and self.status != 'finalizado':
            self.status = 'finalizado'
            if not self.data_conclusao:
                self.data_conclusao = hoje
        elif self.data_fim < hoje and self.status != 'finalizado':
            self.status = 'atrasado'
        elif self.data_inicio <= hoje <= self.data_fim and self.status == 'a_iniciar':
            self.status = 'em_andamento'
        
        self.save()

    def esta_atrasada(self):
        """Verifica se a ação está atrasada"""
        from django.utils import timezone
        hoje = timezone.now().date()
        return self.data_fim < hoje and self.status != 'finalizado'

    def duracao_dias(self):
        """Retorna a duração da ação em dias"""
        delta = self.data_fim - self.data_inicio
        return delta.days + 1


class ChecklistItem(models.Model):
    """
    Sub-tarefas (Checklist) dentro de uma Ação.
    """
    acao = models.ForeignKey(Acao, related_name='checklist_itens', on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)
    concluido = models.BooleanField(default=False)

    def __str__(self):
        return self.nome
