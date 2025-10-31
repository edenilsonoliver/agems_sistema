"""
Management command para atualizar usuários existentes com novos perfis e senhas temporárias
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from core.models import Diretoria, Subunidade

User = get_user_model()


class Command(BaseCommand):
    help = 'Atualiza usuários existentes com novos perfis e define senhas temporárias'

    def add_arguments(self, parser):
        parser.add_argument(
            '--senha-padrao',
            type=str,
            default='Agems@2025',
            help='Senha temporária padrão para usuários sem senha'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a execução sem fazer alterações no banco'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        senha_padrao = options['senha_padrao']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 MODO SIMULAÇÃO - Nenhuma alteração será feita'))
        
        self.stdout.write('🔄 Iniciando atualização de usuários...\n')
        
        # Buscar diretorias e subunidades
        try:
            dge = Diretoria.objects.get(sigla='DGE')
            categas = Subunidade.objects.get(sigla='CATEGAS', diretoria=dge)
            creg = Subunidade.objects.get(sigla='CREG', diretoria=dge)
        except (Diretoria.DoesNotExist, Subunidade.DoesNotExist) as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro: {e}'))
            self.stdout.write(self.style.WARNING('Certifique-se de que existem:'))
            self.stdout.write('  - Diretoria com sigla "DGE"')
            self.stdout.write('  - Subunidade com sigla "CATEGAS" vinculada à DGE')
            self.stdout.write('  - Subunidade com sigla "CREG" vinculada à DGE')
            return
        
        # Configurações de usuários conforme especificado
        usuarios_config = {
            'admin': {
                'perfil': 0,  # Admin
                'diretoria': None,
                'subunidade': None,
                'descricao': 'Administrador do Sistema'
            },
            'apolleto': {
                'perfil': 4,  # Usuário Comum
                'diretoria': dge,
                'subunidade': categas,
                'descricao': 'Usuário Comum - DGE/CATEGAS'
            },
            'fporcaro': {
                'perfil': 2,  # Assessoria
                'diretoria': dge,
                'subunidade': categas,
                'descricao': 'Assessoria - DGE/CATEGAS'
            },
            'zgodoy': {
                'perfil': 3,  # Coordenação
                'diretoria': dge,
                'subunidade': creg,
                'descricao': 'Coordenação - DGE/CREG'
            },
        }
        
        usuarios_atualizados = 0
        senhas_definidas = 0
        
        for username, config in usuarios_config.items():
            try:
                user = User.objects.get(username=username)
                
                self.stdout.write(f'\n👤 Atualizando usuário: {username}')
                self.stdout.write(f'   Descrição: {config["descricao"]}')
                
                if not dry_run:
                    # Atualizar perfil
                    user.perfil = config['perfil']
                    user.diretoria = config['diretoria']
                    user.subunidade = config['subunidade']
                    
                    # Definir senha temporária se não tiver senha ou se for senha inválida
                    if not user.has_usable_password() or username != 'admin':
                        user.set_password(senha_padrao)
                        user.senha_temporaria = True
                        senhas_definidas += 1
                        self.stdout.write(f'   ✅ Senha temporária definida: {senha_padrao}')
                    
                    user.save()
                    usuarios_atualizados += 1
                    self.stdout.write(self.style.SUCCESS(f'   ✅ Atualizado com sucesso!'))
                else:
                    self.stdout.write(f'   🔍 Seria atualizado para: Perfil {config["perfil"]}')
                    if config['diretoria']:
                        self.stdout.write(f'      Diretoria: {config["diretoria"].sigla}')
                    if config['subunidade']:
                        self.stdout.write(f'      Subunidade: {config["subunidade"].nome}')
                
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'   ⚠️  Usuário "{username}" não encontrado'))
        
        # Resumo
        self.stdout.write('\n' + '='*60)
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 SIMULAÇÃO CONCLUÍDA'))
            self.stdout.write(f'   {len(usuarios_config)} usuários seriam atualizados')
        else:
            self.stdout.write(self.style.SUCCESS('✅ ATUALIZAÇÃO CONCLUÍDA!'))
            self.stdout.write(f'   {usuarios_atualizados} usuários atualizados')
            self.stdout.write(f'   {senhas_definidas} senhas temporárias definidas')
            self.stdout.write(f'\n📝 Senha temporária padrão: {senha_padrao}')
            self.stdout.write('⚠️  Usuários devem trocar a senha no primeiro acesso!')
        
        self.stdout.write('='*60 + '\n')
        
        # Mostrar resumo de perfis
        self.stdout.write('\n📊 RESUMO DE PERFIS:')
        for perfil_id, perfil_nome in User.PERFIL_CHOICES:
            count = User.objects.filter(perfil=perfil_id).count()
            if count > 0:
                self.stdout.write(f'   {perfil_nome}: {count} usuário(s)')

