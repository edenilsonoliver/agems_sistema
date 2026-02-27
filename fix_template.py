import os

path = r'c:\Users\rlazaro\Documents\Projetos_AGEMS\agems_sistema\templates\acoes\acao_form.html'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Fix the broken endif tag specifically
    if '{% endif' in line and not '%}' in line:
        new_lines.append(line.replace('{% endif', '{% endif %}'))
    elif line.strip() == '%}' and len(new_lines) > 0 and '{% endif %}' in new_lines[-1]:
        # Skip the next line if it was just the closing part of the endif
        continue
    else:
        new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
