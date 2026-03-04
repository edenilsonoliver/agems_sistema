import re

file_path = r'c:\Users\rlazaro\Documents\Projetos_AGEMS\agems_sistema\templates\acoes\acao_form.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

tags = re.findall(r'{%\s*(if|endif|for|endfor|block|endblock)\s*.*?%}', content)

if_stack = []
for_stack = []
block_stack = []

errors = []

for tag in tags:
    if 'endif' in tag:
        if not if_stack: errors.append("Extra endif")
        else: if_stack.pop()
    elif 'if' in tag:
        if_stack.append('if')
        
    elif 'endfor' in tag:
        if not for_stack: errors.append("Extra endfor")
        else: for_stack.pop()
    elif 'for' in tag:
        for_stack.append('for')
        
    elif 'endblock' in tag:
        if not block_stack: errors.append("Extra endblock")
        else: block_stack.pop()
    elif 'block' in tag:
        block_stack.append('block')

if if_stack: errors.append(f"Unclosed if: {len(if_stack)}")
if for_stack: errors.append(f"Unclosed for: {len(for_stack)}")
if block_stack: errors.append(f"Unclosed block: {len(block_stack)}")

if not errors:
    print("ALL TAGS BALANCED!")
else:
    for e in errors:
        print(f"ERROR: {e}")
