
import os
import sys

# Garante que o diretório raiz está no path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validar_paginas import run_tests as test_pages
from validar_logica_acoes import testar_automacao_acao as test_logic
from auto_fix_templates import fix_django_template_spaces

def main():
    print("="*60)
    print("      INICIANDO VERIFICAÇÃO DE INTEGRIDADE DO SISTEMA")
    print("="*60)
    
    # 1. Auto-correção preventiva
    print("1. Verificando sintaxe de templates (Auto-fix)... ", end="")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fixed_count = fix_django_template_spaces(base_dir)
    print(f"OK ({fixed_count} correções feitas)")
    print("-" * 60)

    # 2. Validação de Páginas
    pages_ok = test_pages()
    print("-" * 60)

    # 3. Lógica de Negócio
    logic_ok = test_logic()
    print("-" * 60)
    
    if pages_ok and logic_ok:
        print("\n[SUCESSO] O sistema passou em todos os testes de integridade.")
        print("Pode prosseguir com confiança.")
    else:
        print("\n[ALERTA] Foram encontrados erros nos testes.")
        print("Verifique os logs acima antes de realizar qualquer commit.")
        sys.exit(1)

if __name__ == "__main__":
    main()
