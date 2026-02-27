
import re
with open(r'c:\Users\rlazaro\Documents\Projetos_AGEMS\agems_sistema\templates\acoes\acao_form.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '{%' in line and '%}' not in line:
        print(f"LINE {i+1} START: {line.strip()}")
        # Peak next line
        if i+1 < len(lines):
            print(f"LINE {i+2} NEXT : {lines[i+1].strip()}")
    if '{{' in line and '}}' not in line:
        print(f"LINE {i+1} VAR START: {line.strip()}")
        if i+1 < len(lines):
            print(f"LINE {i+2} VAR NEXT : {lines[i+1].strip()}")
