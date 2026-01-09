# ===== COMANDO PARA GERAR NOTIFICAÇÕES AUTOMATICAMENTE =====
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model

from acoes.models import Acao
from instrumentos.models import Obrigacao
from alertas.models import Notificacao, PreferenciaNotificacao
from alertas.views import (
    criar_notificacao_acao_atrasada,
    criar_notificacao_acao_vencendo_hoje,
    criar_notificacao_acao_a_vencer,
    criar_notificacao_obrigacao_vencendo,
)


class Command(BaseCommand):
    help = 'Gera notificações automáticas baseadas em ações e obrigações (Nível 4)'

    def add_arguments(self, parser):
        parser.add_argument('--limpar-antigas', action='store_true')
        parser.add_argument('--dias-limpeza', type=int, default=30)

    def handle(self, *args, **options):
        hoje = timezone.now().date()
        amanha = hoje + timezone.timedelta(days=1)
        proxima_semana = hoje + timezone.timedelta(days=7)
        total_criadas = 0
        
        self.stdout.write(self.style.SUCCESS('🔔 Gerando notificações...'))
        
        User = get_user_model()
        usuarios = User.objects.filter(is_active=True)
        
        for usuario in usuarios:
            prefs, _ = PreferenciaNotificacao.objects.get_or_create(usuario=usuario)
            
            # AÇÕES (Substituído Tarefas)
            acoes = Acao.objects.filter(
                Q(responsavel=usuario) | Q(executores=usuario)
            ).distinct()
            
            # 1. Ações ATRASADAS
            if prefs.notificar_acao_atrasada:
                atrasadas = acoes.filter(
                    data_fim__lt=hoje,
                    status__in=['a_iniciar', 'em_andamento', 'atrasado']
                )
                for acao in atrasadas:
                    if not Notificacao.objects.filter(usuario=usuario, tipo='acao_atrasada', acao_id=acao.id, lida=False).exists():
                        criar_notificacao_acao_atrasada(acao, usuario)
                        total_criadas += 1
            
            # 2. Ações VENCENDO HOJE
            if prefs.notificar_acao_vencendo:
                vencendo_hoje = acoes.filter(data_fim=hoje, status__in=['a_iniciar', 'em_andamento'])
                for acao in vencendo_hoje:
                    if not Notificacao.objects.filter(usuario=usuario, tipo='acao_vencendo_hoje', acao_id=acao.id, lida=False).exists():
                        criar_notificacao_acao_vencendo_hoje(acao, usuario)
                        total_criadas += 1
            
            # 3. Ações A VENCER
            if prefs.notificar_acao_vencendo:
                a_vencer = acoes.filter(data_fim__gte=amanha, data_fim__lte=proxima_semana, status__in=['a_iniciar', 'em_andamento'])
                for acao in a_vencer:
                    if not Notificacao.objects.filter(usuario=usuario, tipo='acao_a_vencer', acao_id=acao.id, lida=False).exists():
                        criar_notificacao_acao_a_vencer(acao, usuario)
                        total_criadas += 1
            
            # OBRIGAÇÕES
            if prefs.notificar_obrigacao:
                # Na hierarquia simplificada, buscamos obrigações que tenham ações do usuário
                obrigacoes_vencendo = Obrigacao.objects.filter(
                    acoes__responsavel=usuario,
                    data_vencimento__lte=proxima_semana,
                    data_vencimento__gte=hoje
                ).distinct()
                
                for obrigacao in obrigacoes_vencendo:
                    if not Notificacao.objects.filter(usuario=usuario, tipo='obrigacao_vencendo', obrigacao_id=obrigacao.id, lida=False).exists():
                        criar_notificacao_obrigacao_vencendo(obrigacao, usuario)
                        total_criadas += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ {total_criadas} notificações criadas!'))
        
        if options['limpar_antigas']:
            count_lidas, _ = Notificacao.limpar_antigas_lidas(dias=options['dias_limpeza'])
            count_expiradas, _ = Notificacao.limpar_expiradas()
            self.stdout.write(self.style.SUCCESS(f'🗑️  Limpeza concluída.'))
