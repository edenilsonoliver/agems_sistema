import os
import sys
import django

# Adiciona o diretório raiz ao path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def validate_views():
    try:
        from acoes.views import AcaoCreateView, AcaoUpdateView
        print("Views importadas com sucesso.")
        
        # Testar instanciação básica (sem request)
        create_view = AcaoCreateView()
        update_view = AcaoUpdateView()
        print("Views instanciadas com sucesso.")
        
        return True
    except Exception as e:
        print(f"Erro na validação das views: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if validate_views():
        sys.exit(0)
    else:
        sys.exit(1)
