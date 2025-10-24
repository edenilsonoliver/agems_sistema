from django.db import models
from django.conf import settings
from core.models import TipoAcao
from instrumentos.models import Instrumento, Obrigacao


class Acao(models.Model):
    """Modelo para representar ações de cumprimento de obrigações."""

    STATUS_CHOICES = [
        ('a_iniciar', 'A Iniciar'),
        ('em_andamento', 'Em Andamento'),
        ('atrasado', 'Atrasado'),
        ('em_validacao', 'Em Validação'),
        ('finalizado', 'Finalizado'),
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

    # Informações básicas
    nome = models.CharField('Nome da Ação', max_length=200)
    descricao = models.TextField('Descrição')

    # Relacionamentos
    instrumento = models.ForeignKey(
        Instrumento,
        on_delete=models.PROTECT,
        verbose_name='Instrumento',
        related_name='acoes',
        null=True,
        blank=True
    )
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
        related_name='acoes'
    )
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name='Responsável',
        related_name='acoes_responsavel'
    )

    # Status e progresso
    status = models.CharField('Status', max_length=15, choices=STATUS_CHOICES, default='a_iniciar')
    percentual_cumprido = models.IntegerField('Percentual Cumprido (%)', default=0, help_text='Percentual de conclusão da ação (0-100)')

    # Periodicidade e datas
    periodicidade = models.CharField('Periodicidade', max_length=15, choices=PERIODICIDADE_CHOICES, default='unica')
    data_inicio = models.DateField('Data de Início', null=True, blank=True)
    data_fim_prevista = models.DateField('Data de Fim Prevista', null=True, blank=True)
    data_fim_real = models.DateField('Data de Fim Real', null=True, blank=True)

    # Alertas
    dias_antecedencia_alerta = models.IntegerField(
        'Dias de Antecedência para Alerta',
        null=True,
        blank=True,
        default=None,
        help_text='Número de dias antes do prazo para gerar alerta (opcional)'
    )

    # Observações e metadados
    observacoes = models.TextField('Observações', blank=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)

    class Meta:
        verbose_name = 'Ação'
        verbose_name_plural = 'Ações'
        ordering = ['data_fim_prevista', 'nome']

    def __str__(self):
        return f"{self.nome} - {self.obrigacao.titulo}"

    def atualizar_percentual(self):
        """Atualiza o percentual com base nas tarefas"""
        tarefas = self.tarefas.all()
        if tarefas.exists():
            total_percentual = sum(t.percentual_cumprido for t in tarefas)
            self.percentual_cumprido = total_percentual // tarefas.count()
            self.save()

    def verificar_status_automatico(self):
        """Atualiza o status com base nas tarefas e datas"""
        from django.utils import timezone
        hoje = timezone.now().date()
        tarefas = self.tarefas.all()

        if tarefas.exists() and all(t.status == 'finalizado' for t in tarefas):
            self.status = 'finalizado'
            if not self.data_fim_real:
                self.data_fim_real = hoje
        elif self.data_fim_prevista and self.data_fim_prevista < hoje and self.status != 'finalizado':
            self.status = 'atrasado'
        elif self.data_inicio and self.data_inicio <= hoje and self.status == 'a_iniciar':
            self.status = 'em_andamento'

        self.save()

    def esta_atrasada(self):
        """Verifica se a ação está atrasada"""
        from django.utils import timezone
        hoje = timezone.now().date()
        return self.data_fim_prevista and self.data_fim_prevista < hoje and self.status != 'finalizado'

    def dias_para_vencimento(self):
        """Retorna quantos dias faltam para o vencimento"""
        from django.utils import timezone
        hoje = timezone.now().date()
        if not self.data_fim_prevista:
            return None
        delta = self.data_fim_prevista - hoje
        return delta.days


