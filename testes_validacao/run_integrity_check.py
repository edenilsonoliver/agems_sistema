
import os
import sys

# Garante que o diretório raiz está no path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validar_paginas import run_tests as test_pages
from validar_logica_acoes import testar_automacao_acao as test_logic

def main():
    print("="*60)
    print("      INICIANDO VERIFICAÇÃO DE INTEGRIDADE DO SISTEMA")
    print("="*60)
    
    pages_ok = test_pages()
    print("-" * 60)
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
