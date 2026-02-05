# -*- coding: utf-8 -*-
"""Script para adicionar ícone do sino ao título."""

# Ler o arquivo atual
with open(r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\templates\alertas\historico.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituição cirúrgica: adicionar ícone do sino, mas manter título em preto
content = content.replace(
    '<h2 class="fw-bold mb-0">\n                Histórico de Notificações',
    '<h2 class="fw-bold mb-0">\n                <i class="bi bi-bell me-2"></i>Histórico de Notificações'
)

# Salvar
with open(r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\templates\alertas\historico.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Ícone do sino adicionado ao título")
print("✓ Título mantém cor preta (sem text-primary)")
