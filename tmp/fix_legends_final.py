
import os
import re

file_path = r'templates/acoes/acao_form.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Garantir que data-legenda esteja no wrapper do formset de fotos
# Procuramos o loop das fotos
find_loop_start = r'{% for f_form in fotos_formset %}\s*<div class="hidden-foto-form" data-index="{{ forloop.counter0 }}"'

# Vamos substituir o bloco inicial do div por um que inclua todos os dados necessários, incluindo a legenda
replace_loop_start = '''{% for f_form in fotos_formset %}
                            <div class="hidden-foto-form" data-index="{{ forloop.counter0 }}"
                                data-coordenadas="{{ f_form.instance.coordenadas|default:'' }}"
                                data-registro="{{ f_form.instance.data_registro|date:'d/m/Y H:i' }}"
                                data-envio="{{ f_form.instance.data_envio|date:'d/m/Y H:i' }}"
                                data-item-id="{{ f_form.instance.item_conformidade_id|default:'' }}"
                                data-legenda="{{ f_form.instance.legenda|default:'' }}"
                                data-usuario="{% if f_form.instance.usuario %}{% firstof f_form.instance.usuario.get_full_name f_form.instance.usuario.username %}{% endif %}">'''

content = re.sub(find_loop_start, replace_loop_start, content, flags=re.DOTALL)

# 2. Garantir que o JS renderExistingAssets use o data-legenda
# Localizar a função renderExistingAssets para Fotos
find_js_legenda = r'const legenda = form\.dataset\.legenda \|\| form\.querySelector\(\'input\[name\$="-legenda"\]\'\)\?\.value \|\| \'\';'
# Já deve estar assim se o script anterior rodou, mas vou garantir.

# Verificando se o JS está correto
if 'const legenda = form.dataset.legenda || form.querySelector(\'input[name$="-legenda"]\')?.value || \'\';' not in content:
    # Tenta o padrão antigo caso não tenha sido substituído
    old_js = r'const legenda = form\.querySelector\(\'input\[name\$="-legenda"\]\'\)\?\.value \|\| \'\';'
    content = re.sub(old_js, "const legenda = form.dataset.legenda || form.querySelector('input[name$=\"-legenda\"]')?.value || '';", content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Correção das legendas aplicada.")
