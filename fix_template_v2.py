import os

path = r'c:\Users\rlazaro\Documents\Projetos_AGEMS\agems_sistema\templates\acoes\acao_form.html'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_next = False
for i in range(len(lines)):
    if skip_next:
        skip_next = False
        continue
    
    line = lines[i]
    if '{% endif' in line and line.strip().endswith('{% endif'):
        # Found a line ending in a broken endif
        # Check if next line starts with %}'
        if i + 1 < len(lines) and lines[i+1].strip() == '%}':
            new_lines.append(line.rstrip() + ' %}\n')
            skip_next = True
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
