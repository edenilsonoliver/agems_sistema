
with open(r'c:\Users\rlazaro\Documents\Projetos_AGEMS\agems_sistema\templates\acoes\acao_form.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'endif' in line:
            print(f"{i+1}: {line.strip()}")
