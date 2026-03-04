
import os
import re

file_path = r'templates/acoes/acao_form.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Count {% if %} vs {% endif %}
# Note: {% if ... %} can also be {% for ... %} etc.
# But user specifically mentioned endif/endblock.

if_count = len(re.findall(r'\{%\s*if\s+', content))
elsif_count = len(re.findall(r'\{%\s*elif\s+', content))
endif_count = len(re.findall(r'\{%\s*endif\s*%\}', content))

for_count = len(re.findall(r'\{%\s*for\s+', content))
endfor_count = len(re.findall(r'\{%\s*endfor\s*%\}', content))

block_count = len(re.findall(r'\{%\s*block\s+', content))
endblock_count = len(re.findall(r'\{%\s*endblock\s*%\}', content))

print(f"IFs: {if_count}, ENDIFs: {endif_count}")
print(f"FORs: {for_count}, ENDFORs: {endfor_count}")
print(f"BLOCKs: {block_count}, ENDBLOCKs: {endblock_count}")

# Check for any remaining split tags
splits = re.findall(r'\{%[^%]*\n[^%]*%\}', content)
if splits:
    print(f"WARNING: Still found {len(splits)} split tags!")
else:
    print("No split tags found.")
