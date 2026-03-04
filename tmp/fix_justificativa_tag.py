
import os
import re

file_path = r'templates/acoes/acao_form.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the split {% if %} and {% endif %} tag for justificativa
# Looking for:
# <div id="justificativa-container" {% if not form.justificativa_resultado.value
#                                     %}style="display:none;" {% endif %}>

pattern = r'\{\%\s*if\s+not\s+form\.justificativa_resultado\.value\s*\n\s*\%\}style="display:none;"\s*\{\%\s*endif\s*\%\}'
replacement = r"{% if not form.justificativa_resultado.value %}style=\"display:none;\"{% endif %}"

new_content = re.sub(pattern, replacement, content)

if new_content == content:
    # If the regex above didn't match due to slight whitespace differences, try a more flexible one
    pattern_flex = r'\{\%\s*if\s+not\s+form\.justificativa_resultado\.value\s*.*?\%\}style="display:none;"\s*\{\%\s*endif\s*\%\}'
    new_content = re.sub(pattern_flex, replacement, new_content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Split tag for justificativa fixed.")
