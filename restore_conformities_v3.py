import os
import re

file_path = r'c:\Users\rlazaro\Documents\Projetos_AGEMS\agems_sistema\templates\acoes\acao_form.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# DOM Listeners to add
dom_listeners = """
        // Ouvintes para Criação de Grupo
        const btnGrupoInline = document.getElementById('btn-add-grupo-inline');
        const inputGrupoInline = document.getElementById('novo-grupo-nome-inline');
        
        btnGrupoInline?.addEventListener('click', window.criarGrupoAjax);
        inputGrupoInline?.addEventListener('keypress', (e) => { 
            if (e.key === 'Enter') { 
                e.preventDefault(); 
                window.criarGrupoAjax(); 
            } 
        });

        // Ouvinte para Importar Template
        document.getElementById('btn-carregar-template')?.addEventListener('click', function() {
            const list = document.getElementById('templates-list');
            list.innerHTML = '<div class="p-4 text-center"><div class="spinner-border spinner-border-sm text-primary"></div></div>';
            const modal = new bootstrap.Modal(document.getElementById('modal-templates'));
            modal.show();
            
            fetch('/acoes/conformidades/templates/list/')
                .then(r => r.json())
                .then(d => {
                    list.innerHTML = '';
                    if (!d.templates || d.templates.length === 0) {
                        list.innerHTML = '<div class="p-4 text-center text-muted">Nenhum template encontrado.</div>';
                        return;
                    }
                    d.templates.forEach(t => {
                        const b = document.createElement('button');
                        b.className = 'list-group-item list-group-item-action py-3';
                        b.innerHTML = `<div><strong class="text-primary">${t.nome}</strong></div><small class="text-muted">${t.descricao || 'Sem descrição'}</small>`;
                        b.onclick = () => window.showAplicarTemplateOptions(t.id, modal);
                        list.appendChild(b);
                    });
                });
        });

        // Ouvintes para Opções de Aplicação de Template
        document.getElementById('btn-aplicar-template-adicionar')?.addEventListener('click', () => {
            if (optionsModal) optionsModal.hide();
            window.aplicarTemplate(pendingTemplateId, pendingTemplateModal, false);
        });

        document.getElementById('btn-aplicar-template-sobrescrever')?.addEventListener('click', () => {
            if (optionsModal) optionsModal.hide();
            window.aplicarTemplate(pendingTemplateId, pendingTemplateModal, true);
        });

        // Ouvinte para Salvar Template
        document.getElementById('btn-confirm-save-template')?.addEventListener('click', function() {
            const nome = document.getElementById('template-new-nome').value.trim();
            const descricao = document.getElementById('template-new-descricao').value.trim();
            if (!nome) { window.showToast('Informe o nome do template.', 'warning'); return; }

            const data = new FormData();
            data.append('nome', nome);
            data.append('descricao', descricao);

            let url = `/acoes/acao/${window.currentAcaoId}/conformidades/salvar-template/`;
            if (!window.currentAcaoId) {
                url = '/acoes/conformidades/template/salvar-direto/';
                data.append('conformidades_json', JSON.stringify(window.localConformidades));
            }

            fetch(url, {
                method: 'POST', body: data, headers: { 'X-CSRFToken': csrfToken }
            }).then(r => r.json()).then(d => {
                if (d.status === 'success') {
                    bootstrap.Modal.getInstance(document.getElementById('modal-salvar-template'))?.hide();
                    window.showToast('Template salvo com sucesso! ✓');
                } else {
                    window.showToast('Erro ao salvar template: ' + (d.message || 'Erro desconhecido'), 'danger');
                }
            });
        });
"""

if 'btnGrupoInline?.addEventListener' not in content:
    pattern = r'(conformidadesTabBtn\.addEventListener\s*\(\s*[\'"]shown\.bs\.tab[\'"]\s*,\s*\(\)\s*=>\s*window\.initConformidades\(\)\);)'
    replacement = r'\1\n' + dom_listeners.replace('\\', '\\\\').replace('$', '\\$')
    content = re.sub(pattern, replacement, content)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Listeners updated successfully with fix.")
else:
    print("Listeners already present.")
