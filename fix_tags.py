
import os

filepath = r'c:\Users\rlazaro\Documents\Projetos_AGEMS\agems_sistema\templates\acoes\acao_form.html'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(filepath, 'w', encoding='utf-8') as f:
    for i, line in enumerate(lines):
        # Line numbers in my view were 1-indexed.
        # Line 376-377
        if '{{ f_form.id }}{{ f_form.imagem }}{{ f_form.legenda }}{{ f_form.coordenadas }}{{' in line:
            # We assume the next line is 377
            f.write(line.strip() + lines[i+1].strip() + '\n')
            lines[i+1] = '' # Clear next line
            continue
        if 'f_form.data_registro }}{{ f_form.DELETE }}' in line and lines[i-1] == '':
             # This means we already processed it
             continue
             
        # Line 378-379
        if '{% if f_form.instance.imagem %}<a href="{{ f_form.instance.imagem.url }}"></a>{% endif' in line:
            f.write(line.strip() + lines[i+1].strip() + '\n')
            lines[i+1] = ''
            continue
        if '%}' in line and lines[i-1] == '' and i > 300 and i < 400:
            continue
            
        if line != '':
            f.write(line)
