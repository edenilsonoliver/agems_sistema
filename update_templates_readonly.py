import os

def update_templates_readonly():
    templates = [
        r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\templates\instrumentos\instrumento_form.html',
        r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\templates\entidades\entidade_form.html'
    ]
    
    for path in templates:
        if not os.path.exists(path): continue
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Inserir Alerta de Readonly no início do content
        alert_html = """
    {% if readonly %}
    <div class="alert alert-info shadow-sm d-flex align-items-center mb-4" role="alert">
        <i class="bi bi-eye-fill fs-4 me-3"></i>
        <div>
            <strong>Modo de Visualização:</strong> Você não possui permissão para editar este registro. Os campos estão desabilitados.
        </div>
    </div>
    {% endif %}
"""
        # Inserir logo após o container-fluid ou mensagens
        if '{% if messages %}' in content:
            content = content.replace('{% endif %}\n    \n    <div class="d-flex', '{% endif %}' + alert_html + '\n    <div class="d-flex')
        else:
            content = content.replace('<div class="container-fluid">', '<div class="container-fluid">' + alert_html)

        # 2. Esconder botões de Salvar
        # Procura por: <button ... Salvar
        content = re.sub(r'(<button[^>]*class="[^"]*btn-primary[^"]*"[^>]*>.*?Salvar.*?</button>)', 
                         r'{% if not readonly %}\1{% endif %}', content, flags=re.DOTALL)
        
        # 3. Esconder botões de Adicionar Obrigação / Extra
        content = re.sub(r'(<button[^>]*onclick="adicionarObrigacao\(\)"[^>]*>.*?</button>)',
                         r'{% if not readonly %}\1{% endif %}', content, flags=re.DOTALL)
        content = re.sub(r'(<button[^>]*data-bs-target="#modalImportarCSV"[^>]*>.*?</button>)',
                         r'{% if not readonly %}\1{% endif %}', content, flags=re.DOTALL)

        # 4. Esconder botões de Excluir (Lixeira)
        content = re.sub(r'(<button[^>]*onclick="removerObrigacao\(this\)"[^>]*>.*?<i class="bi bi-trash"></i>.*?</button>)',
                         r'{% if not readonly %}\1{% endif %}', content, flags=re.DOTALL)
        
        # Especial para Entidades se houver botão delete
        content = re.sub(r'(<a[^>]*href="[^"]*delete[^"]*"[^>]*>.*?Excluir.*?</a>)',
                         r'{% if not readonly %}\1{% endif %}', content, flags=re.DOTALL)

        # 5. Desabilitar botões de Modais CRUD (Plus icons)
        content = re.sub(r'(<button[^>]*data-bs-target="#modal(TipoInstrumento|Diretoria|TipoEntidade|Municipio)"[^>]*>.*?<i class="bi bi-plus-circle"></i>.*?</button>)',
                         r'{% if not readonly %}\1{% endif %}', content, flags=re.DOTALL)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    print("Templates atualizados com suporte a readonly.")

import re
if __name__ == "__main__":
    update_templates_readonly()
