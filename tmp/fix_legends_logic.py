
import os
import re

file_path = r'templates/acoes/acao_form.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update handleFotosSelection to set legend and data-legenda
# We'll use a regex to be more precise
find_pattern = r'if \(e\.target\.dataset\.itemId\) wrapper\.dataset\.itemId = e\.target\.dataset\.itemId;'
replace_str = """if (e.target.dataset.itemId) {
                    wrapper.dataset.itemId = e.target.dataset.itemId;
                    const itemEl = document.querySelector(`[data-id="${e.target.dataset.itemId}"] .item-nome`);
                    const itemNome = itemEl ? itemEl.innerText.trim() : "";
                    wrapper.dataset.legenda = itemNome ? `Evidência: ${itemNome}` : "Nova Foto";
                }"""
content = re.sub(find_pattern, replace_str, content)

# 2. Update handleFotosSelection to set input value
find_reg = r'const regInput = wrapper\.querySelector\(`input\[name="fotos-\$\{idx\}-data_registro"\]`\);'
replace_reg = """const legInput = wrapper.querySelector(`input[name="fotos-${idx}-legenda"]`);
                if (legInput && wrapper.dataset.legenda) legInput.value = wrapper.dataset.legenda;
                const regInput = wrapper.querySelector(`input[name="fotos-${idx}-data_registro"]`);"""
content = re.sub(find_reg, replace_reg, content)

# 3. Update openPhotoCapture for existing action
find_opc = r'if \(legendaInput\) legendaInput\.value = d\.legenda;'
replace_opc = 'if (legendaInput) { legendaInput.value = d.legenda; wrapper.dataset.legenda = d.legenda; }'
content = re.sub(find_opc, replace_opc, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Ajustes de legenda concluídos.")
