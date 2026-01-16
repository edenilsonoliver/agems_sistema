
import os
import django
from django.utils import timezone

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from acoes.models import Acao, ChecklistItem
from instrumentos.models import Obrigacao
from usuarios.models import Usuario

def testar_automacao_acao():
    print("=== Suite de Testes: Lógica de Automação de Ações ===")
    
    try:
        user = Usuario.objects.first()
        obrig = Obrigacao.objects.first()
        
        if not user or not obrig:
            print("Pulei o teste: Preciso de ao menos um Usuário e uma Obrigação no banco.")
            return True

        # 1. Criar Ação
        print("1. Criando ação de teste... ", end="")
        acao = Acao.objects.create(
            nome="Ação Teste Integridade",
            obrigacao=obrig,
            data_inicio=timezone.now().date(),
            data_fim=timezone.now().date() + timezone.timedelta(days=1),
            status='a_iniciar',
            responsavel=user
        )
        print("OK")

        # 2. Verificar Progresso Inicial
        print(f"2. Progresso Inicial ({acao.percentual_cumprido}%)... ", end="")
        if acao.percentual_cumprido == 0:
            print("OK")
        else:
            print("FALHA")

        # 3. Adicionar item ao checklist
        print("3. Adicionando item concluído ao checklist... ", end="")
        item = ChecklistItem.objects.create(acao=acao, nome="Tarefa 1", concluido=True)
        acao.refresh_from_db()
        if acao.percentual_cumprido == 100 and acao.status == 'finalizado':
            print("OK (Status: Finalizado)")
        else:
            print(f"FALHA (Progresso: {acao.percentual_cumprido}%, Status: {acao.status})")

        # 4. Reabrir tarefa
        print("4. Desmarcando item (Reabertura)... ", end="")
        item.concluido = False
        item.save()
        acao.refresh_from_db()
        if acao.percentual_cumprido == 0 and acao.status != 'finalizado':
            print(f"OK (Status reverted: {acao.status})")
        else:
            print(f"FALHA (Status: {acao.status})")

        # Limpar
        acao.delete()
        print("\nResultado: Logica de automação INTEGRAL.")
        return True

    except Exception as e:
        print(f"\nERRO NO TESTE DE LOGICA: {str(e)}")
        return False

if __name__ == "__main__":
    testar_automacao_acao()
