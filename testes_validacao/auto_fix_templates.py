
import os
import re

def fix_django_template_spaces(directory):
    """
    Percorre todos os arquivos HTML no diretório e corrige falta de espaços
    em tags if/elif que podem causar TemplateSyntaxError.
    Ex: {% if var==val %} -> {% if var == val %}
    """
    total_fixed = 0
    for root, dirs, files in os.walk(directory):
        # Ignorar pastas de ambiente virtual e git
        if 'venv' in root or '.git' in root or 'node_modules' in root:
            continue
            
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Regex para encontrar comparadores sem espaços dentro de tags Django
                    # Procura por ==, !=, >=, <=, <, > dentro de {% ... %}
                    patterns = [
                        (r'\{% (if|elif) ([^ %]+)==([^ %]+) %\}', r'{% \1 \2 == \3 %}'),
                        (r'\{% (if|elif) ([^ %]+)!=([^ %]+) %\}', r'{% \1 \2 != \3 %}'),
                        (r'\{% (if|elif) ([^ %]+)>=([^ %]+) %\}', r'{% \1 \2 >= \3 %}'),
                        (r'\{% (if|elif) ([^ %]+)<=([^ %]+) %\}', r'{% \1 \2 <= \3 %}'),
                    ]
                    
                    new_content = content
                    for pattern, replacement in patterns:
                        new_content = re.sub(pattern, replacement, new_content)
                    
                    if new_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        # print(f"  [AUTO-FIX] Espaços corrigidos em: {file}")
                        total_fixed += 1
                except Exception as e:
                    print(f"  [ERRO] Falha ao processar {file}: {e}")
    
    return total_fixed

if __name__ == "__main__":
    # Teste isolado
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    count = fix_django_template_spaces(base_dir)
    print(f"Correção concluída. Arquivos modificados: {count}")
