
import os
import re

file_path = r'c:/Users/rlazaro/Documents/Projetos_AGEMS/agems_sistema/templates/acoes/acao_form.html'

if not os.path.exists(file_path):
    print(f"ERRO: Arquivo nao encontrado em {file_path}")
    exit(1)

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Tamanho original: {len(content)}")

# 1. Corrigir espaços em volta de ==
# Procura form.resultado.value=='...' e adiciona espaços
content = re.sub(r"form\.resultado\.value\s*==\s*'([^']*)'", r"form.resultado.value == '\1'", content)
# Caso o regex falhe, faz replace literal de seguranca
content = content.replace("form.resultado.value=='atendido'", "form.resultado.value == 'atendido'")
content = content.replace("form.resultado.value=='parcialmente_atendido'", "form.resultado.value == 'parcialmente_atendido'")
content = content.replace("form.resultado.value=='nao_atendido'", "form.resultado.value == 'nao_atendido'")

# 2. Corrigir tags quebradas (split tags)
# Procura tags {% if ... %} que foram quebradas por quebras de linha
def join_tags(match):
    return match.group(0).replace('\n', ' ').replace('  ', ' ')

content = re.sub(r"\{% if .*? %}", join_tags, content, flags=re.DOTALL)
content = re.sub(r"\{% endif .*? %}", join_tags, content, flags=re.DOTALL)

# 3. Corrigir especificamente o caso do radio button que estava quebrado
content = re.sub(r"\{% if\s+form\.resultado\.value\s*==\s*'parcialmente_atendido'\s*\%\}", "{% if form.resultado.value == 'parcialmente_atendido' %}", content)

# 4. Corrigir justificativa container (garantir uma unica linha)
content = re.sub(r'<div id="justificativa-container" \{% if not form\.justificativa_resultado\.value %\}.*?\{% endif %\}>', 
                 '<div id="justificativa-container" {% if not form.justificativa_resultado.value %}style="display:none;"{% endif %}>', content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Tamanho final: {len(content)}")
print("Script de correcao total executado.")
