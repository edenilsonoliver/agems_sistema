
import os

file_path = r'templates/acoes/acao_form.html'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if 'id="justificativa-container"' in line:
        # Pega a linha atual e a próxima para garantir que limpamos a sujeira
        combined = line.strip() + " " + lines[i+1].strip()
        # Corrige para uma linha limpa sem escapes e sem quebras
        fixed_line = '                                <div id="justificativa-container" {% if not form.justificativa_resultado.value %}style="display:none;"{% endif %}>\n'
        new_lines.append(fixed_line)
        skip = True # Pula a próxima linha que já foi processada
    elif skip:
        skip = False
        continue
    else:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Justificativa container line cleaned and joined.")
