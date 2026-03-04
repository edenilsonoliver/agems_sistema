
import os

file_path = r'templates/acoes/acao_form.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # Detect split if tag: starts with {% if and has no %} on the same line
    if '{% if' in line and '%}' not in line and i + 1 < len(lines):
        next_line = lines[i+1].lstrip()
        merged = line.rstrip() + " " + next_line
        new_lines.append(merged)
        i += 2
    else:
        new_lines.append(line)
        i += 1

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Merged split tags.")
