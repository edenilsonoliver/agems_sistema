
import re
with open(r'c:\Users\rlazaro\Documents\Projetos_AGEMS\agems_sistema\templates\acoes\acao_form.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '{%' in line and '%}' not in line:
        print(f"Split tag start at line {i+1}: {line.strip()}")
    if '{{' in line and '}}' not in line:
        print(f"Split variable start at line {i+1}: {line.strip()}")