class Tarefa(models.Model):
    """Modelo para representar tarefas dentro de uma ação."""
    
    STATUS_CHOICES = [
        ('a_iniciar', 'A Iniciar'),
        ('em_andamento', 'Em Andamento'),
        ('atrasado', 'Atrasado'),
        ('em_validacao', 'Em Validação'),
        ('finalizado', 'Finalizado'),
    ]
    
    # Informações Básicas
    nome = models.CharField('Nome da Tarefa', max_length=200)
    descricao = models.TextField('Descrição', blank=True)
    
    # Relacionamento
    acao = models.ForeignKey(
        Acao,
        on_delete=models.CASCADE,
        verbose_name='Ação',
        related_name='tarefas'
    )
    
    # Responsabilidade
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name='Responsável',
        related_name='tarefas_responsavel',
        help_text='Responsável pela tarefa (apenas 1)'
    )
    executores = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name='Executores',
        related_name='tarefas_executor',
        blank=True,
        help_text='Usuários que executam a tarefa (pode ser vários)'
    )
    
    # Status e Progresso
    status = models.CharField('Status', max_length=15, choices=STATUS_CHOICES, default='a_iniciar')
    percentual_cumprido = models.IntegerField(
        'Percentual Cumprido (%)',
        default=0,
        help_text='Percentual de conclusão da tarefa (0-100)'
    )
    
    # Datas (para Gráfico de Gantt)
    data_inicio = models.DateField('Data de Início')
    data_fim = models.DateField('Data de Fim')
    data_conclusao = models.DateField('Data de Conclusão Real', null=True, blank=True)
    
    # Dependências
    tarefas_predecessoras = models.ManyToManyField(
        'self',
        symmetrical=False,
        verbose_name='Tarefas Predecessoras',
        related_name='tarefas_sucessoras',
        blank=True,
        help_text='Tarefas que devem ser concluídas antes desta'
    )
    
    # Prioridade
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    prioridade = models.CharField(
        'Prioridade',
        max_length=10,
        choices=PRIORIDADE_CHOICES,
        default='media'
    )
    
    # Observações e Metadados
    observacoes = models.TextField('Observações', blank=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    
    class Meta:
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'
        ordering = ['data_inicio', 'prioridade', 'nome']
    
    def __str__(self):
        return f"{self.nome} - {self.acao.nome}"
    
    def verificar_status_automatico(self):
        """Atualiza o status com base nas datas e percentual"""
        from django.utils import timezone
        
        hoje = timezone.now().date()
        
        # Se percentual é 100%, marcar como finalizado
        if self.percentual_cumprido >= 100 and self.status != 'finalizado':
            self.status = 'finalizado'
            if not self.data_conclusao:
                self.data_conclusao = hoje
        # Se passou da data de fim e não está finalizado
        elif self.data_fim < hoje and self.status != 'finalizado':
            self.status = 'atrasado'
        # Se está dentro do período
        elif self.data_inicio <= hoje <= self.data_fim and self.status == 'a_iniciar':
            self.status = 'em_andamento'
        
        self.save()
        
        # Atualizar percentual da ação
        self.acao.atualizar_percentual()
    
    def esta_atrasada(self):
        """Verifica se a tarefa está atrasada"""
        from django.utils import timezone
        hoje = timezone.now().date()
        return self.data_fim < hoje and self.status != 'finalizado'
    
    def pode_iniciar(self):
        """Verifica se todas as tarefas predecessoras foram concluídas"""
        predecessoras = self.tarefas_predecessoras.all()
        if not predecessoras.exists():
            return True
        return all(t.status == 'finalizado' for t in predecessoras)
    
    def duracao_dias(self):
        """Retorna a duração da tarefa em dias"""
        delta = self.data_fim - self.data_inicio
        return delta.days + 1
    
    def get_executores_display(self):
        """Retorna lista de executores"""
        return ", ".join([e.get_full_name() or e.username for e in self.executores.all()])

class ChecklistItem(models.Model):
    tarefa = models.ForeignKey('Tarefa', related_name='checklist_itens', on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)
    concluido = models.BooleanField(default=False)

    def __str__(self):
        return self.nome
