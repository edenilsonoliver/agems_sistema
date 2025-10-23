from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Modelo customizado de usuário para o sistema AGEMS."""
    
    PERFIL_CHOICES = [
        ('presidencia', 'Presidência'),
        ('diretoria', 'Diretoria'),
        ('fiscal', 'Fiscal'),
        ('concessionaria', 'Concessionária'),
        ('juridico', 'Jurídico'),
        ('tecnico', 'Técnico'),
    ]
    
    perfil = models.CharField(max_length=20, choices=PERFIL_CHOICES, verbose_name='Perfil de Acesso')
    cargo = models.CharField(max_length=100, blank=True, verbose_name='Cargo')
    setor = models.CharField(max_length=100, blank=True, verbose_name='Setor/Departamento')
    telefone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    entidade = models.ForeignKey('entidades.Entidade', on_delete=models.SET_NULL, 
                                  null=True, blank=True, related_name='usuarios', 
                                  verbose_name='Entidade')
    ativo = models.BooleanField(default=True, verbose_name='Usuário Ativo')
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Última Atualização')
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['first_name', 'last_name']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_perfil_display()})"
