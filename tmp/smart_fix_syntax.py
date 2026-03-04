
import os
import re

file_path = r'c:/Users/rlazaro/Documents/Projetos_AGEMS/agems_sistema/templates/acoes/acao_form.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix spacing around == for all Django template conditions in this file
# This regex looks for comparison operators inside {% ... %}
def fix_spaces(match):
    tag_content = match.group(1)
    # Add spaces around == if they are missing
    tag_content = re.sub(r'([^\s!])==', r'\1 ==', tag_content)
    tag_content = re.sub(r'==([^\s])', r'== \1', tag_content)
    # Same for !=
    tag_content = re.sub(r'([^\s!])!=', r'\1 !=', tag_content)
    tag_content = re.sub(r'!=([^\s])', r'!= \1', tag_content)
    return '{% ' + tag_content + ' %}'

# Apply to all {% ... %} blocks (ignoring multi-line for now, but usually they are single line)
new_content = re.sub(r'\{%\s*(.*?)\s*%\}', fix_spaces, content)

if new_content != content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Sintaxe de comparação corrigida em todo o arquivo.")
else:
    print("Nenhuma inconsistência de espaço encontrada.")

