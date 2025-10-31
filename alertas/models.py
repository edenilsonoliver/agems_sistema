# ===== SISTEMA DE ALERTAS - VERSÃO 2: MODELO DE NOTIFICAÇÃO =====
from django.db import models
from django.conf import settings
from django.utils import timezone


class Notificacao(models.Model):
    """
    Modelo para persistir notificações no banco
    
    Permite:
    - Marcar como lida
    - Histórico de notificações
    - Notificações customizadas
    - Diferentes tipos de alertas
    """
    
    TIPOS = [
        ('tarefa_atrasada', 'Tarefa Atrasada'),
        ('tarefa_vencendo_hoje', 'Tarefa Vencendo Hoje'),
        ('tarefa_a_vencer', 'Tarefa a Vencer'),
        ('tarefa_nova', 'Nova Tarefa'),
        ('obrigacao_vencendo', 'Obrigação Vencendo'),
        ('instrumento_expirando', 'Instrumento Expirando'),
        ('comentario', 'Novo Comentário'),
        ('atribuicao', 'Tarefa Atribuída'),
        ('mudanca_status', 'Mudança de Status'),
    ]
    
    PRIORIDADES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    # Quem recebe a notificação
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='notificacoes',
        verbose_name='Usuário'
    )
    
    # Tipo e prioridade
    tipo = models.CharField(
        max_length=50, 
        choices=TIPOS,
        verbose_name='Tipo'
    )
    
    prioridade = models.CharField(
        max_length=20,
        choices=PRIORIDADES,
        default='media',
        verbose_name='Prioridade'
    )
    
    # Conteúdo
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    
    mensagem = models.TextField(
        verbose_name='Mensagem',
        blank=True
    )
    
    # Link para a entidade relacionada
    link = models.CharField(
        max_length=200,
        verbose_name='Link',
        help_text='URL para onde a notificação leva'
    )
    
    # IDs das entidades relacionadas (para facilitar queries)
    tarefa_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='ID da Tarefa'
    )
    
    obrigacao_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='ID da Obrigação'
    )
    
    instrumento_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='ID do Instrumento'
    )
    
    # Estado
    lida = models.BooleanField(
        default=False,
        verbose_name='Lida'
    )
    
    data_leitura = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Leitura'
    )
    
    # Metadados
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    
    data_expiracao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Expiração',
        help_text='Notificação será removida após esta data'
    )
    
    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        indexes = [
            models.Index(fields=['usuario', 'lida']),
            models.Index(fields=['usuario', 'data_criacao']),
            models.Index(fields=['tipo', 'usuario']),
        ]
    
    def __str__(self):
        return f"{self.usuario.username} - {self.titulo}"
    
    def marcar_como_lida(self):
        """Marca notificação como lida"""
        if not self.lida:
            self.lida = True
            self.data_leitura = timezone.now()
            self.save(update_fields=['lida', 'data_leitura'])
    
    def marcar_como_nao_lida(self):
        """Marca notificação como não lida"""
        if self.lida:
            self.lida = False
            self.data_leitura = None
            self.save(update_fields=['lida', 'data_leitura'])
    
    @classmethod
    def criar_notificacao(cls, usuario, tipo, titulo, mensagem, link, **kwargs):
        """
        Método helper para criar notificações
        
        Uso:
            Notificacao.criar_notificacao(
                usuario=user,
                tipo='tarefa_atrasada',
                titulo='Tarefa atrasada!',
                mensagem='A tarefa X está atrasada',
                link='/tarefas/1/editar/',
                tarefa_id=1,
                prioridade='alta'
            )
        """
        return cls.objects.create(
            usuario=usuario,
            tipo=tipo,
            titulo=titulo,
            mensagem=mensagem,
            link=link,
            **kwargs
        )
    
    @classmethod
    def limpar_expiradas(cls):
        """Remove notificações expiradas"""
        agora = timezone.now()
        return cls.objects.filter(
            data_expiracao__lt=agora
        ).delete()
    
    @classmethod
    def limpar_antigas_lidas(cls, dias=30):
        """Remove notificações lidas há mais de X dias"""
        data_limite = timezone.now() - timezone.timedelta(days=dias)
        return cls.objects.filter(
            lida=True,
            data_leitura__lt=data_limite
        ).delete()


class PreferenciaNotificacao(models.Model):
    """
    Preferências de notificação do usuário
    
    Permite que usuário configure:
    - Quais tipos de notificação quer receber
    - Se quer receber por e-mail
    - Frequência de e-mails
    """
    
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preferencia_notificacao',
        verbose_name='Usuário'
    )
    
    # Tipos de notificação habilitados
    notificar_tarefa_atrasada = models.BooleanField(
        default=True,
        verbose_name='Notificar Tarefa Atrasada'
    )
    
    notificar_tarefa_vencendo = models.BooleanField(
        default=True,
        verbose_name='Notificar Tarefa Vencendo'
    )
    
    notificar_tarefa_nova = models.BooleanField(
        default=True,
        verbose_name='Notificar Nova Tarefa'
    )
    
    notificar_obrigacao = models.BooleanField(
        default=True,
        verbose_name='Notificar Obrigação'
    )
    
    notificar_comentario = models.BooleanField(
        default=True,
        verbose_name='Notificar Comentário'
    )
    
    # E-mail
    enviar_email = models.BooleanField(
        default=False,
        verbose_name='Enviar E-mail',
        help_text='Receber notificações por e-mail'
    )
    
    FREQUENCIAS = [
        ('imediato', 'Imediato'),
        ('diario', 'Resumo Diário'),
        ('semanal', 'Resumo Semanal'),
    ]
    
    frequencia_email = models.CharField(
        max_length=20,
        choices=FREQUENCIAS,
        default='diario',
        verbose_name='Frequência de E-mail'
    )
    
    # Sons e notificações visuais
    tocar_som = models.BooleanField(
        default=True,
        verbose_name='Tocar Som',
        help_text='Tocar som ao receber notificação'
    )
    
    mostrar_toast = models.BooleanField(
        default=True,
        verbose_name='Mostrar Toast',
        help_text='Mostrar notificação visual (toast)'
    )
    
    class Meta:
        verbose_name = 'Preferência de Notificação'
        verbose_name_plural = 'Preferências de Notificação'
    
    def __str__(self):
        return f"Preferências de {self.usuario.username}"

