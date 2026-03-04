
import os
import re

file_path = r'templates/acoes/acao_form.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. MOVER 'FOI ATENDIDO' PARA DENTRO DA ABA DADOS
# Localizar o card
match_card = re.search(r'<!-- SEÇÃO C: RESULTADO .*?</div><!-- /card Resultado -->', content, re.DOTALL)
if match_card:
    card_html = match_card.group(0)
    # Remove da posição atual (que estava fora das divs de tab-pane)
    content = content.replace(card_html, '')
    
    # Inserir no final da div 'dados'
    # Procuramos o final da div que contém o botão de adicionar item
    find_pattern = r'<button type="button" class="btn btn-sm btn-outline-primary" id="add-checklist-item">.*?</button>\s*</div>'
    def insert_card(m):
        return m.group(0) + '\n\n                ' + card_html
    
    content = re.sub(find_pattern, insert_card, content, flags=re.DOTALL)

# 2. CORREÇÃO DAS LEGENDAS DAS FOTOS
# Adicionar data-legenda no wrapper do formset de fotos
find_wrapper = r'data-usuario="\{% if f_form.instance.usuario %\}\{% firstof f_form.instance.usuario.get_full_name f_form.instance.usuario.username %\}\{% endif %\}">'
replace_wrapper = 'data-usuario="{% if f_form.instance.usuario %}{% firstof f_form.instance.usuario.get_full_name f_form.instance.usuario.username %}{% endif %}" data-legenda="{{ f_form.instance.legenda|default:\'\' }}">'
content = content.replace(find_wrapper, replace_wrapper)

# Atualizar o JS para ler o data-legenda se o input estiver vazio (inicialização)
find_js = r'const legenda = form.querySelector\(\'input\[name\$="-legenda"\]\'\)\?\.value \|\| \'\';'
replace_js = "const legenda = form.dataset.legenda || form.querySelector('input[name$=\"-legenda\"]')?.value || '';"
content = re.sub(find_js, replace_js, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Ajustes concluídos com sucesso.")
