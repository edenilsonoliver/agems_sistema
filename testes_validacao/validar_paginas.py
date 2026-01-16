
import os
import django
from django.test import RequestFactory
from django.urls import resolve, reverse

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from usuarios.models import Usuario

def check_url(url_name, kwargs=None):
    """Simula o carregamento de uma URL e verifica se ela renderiza sem erros (200 OK)"""
    try:
        url = reverse(url_name, kwargs=kwargs) if kwargs else reverse(url_name)
        print(f"Testando: {url_name} ({url})... ", end="")
        
        resolver_match = resolve(url)
        view_func = resolver_match.func
        
        factory = RequestFactory()
        request = factory.get(url)
        
        # Simular usuário administrador
        user = Usuario.objects.filter(is_superuser=True).first()
        if not user:
            print("ERRO (Nenhum superusuário encontrado para o teste)")
            return False
        request.user = user
        
        # Chame a view
        if hasattr(view_func, 'view_class'):
            response = view_func.view_class.as_view()(request, **resolver_match.kwargs)
        else:
            response = view_func(request, **resolver_match.kwargs)
            
        if hasattr(response, 'render'):
            response.render()
            
        if response.status_code == 200:
            print("OK (200)")
            return True
        else:
            print(f"FALHA (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"CRASH!")
        print(f"Erro: {str(e)}")
        return False

def run_tests():
    print("=== Suite de Testes: Validação de Páginas Principal ===")
    urls_to_test = [
        'dashboard',
        'entidade_list',
        'entidade_create',
        'instrumento_list',
        'acao_list',
        'indicador_list',
        'configuracoes',
        'acao_create',
    ]
    
    success_count = 0
    for name in urls_to_test:
        if check_url(name):
            success_count += 1
            
    print(f"\nResultado: {success_count}/{len(urls_to_test)} páginas OK.")
    return success_count == len(urls_to_test)

if __name__ == "__main__":
    run_tests()
