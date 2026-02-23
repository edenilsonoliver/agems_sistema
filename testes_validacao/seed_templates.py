import os
import sys
import django

# Adiciona o diretório raiz ao path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from acoes.models import ConformidadeTemplate, ItemConformidadeTemplate

def seed_templates():
    t, created = ConformidadeTemplate.objects.get_or_create(
        nome="Fiscalização de Saneamento Básico",
        descricao="Template padrão para fiscalização de redes de água e esgoto."
    )
    if created:
        itens = [
            "Estado das Tampas de PV",
            "Vazamentos Visíveis",
            "Pressão na Rede (Medição)",
            "Qualidade Visual da Água",
            "Sinalização de Obras",
            "Recomposição Asfáltica"
        ]
        for i, nome in enumerate(itens):
            ItemConformidadeTemplate.objects.create(
                template=t,
                nome=nome,
                ordem=i
            )
        print(f"Template '{t.nome}' criado com sucesso!")
    else:
        print(f"Template '{t.nome}' já existe.")

if __name__ == "__main__":
    seed_templates()
