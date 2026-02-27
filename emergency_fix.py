
import os

file_path = r'c:\Users\rlazaro\Documents\Projetos_AGEMS\agems_sistema\templates\acoes\acao_form.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix crash points
# Fix 1: Form errors split tag
content = content.replace(
    '<li><strong>{{ field.label }}:</strong> {{\n                field.errors|striptags }}</li>',
    '<li><strong>{{ field.label }}:</strong> {{ field.errors|striptags }}</li>'
)

# Fix 2: Fotos formset split tags
content = content.replace(
    '{{ f_form.id }}{{ f_form.imagem }}{{ f_form.legenda }}{{ f_form.coordenadas }}{{\n                                f_form.data_registro }}{{ f_form.DELETE }}',
    '{{ f_form.id }}{{ f_form.imagem }}{{ f_form.legenda }}{{ f_form.coordenadas }}{{ f_form.data_registro }}{{ f_form.DELETE }}'
)

# Fix 3: Fotos instance image split tag
content = content.replace(
    '{% if f_form.instance.imagem %}<a href="{{ f_form.instance.imagem.url }}"></a>{% endif\n                                %}',
    '{% if f_form.instance.imagem %}<a href="{{ f_form.instance.imagem.url }}"></a>{% endif %}'
)

with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print("Emergency fixes applied via Python script.")
