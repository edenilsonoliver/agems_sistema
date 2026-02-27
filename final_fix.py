import re
import os

filepath = r'c:\Users\rlazaro\Documents\Projetos_AGEMS\agems_sistema\templates\acoes\acao_form.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the split {% endif %} tags for images
content = re.sub(r'\{%\s*endif\s*\n\s*%\}', r'{% endif %}', content)

# Fix the split tags in fotos formset
content = re.sub(r'\{\{\s*\n\s*f_form\.data_registro\s*\}\}', r'{{ f_form.data_registro }}', content)

# Also fix the split tags in checklist if any
content = re.sub(r'\{\{\s*\n\s*c_form\.nome\|as_crispy_field\s*\}\}', r'{{ c_form.nome|as_crispy_field }}', content)

# Now Let's also restore the data-usuario and data-data attributes safely to avoid 'Failed lookup'
# For docs
doc_safe_usuario = 'data-usuario="{% if d_form.instance.usuario %}{% firstof d_form.instance.usuario.get_full_name d_form.instance.usuario.username %}{% endif %}"'
doc_safe_data = 'data-data="{{ d_form.instance.data_envio|date:\'d/m/Y H:i\' }}"'

content = content.replace(
    'data-url="{% if d_form.instance.arquivo %}{{ d_form.instance.arquivo.url }}{% endif %}">',
    'data-url="{% if d_form.instance.arquivo %}{{ d_form.instance.arquivo.url }}{% endif %}"\n                                ' + doc_safe_usuario + '\n                                ' + doc_safe_data + '>'
)

# For fotos
foto_safe_usuario = 'data-usuario="{% if f_form.instance.usuario %}{% firstof f_form.instance.usuario.get_full_name f_form.instance.usuario.username %}{% endif %}"'

content = content.replace(
    'data-envio="{{ f_form.instance.data_envio|date:\'d/m/Y H:i\' }}">',
    'data-envio="{{ f_form.instance.data_envio|date:\'d/m/Y H:i\' }}"\n                                ' + foto_safe_usuario + '>'
)

# Unify the split curly braces that I keep seeing
content = content.replace('{{\n                                f_form.data_registro }}', '{{ f_form.data_registro }}')
content = content.replace('{% endif\n                                %}', '{% endif %}')

# Ensure no hidden characters are messing up the split tags
content = content.replace('{% endif\r\n                                %}', '{% endif %}')

with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print("File fixed successfully")
