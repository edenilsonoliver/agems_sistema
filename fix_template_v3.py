import os

path = r'c:\Users\rlazaro\Documents\Projetos_AGEMS\agems_sistema\templates\acoes\acao_form.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix split {% endif %} tags
import re
content = re.sub(r'\{%\s*endif\s*\n\s*%\}', r'{% endif %}', content)

# Ensure usuario lookup is safe (multiple instances)
content = content.replace(
    'data-usuario="{{ d_form.instance.usuario.get_full_name|default:d_form.instance.usuario.username }}"',
    'data-usuario="{% if d_form.instance.usuario %}{{ d_form.instance.usuario.get_full_name|default:d_form.instance.usuario.username }}{% endif %}"'
)
content = content.replace(
    'data-usuario="{{ f_form.instance.usuario.get_full_name|default:f_form.instance.usuario.username }}"',
    'data-usuario="{% if f_form.instance.usuario %}{{ f_form.instance.usuario.get_full_name|default:f_form.instance.usuario.username }}{% endif %}"'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
