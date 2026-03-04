import os

file_path = r'c:\Users\rlazaro\Documents\Projetos_AGEMS\agems_sistema\templates\acoes\acao_form.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the escaped dollar signs in template literals
content = content.replace(r'\${t.nome}', '${t.nome}')
content = content.replace(r"\${t.descricao || 'Sem descrição'}", "${t.descricao || 'Sem descrição'}")
content = content.replace(r'\${window.currentAcaoId}', '${window.currentAcaoId}')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Template literals fixed.")
