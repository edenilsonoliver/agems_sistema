
import os
import re

file_path = r'templates/acoes/acao_form.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix spacing around == in template tags for resultado
# Note: Django's template engine is very strict on Windows/certain versions regarding == without spaces.

original = content

# Fix for form.resultado.value
content = re.sub(r"\{\%\s*if\s+form\.resultado\.value\s*==\s*'([^']*)'\s*\%\}", r"{% if form.resultado.value == '\1' %}", content)
# Simple check for missing space if the above regex was too strict
content = re.sub(r"form\.resultado\.value=='", r"form.resultado.value == '", content)

# Check for other potential missing spaces in the same file
content = re.sub(r"instrumento_selecionado==inst\.id", r"instrumento_selecionado == inst.id", content)
content = re.sub(r"obrigacao_selecionada==obj\.id", r"obrigacao_selecionada == obj.id", content)

if content != original:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Espaçamento do template corrigido.")
else:
    print("Nenhuma alteração necessária ou padrão não encontrado.")
