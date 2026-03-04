
import os
import re

file_path = r'templates/acoes/acao_form.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find Django tags that are split across lines
# This matches {% ... %} even if they have newlines inside
def fix_tags(match):
    tag_content = match.group(0)
    # Remove interior newlines and extra spaces
    cleaned = re.sub(r'\s*\n\s*', ' ', tag_content)
    return cleaned

# Find any {% ... %} block and join it if it has newlines
content = re.sub(r'\{%.*?%\}', fix_tags, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed all split Django tags.")
