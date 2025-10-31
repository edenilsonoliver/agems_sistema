# ===== COMANDO PARA GERAR NOTIFICAÇÕES AUTOMATICAMENTE =====
"""
Comando Django para gerar notificações baseadas em tarefas e obrigações

Uso:
    python manage.py gerar_notificacoes

Agendar com cron (executar a cada hora):
    0 * * * * cd /app && python manage.py gerar_notificacoes
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model

from acoes.models import Tarefa
from instrumentos.models import Obrigacao
from alertas.models import Notificacao, PreferenciaNotificacao
from alertas.views import (
    criar_notificacao_tarefa_atrasada,
    criar_notificacao_tarefa_vencendo_hoje,
    criar_notificacao_tarefa_a_vencer,
    criar_notificacao_obrigacao_vencendo,
)


class Command(BaseCommand):
    help = 'Gera notificações automáticas baseadas em tarefas e obrigações'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar-antigas',
            action='store_true',
            help='Limpar notificações antigas (lidas há mais de 30 dias)',
        )
        
        parser.add_argument(
            '--dias-limpeza',
            type=int,
            default=30,
            help='Dias para considerar notificação antiga (padrão: 30)',
        )

    def handle(self, *args, **options):
        hoje = timezone.now().date()
        amanha = hoje + timezone.timedelta(days=1)
        proxima_semana = hoje + timezone.timedelta(days=7)
        
        total_criadas = 0
        
        self.stdout.write(self.style.SUCCESS('🔔 Gerando notificações...'))
        
        # ===== PROCESSAR CADA USUÁRIO =====
        User = get_user_model()
        usuarios = User.objects.filter(is_active=True)
        
        for usuario in usuarios:
            # Buscar preferências
            prefs, _ = PreferenciaNotificacao.objects.get_or_create(usuario=usuario)
            
            # ===== TAREFAS =====
            tarefas = Tarefa.objects.filter(
                Q(responsavel=usuario) | Q(executores=usuario)
            ).distinct()
            
            # 1. Tarefas ATRASADAS
            if prefs.notificar_tarefa_atrasada:
                atrasadas = tarefas.filter(
                    data_fim__lt=hoje,
                    status__in=['a_iniciar', 'em_andamento', 'atrasado']
                )
                
                for tarefa in atrasadas:
                    # Verificar se já existe notificação não lida
                    existe = Notificacao.objects.filter(
                        usuario=usuario,
                        tipo='tarefa_atrasada',
                        tarefa_id=tarefa.id,
                        lida=False
                    ).exists()
                    
                    if not existe:
                        criar_notificacao_tarefa_atrasada(tarefa, usuario)
                        total_criadas += 1
            
            # 2. Tarefas VENCENDO HOJE
            if prefs.notificar_tarefa_vencendo:
                vencendo_hoje = tarefas.filter(
                    data_fim=hoje,
                    status__in=['a_iniciar', 'em_andamento']
                )
                
                for tarefa in vencendo_hoje:
                    existe = Notificacao.objects.filter(
                        usuario=usuario,
                        tipo='tarefa_vencendo_hoje',
                        tarefa_id=tarefa.id,
                        lida=False
                    ).exists()
                    
                    if not existe:
                        criar_notificacao_tarefa_vencendo_hoje(tarefa, usuario)
                        total_criadas += 1
            
            # 3. Tarefas A VENCER (próximos 7 dias)
            if prefs.notificar_tarefa_vencendo:
                a_vencer = tarefas.filter(
                    data_fim__gte=amanha,
                    data_fim__lte=proxima_semana,
                    status__in=['a_iniciar', 'em_andamento']
                )
                
                for tarefa in a_vencer:
                    existe = Notificacao.objects.filter(
                        usuario=usuario,
                        tipo='tarefa_a_vencer',
                        tarefa_id=tarefa.id,
                        lida=False
                    ).exists()
                    
                    if not existe:
                        criar_notificacao_tarefa_a_vencer(tarefa, usuario)
                        total_criadas += 1
            
            # ===== OBRIGAÇÕES =====
            if prefs.notificar_obrigacao:
                obrigacoes_vencendo = Obrigacao.objects.filter(
                    acoes__responsavel=usuario,
                    data_vencimento__lte=proxima_semana,
                    data_vencimento__gte=hoje,
                    status='pendente'
                ).distinct()
                
                for obrigacao in obrigacoes_vencendo:
                    existe = Notificacao.objects.filter(
                        usuario=usuario,
                        tipo='obrigacao_vencendo',
                        obrigacao_id=obrigacao.id,
                        lida=False
                    ).exists()
                    
                    if not existe:
                        criar_notificacao_obrigacao_vencendo(obrigacao, usuario)
                        total_criadas += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {total_criadas} notificações criadas!')
        )
        
        # ===== LIMPEZA =====
        if options['limpar_antigas']:
            dias = options['dias_limpeza']
            
            # Limpar notificações lidas antigas
            count_lidas, _ = Notificacao.limpar_antigas_lidas(dias=dias)
            self.stdout.write(
                self.style.SUCCESS(f'🗑️  {count_lidas} notificações lidas antigas removidas')
            )
            
            # Limpar notificações expiradas
            count_expiradas, _ = Notificacao.limpar_expiradas()
            self.stdout.write(
                self.style.SUCCESS(f'🗑️  {count_expiradas} notificações expiradas removidas')
            )
        
        self.stdout.write(self.style.SUCCESS('🎉 Concluído!'))

