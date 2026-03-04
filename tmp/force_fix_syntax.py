
import os

file_path = r'templates/acoes/acao_form.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix spacing around == in form.resultado.value
content = content.replace("form.resultado.value=='atendido'", "form.resultado.value == 'atendido'")
content = content.replace("form.resultado.value=='parcialmente_atendido'", "form.resultado.value == 'parcialmente_atendido'")
content = content.replace("form.resultado.value=='nao_atendido'", "form.resultado.value == 'nao_atendido'")

# Fix split tags
content = content.replace("{% if\n                                            form.resultado.value == 'parcialmente_atendido' %}", "{% if form.resultado.value == 'parcialmente_atendido' %}")
content = content.replace("{% if\n                                            form.resultado.value=='parcialmente_atendido' %}", "{% if form.resultado.value == 'parcialmente_atendido' %}")
content = content.replace("{% endif\n                                            %}", "{% endif %}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Ajuste manual concluído via script python.")
