
import os
import re

file_path = r'templates/acoes/acao_form.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Identificamos o fechamento prematuro da aba dados (antes do card)
# E o card que está "flutuando"

# 1. Remover o </div> extra na linha 1391 (antes do card)
# 2. Inserir esse </div> após o card de resultado

# Vamos localizar o bloco específico
pattern = r'(id="add-checklist-item">.*?Adicionar Item</button>)\s*</div>\s*(<!-- SEÇÃO C: RESULTADO .*?</div><!-- /card Resultado -->)'
def move_div(m):
    return m.group(1) + '\n\n' + m.group(2) + '\n                </div>'

new_content = re.sub(pattern, move_div, content, flags=re.DOTALL)

if new_content != content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Card movido para dentro da aba Dados com sucesso.")
else:
    print("Não foi possível localizar o padrão para mover o card.")
