import os
import sys
import django

# Setup Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from usuarios.models import Usuario
from acoes.models import Acao
from instrumentos.models import Instrumento

def check_tecnico2_access():
    results = []
    try:
        # Check tecnico2
        try:
            user2 = Usuario.objects.get(username='tecnico2')
            results.append(f"User tecnico2: ID={user2.id}, Perfil={user2.perfil}, Subunidade={user2.subunidade}, Diretoria={user2.diretoria}")
        except Usuario.DoesNotExist:
            results.append("User tecnico2 not found.")
            return results

        # Check tecnico1 for comparison
        try:
            user1 = Usuario.objects.get(username='tecnico1')
            results.append(f"User tecnico1: ID={user1.id}, Perfil={user1.perfil}, Subunidade={user1.subunidade}, Diretoria={user1.diretoria}")
        except Usuario.DoesNotExist:
            results.append("User tecnico1 not found.")

        # Find the Action from the screenshot
        # Title: "Ação Teste 1", Description: "Ação para o tecnico1"
        try:
            action = Acao.objects.filter(nome='Ação Teste 1').first()
            if action:
                results.append(f"Action: '{action.nome}', ID={action.id}, Instrumento ID={action.obrigacao.instrumento.id}")
                results.append(f"Action Responsável: {action.responsavel}")
                results.append(f"Action Executores: {[u.username for u in action.executores.all()]}")
                results.append(f"Instrumento Subunidades: {[s.nome for s in action.obrigacao.instrumento.subunidades.all()]}")
            else:
                results.append("Action 'Ação Teste 1' not found.")
        except Exception as e:
            results.append(f"Error finding action: {e}")

    except Exception as e:
        import traceback
        results.append(f"General Error: {e}")
        results.append(traceback.format_exc())

    output_path = os.path.join(BASE_DIR, 'debug_tecnico2.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(results))

if __name__ == "__main__":
    check_tecnico2_access()
