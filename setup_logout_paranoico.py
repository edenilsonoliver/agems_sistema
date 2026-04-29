import os
import shutil
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Arquivos sensíveis
SETTINGS_PATH = os.path.join(BASE_DIR, 'config', 'settings.py')
URLS_PATH = os.path.join(BASE_DIR, 'config', 'urls.py')
BASE_MODERN_PATH = os.path.join(BASE_DIR, 'templates', 'base_modern.html')

def backup_file(filepath):
    if os.path.exists(filepath):
        backup_path = filepath + '.bak'
        shutil.copy2(filepath, backup_path)
        print(f"[OK] Backup Criado Seguro: {backup_path}")
    else:
        print(f"[ERRO] Arquivo não encontrado: {filepath}")
        sys.exit(1)

def inject_settings():
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "SESSION_COOKIE_AGE = 600" in content:
        print("[!] Settings já parece ter o Timeout injetado. Ignorando.")
        return
    
    injection = """
# =========================================================================
# LOGOUT AUTOMÁTICO (PARANOIA PROTOCOL V2)
# =========================================================================
SESSION_COOKIE_AGE = 600  # 10 minutos (em segundos)
SESSION_SAVE_EVERY_REQUEST = True  # Renova o tempo a cada clique no site
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Derruba a sessão se fechar o navegador
"""
    with open(SETTINGS_PATH, 'a', encoding='utf-8') as f:
        f.write("\n" + injection)
    print("[OK] Settings Modificado (10 mins injetados no final)")

def inject_urls():
    with open(URLS_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Valida se já existe
    if any("def ping_view" in line for line in lines):
        print("[!] Rota de Ping já detectada no urls.py. Ignorando.")
        return
    
    new_lines = []
    # Injetando com segurança sem quebrar nada localizando a abertura da lista urlpatterns
    for line in lines:
        if line.startswith("urlpatterns = ["):
            new_lines.append("\n# --- CORE DA VIEW DE PING SEGURA ---\n")
            new_lines.append("from django.http import JsonResponse\n")
            new_lines.append("def ping_view(request):\n")
            new_lines.append("    return JsonResponse({'status': 'alive'})\n\n")
            new_lines.append(line)
            new_lines.append("    # Rota Ping (usada JS para manter sessão viva sem dar refresh pesado na page)\n")
            new_lines.append("    path('ping/', ping_view, name='ping'),\n\n")
        else:
            new_lines.append(line)
            
    with open(URLS_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("[OK] URLs Modificado (Ping injetado preservando a ordem do parser)")

def inject_base_modern():
    with open(BASE_MODERN_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    if any("auto_logout.html" in line for line in lines):
        print("[!] HTML base_modern.html já inclui o auto_logout. Ignorando.")
        return
        
    new_lines = []
    for line in lines:
        # Injetar uma linha antes do </body> global
        if "</body>" in line:
            new_lines.append("    <!-- Plugin de Inatividade e Auto-Logout (Cross-Tab via Paranoia Rule 5) -->\n")
            new_lines.append("    {% if user.is_authenticated %}\n")
            new_lines.append("    {% include 'auto_logout.html' %}\n")
            new_lines.append("    {% endif %}\n\n")
        new_lines.append(line)
        
    with open(BASE_MODERN_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("[OK] Base_Modern HTML Modificado estruturalmente pelo array de strings!")

if __name__ == '__main__':
    print("Iniciando Injeção Paranoica do Auto Logout...")
    print("-" * 50)
    
    backup_file(SETTINGS_PATH)
    backup_file(URLS_PATH)
    backup_file(BASE_MODERN_PATH)
    
    print("-" * 50)
    
    inject_settings()
    inject_urls()
    inject_base_modern()
    
    print("-" * 50)
    print("✅ TODO O CÓDIGO INJETADO SEGURAMENTE! NENHUM FALLBACK DE IA NATIVO CONFLITADO.")
    print("Próximo passo: Execute 'docker-compose restart web'")
