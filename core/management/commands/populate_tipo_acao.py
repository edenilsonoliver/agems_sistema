from django.core.management.base import BaseCommand
from core.models import TipoAcao

class Command(BaseCommand):
    help = 'Popula os tipos iniciais de Ação conforme Fase 5'

    def handle(self, *args, **options):
        tipos_iniciais = [
            "Fiscalização",
            "Monitoramento",
            "Visita Técnica",
            "Acompanhamento",
            "Projeto",
            "Reunião",
            "Outros"
        ]

        self.stdout.write('Iniciando carga de Tipos de Ação...')

        criados = 0
        existentes = 0

        for nome in tipos_iniciais:
            obj, created = TipoAcao.objects.get_or_create(
                nome=nome,
                defaults={'descricao': f'Tipo de ação para {nome.lower()}'}
            )
            if created:
                criados += 1
            else:
                existentes += 1
        
        self.stdout.write(self.style.SUCCESS(f'Concluído! Criados: {criados}, Existentes: {existentes}'))
