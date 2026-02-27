
import re

def check_django_tags(content):
    # Very simple check for balanced tags
    tags = re.findall(r'\{%\s*(\w+)', content)
    end_tags = re.findall(r'\{%\s*end(\w+)', content)
    
    # This is too simple. Let's do a stack based approach for common tags
    stack = []
    errors = []
    
    # Pattern for all {% tag %} and {{ var }}
    # We care about tags that have ends: if, for, block, with, autoescape, compress, cache, filter, spaceless
    open_tags = ['if', 'for', 'block', 'with', 'autoescape', 'compress', 'cache', 'filter', 'spaceless']
    
    # Find all django tags
    all_tags = re.finditer(r'\{%\s*(?P<tag>\w+).*?%\}', content, re.DOTALL)
    
    for match in all_tags:
        tag_name = match.group('tag')
        line_num = content.count('\n', 0, match.start()) + 1
        
        if tag_name in open_tags:
            stack.append((tag_name, line_num))
        elif tag_name.startswith('end'):
            expected_end = tag_name[3:]
            if not stack:
                errors.append(f"Unexpected {{% {tag_name} %}} at line {line_num}")
            else:
                last_tag, last_line = stack.pop()
                if last_tag != expected_end:
                    errors.append(f"Expected {{% end{last_tag} %}} (from line {last_line}), but found {{% {tag_name} %}} at line {line_num}")
    
    for tag, line in stack:
        errors.append(f"Unclosed {{% {tag} %}} from line {line}")
        
    return errors

with open(r'c:\Users\rlazaro\Documents\Projetos_AGEMS\agems_sistema\templates\acoes\acao_form.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Check for split tags manually first
split_tags = re.findall(r'\{%[^%]*\n', content)
if split_tags:
    print("Found potential split tags:")
    for st in split_tags:
        print(f"---{st.strip()}---")

errors = check_django_tags(content)
if errors:
    print("\nErrors found:")
    for err in errors:
        print(err)
else:
    print("\nNo balancing errors found.")
