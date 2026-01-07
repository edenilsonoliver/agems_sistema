import re

def check_tags(filepath):
    try:
        content = open(filepath, encoding='utf-8').read()
        tags = re.findall(r'{%\s*(if|endif|for|endfor|block|endblock)', content)
        stack = []
        for t in tags:
            if t == 'endif':
                if stack and stack[-1] == 'if': stack.pop()
                else: print(f"{filepath} - Error: endif without if")
            elif t == 'endfor':
                if stack and stack[-1] == 'for': stack.pop()
                else: print(f"{filepath} - Error: endfor without for")
            elif t == 'endblock':
                if stack and stack[-1] == 'block': stack.pop()
                else: print(f"{filepath} - Error: endblock without block. Stack: {stack}")
            else:
                stack.append(t)
        print(f"{filepath} - Final stack: {stack}")
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

check_tags('templates/instrumentos/instrumento_form_novo.html')
check_tags('templates/instrumentos/instrumento_form.html')
check_tags('templates/instrumentos/instrumento_form_novo copy.html')
