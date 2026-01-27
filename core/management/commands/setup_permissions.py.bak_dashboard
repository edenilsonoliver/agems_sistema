from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from instrumentos.models import Instrumento, Obrigacao
from entidades.models import Entidade
from acoes.models import Acao, ChecklistItem
from usuarios.models import Usuario

class Command(BaseCommand):
    help = 'Configura os grupos de acesso e permissões iniciais do sistema'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando configuração de permissões...')

        # Definindo a estrutura de permissões
        # Formato: 'app_model': ['permissões']
        
        # 1. GRUPO GESTORES (Diretoria/Assessoria)
        # Foco: Gerenciar o "Negócio" (Contratos, Entidades)
        perms_gestores = {
            'entidades': ['add_entidade', 'change_entidade', 'view_entidade'],
            'instrumentos': ['add_instrumento', 'change_instrumento', 'view_instrumento', 'add_obrigacao', 'change_obrigacao', 'view_obrigacao'],
            'acoes': ['view_acao', 'view_checklistitem'], # Apenas visualizam o operacional
            'usuarios': ['view_usuario'],
        }

        # 2. GRUPO TÉCNICOS (Coordenação/Fiscais)
        # Foco: Executar o "Operacional" (Ações, Checklists)
        perms_tecnicos = {
            'entidades': ['view_entidade'],
            'instrumentos': ['view_instrumento', 'view_obrigacao'],
            'acoes': ['add_acao', 'change_acao', 'view_acao', 'add_checklistitem', 'change_checklistitem', 'view_checklistitem', 'delete_checklistitem'],
        }

        # 3. GRUPO VISUALIZADORES (Auditoria)
        # Foco: Ver tudo, não tocar em nada
        perms_visualizadores = {
            'entidades': ['view_entidade'],
            'instrumentos': ['view_instrumento', 'view_obrigacao'],
            'acoes': ['view_acao', 'view_checklistitem'],
            'usuarios': ['view_usuario'],
        }

        grupos_config = {
            'Gestores': perms_gestores,
            'Tecnicos': perms_tecnicos,
            'Visualizadores': perms_visualizadores,
        }

        for nome_grupo, apps_perms in grupos_config.items():
            grupo, created = Group.objects.get_or_create(name=nome_grupo)
            if created:
                self.stdout.write(f'Grupo "{nome_grupo}" criado.')
            else:
                self.stdout.write(f'Grupo "{nome_grupo}" atualizado.')
            
            # Limpar permissões antigas para garantir estado limpo
            grupo.permissions.clear()

            total_perms = 0
            for app, codenames in apps_perms.items():
                for codename in codenames:
                    try:
                        perm = Permission.objects.get(codename=codename)
                        grupo.permissions.add(perm)
                        total_perms += 1
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Permissão não encontrada: {codename}'))
            
            self.stdout.write(self.style.SUCCESS(f' - {total_perms} permissões atribuídas ao grupo {nome_grupo}'))

        self.stdout.write(self.style.SUCCESS('Configuração de permissões concluída com sucesso!'))
