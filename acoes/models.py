from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
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
        on_delete=models.PROTECT,
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

    def atualizar_progresso(self):
        """Calcula e atualiza o percentual cumprido com base no checklist"""
        total = self.checklist_itens.count()
        novo_percentual = 0
        if total > 0:
            concluidos = self.checklist_itens.filter(concluido=True).count()
            novo_percentual = int((concluidos / total) * 100)
        
        # Aproveita para verificar o status
        from django.utils import timezone
        hoje = timezone.now().date()
        novo_status = self.status
        nova_data_conclusao = self.data_conclusao
        
        if novo_percentual >= 100:
            novo_status = 'finalizado'
            if not nova_data_conclusao:
                nova_data_conclusao = hoje
        else:
            # Se baixou de 100%, não pode ser finalizado
            if novo_status == 'finalizado':
                nova_data_conclusao = None
                if self.data_fim < hoje:
                    novo_status = 'atrasado'
                elif novo_percentual > 0:
                    novo_status = 'em_andamento'
                else:
                    novo_status = 'a_iniciar'
            
            # Outras atualizações automáticas
            if self.data_fim < hoje and novo_status != 'finalizado':
                novo_status = 'atrasado'
            elif novo_status == 'a_iniciar' and novo_percentual > 0:
                novo_status = 'em_andamento'
        
        # Usar update para evitar disparar sinais novamente e garantir persistência direta
        Acao.objects.filter(pk=self.pk).update(
            percentual_cumprido=novo_percentual,
            status=novo_status,
            data_conclusao=nova_data_conclusao
        )
        
        # Atualizar o objeto em memória também
        self.percentual_cumprido = novo_percentual
        self.status = novo_status
        self.data_conclusao = nova_data_conclusao


    def esta_atrasada(self):
        """Verifica se a ação está atrasada"""
        from django.utils import timezone
        hoje = timezone.now().date()
        return self.data_fim < hoje and self.status != 'finalizado'

    def duracao_dias(self):
        """Retorna a duração da ação em dias"""
        delta = self.data_fim - self.data_inicio
        return delta.days + 1

    def clean(self):
        """Validações de datas e consistência"""
        from django.core.exceptions import ValidationError
        
        if self.data_inicio and self.data_fim:
            if self.data_fim < self.data_inicio:
                raise ValidationError({
                    'data_fim': 'A data de fim não pode ser anterior à data de início.'
                })
        
        if self.data_conclusao and self.data_inicio:
            if self.data_conclusao < self.data_inicio:
                raise ValidationError({
                    'data_conclusao': 'A conclusão não pode ser anterior ao início da ação.'
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ChecklistItem(models.Model):
    """
    Sub-tarefas (Checklist) dentro de uma Ação.
    """
    acao = models.ForeignKey(Acao, related_name='checklist_itens', on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)
    concluido = models.BooleanField(default=False)
    ordem = models.IntegerField(default=0)

    class Meta:
        ordering = ['ordem', 'id']
        verbose_name = 'Item de Checklist'
        verbose_name_plural = 'Itens de Checklist'

    def __str__(self):
        return self.nome


@receiver(post_save, sender=ChecklistItem)
@receiver(post_delete, sender=ChecklistItem)
def checklist_item_changed(sender, instance, **kwargs):
    """
    Sinal para atualizar o progresso da ação quando um item do checklist muda.
    Também atualiza o status da obrigação pai, já que atualizar_progresso()
    usa .update() que não dispara o signal post_save da Ação.
    """
    if instance.acao:
        # Atualiza progresso da ação (percentual e status)
        instance.acao.atualizar_progresso()
        
        # Atualiza status da obrigação (já que .update() não dispara signal)
        if instance.acao.obrigacao:
            instance.acao.obrigacao.atualizar_status_por_acoes()




class AcaoDocumento(models.Model):
    """
    Documentos anexados à Ação (PDF, DOC, XLS, etc).
    """
    acao = models.ForeignKey(Acao, related_name='documentos', on_delete=models.CASCADE)
    arquivo = models.FileField(upload_to='evidencias/docs/%Y/%m/')
    descricao = models.CharField('Descrição do Documento', max_length=255, blank=True, null=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Enviado por'
    )
    data_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Documento da Ação'
        verbose_name_plural = 'Documentos da Ação'
        ordering = ['-data_envio']

    def __str__(self):
        return self.descricao


class AcaoMarcador(models.Model):
    """
    Pontos georeferenciados capturados no mapa durante a fiscalização.
    """
    acao = models.ForeignKey(Acao, related_name='marcadores', on_delete=models.CASCADE)
    titulo = models.CharField('Título/Identificação', max_length=200)
    descricao = models.TextField('Descritivo da Ocorrência', blank=True)
    
    # Coordenadas
    latitude = models.DecimalField(max_digits=22, decimal_places=16)
    longitude = models.DecimalField(max_digits=22, decimal_places=16)
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Criado por'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Marcador de Mapa'
        verbose_name_plural = 'Marcadores de Mapa'
        ordering = ['-data_criacao']

    def __str__(self):
        return f"{self.titulo} - {self.acao.nome}"


class Conformidade(models.Model):
    """Grupos de verificação dentro de uma Ação de Fiscalização."""
    acao = models.ForeignKey(Acao, related_name='conformidades', on_delete=models.CASCADE)
    nome = models.CharField('Nome da Conformidade', max_length=255)
    ordem = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Conformidade'
        verbose_name_plural = 'Conformidades'
        ordering = ['ordem', 'id']

    def __str__(self):
        return f"{self.nome} (Ação: {self.acao.nome})"


class ItemConformidade(models.Model):
    """Itens verificáveis dentro de uma Conformidade."""
    STATUS_CHOICES = [
        (0, 'Neutro'),
        (1, 'Conforme'),
        (-1, 'Não Conforme'),
    ]
    
    conformidade = models.ForeignKey(Conformidade, related_name='itens', on_delete=models.CASCADE)
    nome = models.CharField('Descrição do Item', max_length=255)
    status = models.IntegerField('Estado de Verificação', choices=STATUS_CHOICES, default=0)
    ordem = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Item de Conformidade'
        verbose_name_plural = 'Itens de Conformidade'
        ordering = ['ordem', 'id']

    def __str__(self):
        return self.nome


class Constatacao(models.Model):
    """Registros textuais descritivos vinculados a um Item de Conformidade."""
    item = models.ForeignKey(ItemConformidade, related_name='constatacoes', on_delete=models.CASCADE)
    texto = models.TextField('Descrição da Constatação')
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Constatação'
        verbose_name_plural = 'Constatações'
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Constatação em {self.item.nome}"


class ConformidadeTemplate(models.Model):
    """Template pré-definido de grupos de fiscalização."""
    nome = models.CharField('Nome do Template', max_length=255)
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Template de Conformidade'
        verbose_name_plural = 'Templates de Conformidade'

    def __str__(self):
        return self.nome


class ItemConformidadeTemplate(models.Model):
    """Itens pré-definidos dentro de um template."""
    template = models.ForeignKey(ConformidadeTemplate, related_name='itens', on_delete=models.CASCADE)
    nome = models.CharField('Descrição do Item', max_length=255)
    ordem = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Item de Template'
        verbose_name_plural = 'Itens de Template'
        ordering = ['ordem', 'id']

    def __str__(self):
        return self.nome



class AcaoFoto(models.Model):
    """
    Registro fotográfico de fiscalizações ou visitas.
    """
    acao = models.ForeignKey(Acao, related_name='fotos', on_delete=models.CASCADE)
    marcador = models.ForeignKey(
        AcaoMarcador, 
        related_name='fotos', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Marcador Associado'
    )
    # Vínculo com conformidades (especialização)
    item_conformidade = models.ForeignKey(
        ItemConformidade,
        related_name='fotos',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Item de Conformidade'
    )
    imagem = models.ImageField(upload_to='evidencias/fotos/%Y/%m/')
    legenda = models.CharField('Legenda', max_length=255, blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Registrado por'
    )
    data_registro = models.DateTimeField('Data do Registro', null=True, blank=True)
    data_envio = models.DateTimeField(auto_now_add=True)
    coordenadas = models.CharField('Coordenadas GPS', max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = 'Foto da Ação'
        verbose_name_plural = 'Fotos da Ação'
        ordering = ['-data_envio']

    def __str__(self):
        return self.legenda or f"Foto {self.id}"

