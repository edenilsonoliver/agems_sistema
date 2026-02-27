
import os

file_path = r'c:\Users\rlazaro\Documents\Projetos_AGEMS\agems_sistema\templates\acoes\acao_form.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the specific crash points by joining the split tags
# Crash 1: line 114-115
content = content.replace(
    '{% for field in form %}{% if field.errors %}<li><strong>{{ field.label }}:</strong> {{\n                field.errors|striptags }}</li>{% endif %}{% endfor %}',
    '{% for field in form %}{% if field.errors %}<li><strong>{{ field.label }}:</strong> {{ field.errors|striptags }}</li>{% endif %}{% endfor %}'
)

# Crash 2: line 305-306
content = content.replace(
    '{{ f_form.id }}{{ f_form.imagem }}{{ f_form.legenda }}{{ f_form.coordenadas }}{{\n                                f_form.data_registro }}{{ f_form.DELETE }}',
    '{{ f_form.id }}{{ f_form.imagem }}{{ f_form.legenda }}{{ f_form.coordenadas }}{{ f_form.data_registro }}{{ f_form.DELETE }}'
)

# Crash 3: line 307-308
content = content.replace(
    '{% if f_form.instance.imagem %}<a href="{{ f_form.instance.imagem.url }}"></a>{% endif\n                                %}',
    '{% if f_form.instance.imagem %}<a href="{{ f_form.instance.imagem.url }}"></a>{% endif %}'
)

with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print("Fixes applied successfully via Python script.")
