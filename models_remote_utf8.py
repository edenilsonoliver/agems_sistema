from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from core.models import TipoAcao
from instrumentos.models import Instrumento, Obrigacao


class Acao(models.Model):
    """
    Novo Modelo de A├º├úo (Antiga Tarefa).
    Representa o n├¡vel de execu├º├úo direta vinculado a uma Obriga├º├úo.
    """

    STATUS_CHOICES = [
        ('a_iniciar', 'A Iniciar'),
        ('em_andamento', 'Em Andamento'),
        ('atrasado', 'Atrasado'),
        ('em_validacao', 'Em Valida├º├úo'),
        ('finalizado', 'Finalizado'),
    ]

    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'M├®dia'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]

    PERIODICIDADE_CHOICES = [
        ('unica', '├Ünica'),
        ('mensal', 'Mensal'),
        ('bimestral', 'Bimestral'),
        ('trimestral', 'Trimestral'),
        ('quadrimestral', 'Quadrimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ]

    # Informa├º├Áes B├ísicas
    nome = models.CharField('Nome da A├º├úo', max_length=200)
    descricao = models.TextField('Descri├º├úo', blank=True)

    # Relacionamentos
    obrigacao = models.ForeignKey(
        Obrigacao,
        on_delete=models.PROTECT,
        verbose_name='Obriga├º├úo',
        related_name='acoes'
    )
    tipo_acao = models.ForeignKey(
        TipoAcao,
        on_delete=models.PROTECT,
        verbose_name='Tipo de A├º├úo',
        related_name='acoes_v2',
        null=True,
        blank=True
    )
    
    # Responsabilidade
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name='Respons├ível',
        related_name='acoes_responsavel',
        help_text='Respons├ível pela a├º├úo (apenas 1)'
    )
    executores = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name='Executores',
        related_name='acoes_executor',
        blank=True,
        help_text='Usu├írios que executam a a├º├úo (pode ser v├írios)'
    )

    # Status e Progresso
    status = models.CharField('Status', max_length=15, choices=STATUS_CHOICES, default='a_iniciar')
    percentual_cumprido = models.IntegerField(
        'Percentual Cumprido (%)', 
        default=0, 
        help_text='Percentual de conclus├úo da a├º├úo (0-100)'
    )

    # Datas
    data_inicio = models.DateField('Data de In├¡cio')
    data_fim = models.DateField('Data de Fim')
    data_conclusao = models.DateField('Data de Conclus├úo Real', null=True, blank=True)

    # Configura├º├Áes Extras (Heran├ºa da A├º├úo antiga)
    periodicidade = models.CharField('Periodicidade', max_length=15, choices=PERIODICIDADE_CHOICES, default='unica')
    prioridade = models.CharField('Prioridade', max_length=10, choices=PRIORIDADE_CHOICES, default='media')
    
    # Alertas
    dias_antecedencia_alerta = models.IntegerField(
        'Dias de Anteced├¬ncia para Alerta',
        null=True,
        blank=True,
        default=None,
        help_text='N├║mero de dias antes do prazo para gerar alerta (opcional)'
    )

    # Depend├¬ncias
    acoes_predecessoras = models.ManyToManyField(
        'self',
        symmetrical=False,
        verbose_name='A├º├Áes Predecessoras',
        related_name='acoes_sucessoras',
        blank=True,
        help_text='A├º├Áes que devem ser conclu├¡das antes desta'
    )

    # Observa├º├Áes e Metadados
    observacoes = models.TextField('Observa├º├Áes', blank=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('├Ültima Atualiza├º├úo', auto_now=True)

    class Meta:
        verbose_name = 'A├º├úo'
        verbose_name_plural = 'A├º├Áes'
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
            # Se baixou de 100%, n├úo pode ser finalizado
            if novo_status == 'finalizado':
                nova_data_conclusao = None
                if self.data_fim < hoje:
                    novo_status = 'atrasado'
                elif novo_percentual > 0:
                    novo_status = 'em_andamento'
                else:
                    novo_status = 'a_iniciar'
            
            # Outras atualiza├º├Áes autom├íticas
            if self.data_fim < hoje and novo_status != 'finalizado':
                novo_status = 'atrasado'
            elif novo_status == 'a_iniciar' and novo_percentual > 0:
                novo_status = 'em_andamento'
        
        # Usar update para evitar disparar sinais novamente e garantir persist├¬ncia direta
        Acao.objects.filter(pk=self.pk).update(
            percentual_cumprido=novo_percentual,
            status=novo_status,
            data_conclusao=nova_data_conclusao
        )
        
        # Atualizar o objeto em mem├│ria tamb├®m
        self.percentual_cumprido = novo_percentual
        self.status = novo_status
        self.data_conclusao = nova_data_conclusao


    def esta_atrasada(self):
        """Verifica se a a├º├úo est├í atrasada"""
        from django.utils import timezone
        hoje = timezone.now().date()
        return self.data_fim < hoje and self.status != 'finalizado'

    def duracao_dias(self):
        """Retorna a dura├º├úo da a├º├úo em dias"""
        delta = self.data_fim - self.data_inicio
        return delta.days + 1

    def clean(self):
        """Valida├º├Áes de datas e consist├¬ncia"""
        from django.core.exceptions import ValidationError
        
        if self.data_inicio and self.data_fim:
            if self.data_fim < self.data_inicio:
                raise ValidationError({
                    'data_fim': 'A data de fim n├úo pode ser anterior ├á data de in├¡cio.'
                })
        
        if self.data_conclusao and self.data_inicio:
            if self.data_conclusao < self.data_inicio:
                raise ValidationError({
                    'data_conclusao': 'A conclus├úo n├úo pode ser anterior ao in├¡cio da a├º├úo.'
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ChecklistItem(models.Model):
    """
    Sub-tarefas (Checklist) dentro de uma A├º├úo.
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
    Sinal para atualizar o progresso da a├º├úo quando um item do checklist muda.
    Tamb├®m atualiza o status da obriga├º├úo pai, j├í que atualizar_progresso()
    usa .update() que n├úo dispara o signal post_save da A├º├úo.
    """
    if instance.acao:
        # Atualiza progresso da a├º├úo (percentual e status)
        instance.acao.atualizar_progresso()
        
        # Atualiza status da obriga├º├úo (j├í que .update() n├úo dispara signal)
        if instance.acao.obrigacao:
            instance.acao.obrigacao.atualizar_status_por_acoes()




class AcaoDocumento(models.Model):
    """
    Documentos anexados ├á A├º├úo (PDF, DOC, XLS, etc).
    """
    acao = models.ForeignKey(Acao, related_name='documentos', on_delete=models.CASCADE)
    arquivo = models.FileField(upload_to='evidencias/docs/%Y/%m/')
    descricao = models.CharField('Descri├º├úo do Documento', max_length=255, blank=True, null=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Enviado por'
    )
    data_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Documento da A├º├úo'
        verbose_name_plural = 'Documentos da A├º├úo'
        ordering = ['-data_envio']

    def __str__(self):
        return self.descricao


class AcaoMarcador(models.Model):
    """
    Pontos georeferenciados capturados no mapa durante a fiscaliza├º├úo.
    """
    acao = models.ForeignKey(Acao, related_name='marcadores', on_delete=models.CASCADE)
    titulo = models.CharField('T├¡tulo/Identifica├º├úo', max_length=200)
    descricao = models.TextField('Descritivo da Ocorr├¬ncia', blank=True)
    
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


class AcaoFoto(models.Model):
    """
    Registro fotogr├ífico de fiscaliza├º├Áes ou visitas.
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
        verbose_name = 'Foto da A├º├úo'
        verbose_name_plural = 'Fotos da A├º├úo'
        ordering = ['-data_envio']

    def __str__(self):
        return self.legenda or f"Foto {self.id}"
