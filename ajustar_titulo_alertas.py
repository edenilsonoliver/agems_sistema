# -*- coding: utf-8 -*-
"""Script para ajustar o título da página de alertas."""

# Ler o arquivo atual
with open(r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\templates\alertas\historico.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituição cirúrgica: remover text-primary e ícone
content = content.replace(
    '<h2 class="fw-bold text-primary mb-0">\n                <i class="bi bi-bell me-2"></i>Histórico de Notificações',
    '<h2 class="fw-bold mb-0">\n                Histórico de Notificações'
)

# Salvar
with open(r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\templates\alertas\historico.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Título ajustado: removido 'text-primary' e ícone")
print("✓ Agora segue o padrão da página Entidades")
