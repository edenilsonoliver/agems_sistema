
import os
import re

file_path = r'templates/acoes/acao_form.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix result radio buttons
content = content.replace("value=='atendido'", "value == 'atendido'")
content = content.replace("value=='parcialmente_atendido'", "value == 'parcialmente_atendido'")
content = content.replace("value=='nao_atendido'", "value == 'nao_atendido'")

# Fix entity select
content = content.replace('format:"s"==ent.id', 'format:"s" == ent.id')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Replacement done.")
