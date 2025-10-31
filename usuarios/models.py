from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Modelo customizado de usuário para o sistema AGEMS."""
    
    # Novos perfis hierárquicos (0-5)
    PERFIL_CHOICES = [
        (0, 'Admin'),
        (1, 'Diretoria'),
        (2, 'Assessoria'),
        (3, 'Coordenação'),
        (4, 'Usuário Comum'),
        (5, 'Visualizador'),
    ]
    
    perfil = models.IntegerField(
        choices=PERFIL_CHOICES,
        default=4,
        verbose_name='Perfil de Acesso',
        help_text='Define o nível de acesso e permissões do usuário'
    )
    
    # Campos de vínculo organizacional
    diretoria = models.ForeignKey(
        'core.Diretoria',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios_diretoria',
        verbose_name='Diretoria',
        help_text='Diretoria principal do usuário (obrigatório para perfis 1-5)'
    )
    
    subunidade = models.ForeignKey(
        'core.Subunidade',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios',
        verbose_name='Subunidade',
        help_text='Subunidade específica (obrigatório para perfis 2, 3, 4)'
    )
    
    # Visualizador pode ter acesso a múltiplas diretorias
    diretorias_visualizacao = models.ManyToManyField(
        'core.Diretoria',
        blank=True,
        related_name='visualizadores',
        verbose_name='Diretorias para Visualização',
        help_text='Diretorias que o visualizador pode acessar (apenas para perfil 5)'
    )
    
    # Campos adicionais (mantidos para compatibilidade)
    cargo = models.CharField(max_length=100, blank=True, verbose_name='Cargo')
    setor = models.CharField(max_length=100, blank=True, verbose_name='Setor/Departamento')
    telefone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    entidade = models.ForeignKey(
        'entidades.Entidade',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios',
        verbose_name='Entidade'
    )
    
    # Controle de senha temporária
    senha_temporaria = models.BooleanField(
        default=False,
        verbose_name='Senha Temporária',
        help_text='Se True, usuário será forçado a trocar senha no próximo login'
    )
    
    # Controle de status
    ativo = models.BooleanField(default=True, verbose_name='Usuário Ativo')
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Última Atualização')
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['first_name', 'last_name']
        indexes = [
            models.Index(fields=['perfil']),
            models.Index(fields=['diretoria']),
            models.Index(fields=['subunidade']),
        ]
    
    def __str__(self):
        nome = self.get_full_name() or self.username
        perfil_display = self.get_perfil_display()
        return f"{nome} ({perfil_display})"
    
    def get_perfil_display_completo(self):
        """Retorna perfil com contexto organizacional"""
        perfil = self.get_perfil_display()
        if self.perfil == 0:  # Admin
            return f"{perfil} - Acesso Total"
        elif self.perfil == 1 and self.diretoria:  # Diretoria
            return f"{perfil} - {self.diretoria.sigla}"
        elif self.perfil in [2, 3, 4] and self.subunidade:  # Assessoria, Coordenação, Usuário Comum
            return f"{perfil} - {self.subunidade.nome}"
        elif self.perfil == 5:  # Visualizador
            dirs = self.diretorias_visualizacao.all()
            if dirs.exists():
                siglas = ", ".join([d.sigla for d in dirs])
                return f"{perfil} - {siglas}"
            return f"{perfil} - Sem diretorias"
        return perfil
    
    def tem_permissao_diretoria(self, diretoria):
        """Verifica se usuário tem permissão para acessar uma diretoria"""
        if self.perfil == 0:  # Admin tem acesso total
            return True
        elif self.perfil == 1:  # Diretoria
            return self.diretoria == diretoria
        elif self.perfil in [2, 3, 4]:  # Assessoria, Coordenação, Usuário Comum
            return self.subunidade and self.subunidade.diretoria == diretoria
        elif self.perfil == 5:  # Visualizador
            return self.diretorias_visualizacao.filter(id=diretoria.id).exists()
        return False
    
    def tem_permissao_subunidade(self, subunidade):
        """Verifica se usuário tem permissão para acessar uma subunidade"""
        if self.perfil == 0:  # Admin tem acesso total
            return True
        elif self.perfil == 1:  # Diretoria
            return self.diretoria == subunidade.diretoria
        elif self.perfil in [2, 3, 4]:  # Assessoria, Coordenação, Usuário Comum
            return self.subunidade == subunidade
        elif self.perfil == 5:  # Visualizador
            return self.diretorias_visualizacao.filter(id=subunidade.diretoria.id).exists()
        return False
    
    def pode_criar_usuario(self):
        """Verifica se usuário pode criar outros usuários"""
        return self.perfil in [0, 1, 2, 3]  # Admin, Diretoria, Assessoria, Coordenação
    
    def pode_editar_usuario(self, usuario_alvo):
        """Verifica se pode editar outro usuário"""
        if self.perfil == 0:  # Admin pode editar todos
            return True
        elif self.perfil == 1:  # Diretoria pode editar usuários da sua diretoria
            return usuario_alvo.diretoria == self.diretoria
        elif self.perfil in [2, 3]:  # Assessoria e Coordenação podem editar usuários da sua subunidade
            return usuario_alvo.subunidade == self.subunidade
        return False
    
    def pode_acessar_modulo(self, modulo):
        """Verifica permissões por módulo"""
        # Admin tem acesso total
        if self.perfil == 0:
            return True
        
        # Visualizador só pode visualizar
        if self.perfil == 5:
            return modulo in ['entidades', 'instrumentos', 'acoes', 'tarefas', 'indicadores', 'dashboard']
        
        # Usuário Comum só acessa ações e tarefas
        if self.perfil == 4:
            return modulo in ['acoes', 'tarefas', 'dashboard']
        
        # Coordenação não acessa entidades e instrumentos
        if self.perfil == 3:
            return modulo not in ['entidades', 'instrumentos']
        
        # Diretoria e Assessoria têm acesso total
        return True
    
    def pode_editar_entidade(self):
        """Verifica se pode criar/editar entidades"""
        return self.perfil in [0, 1, 2]  # Admin, Diretoria, Assessoria
    
    def pode_editar_instrumento(self):
        """Verifica se pode criar/editar instrumentos"""
        return self.perfil in [0, 1, 2]  # Admin, Diretoria, Assessoria (Coordenação NÃO)
    
    def pode_editar_acao_tarefa(self):
        """Verifica se pode criar/editar ações e tarefas"""
        return self.perfil in [0, 1, 2, 3, 4]  # Todos exceto Visualizador
    
    def pode_editar_indicador(self):
        """Verifica se pode criar/editar indicadores"""
        return self.perfil in [0, 1, 2, 3]  # Todos exceto Usuário Comum e Visualizador

