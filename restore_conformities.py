import os

file_path = r'c:\Users\rlazaro\Documents\Projetos_AGEMS\agems_sistema\templates\acoes\acao_form.html'
backup_path = file_path + '.v4.bak'

# Create backup
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(content)

# 1. Add missing modals before {% endblock %}
modals_html = """
<!-- MODAIS DE TEMPLATE -->
<div class="modal fade" id="modal-templates" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5>Templates de Conformidade</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body p-0">
                <div class="list-group list-group-flush" id="templates-list"></div>
            </div>
        </div>
    </div>
</div>

<div class="modal fade" id="modal-salvar-template" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content border-0 shadow-lg">
            <div class="modal-header bg-success text-white border-bottom-0">
                <h5>Salvar como Template</h5><button type="button" class="btn-close btn-close-white"
                    data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body p-4">
                <div class="mb-3"><label class="form-label fw-bold">Título do Template *</label><input type="text"
                        id="template-new-nome" class="form-control" placeholder="Ex: Checklist de Manutenção"></div>
                <div class="mb-3"><label class="form-label">Descrição (Opcional)</label><textarea id="template-new-descricao"
                        class="form-control" rows="3"></textarea></div>
            </div>
            <div class="modal-footer"><button type="button" class="btn btn-success text-white px-4"
                    id="btn-confirm-save-template">Confirmar e Salvar</button></div>
        </div>
    </div>
</div>

<div class="modal fade" id="modal-aplicar-template-opcoes" tabindex="-1">
    <div class="modal-dialog modal-sm modal-dialog-centered">
        <div class="modal-content border-0 shadow-lg">
            <div class="modal-header bg-primary text-white border-bottom-0 pb-2">
                <h5 class="modal-title fs-6"><i class="bi bi-download me-2"></i>Importar Template</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body text-center p-4">
                <p class="mb-4 text-muted">Como deseja aplicar este template?</p>
                <div class="d-grid gap-3">
                    <button type="button" class="btn btn-outline-primary fw-bold" id="btn-aplicar-template-adicionar">
                        <i class="bi bi-plus-circle me-2"></i>Adicionar aos existentes
                    </button>
                    <button type="button" class="btn btn-outline-danger fw-bold" id="btn-aplicar-template-sobrescrever">
                        <i class="bi bi-exclamation-triangle me-2"></i>Excluir atuais e Substituir
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
"""

if 'id="modal-templates"' not in content:
    content = content.replace('{% endblock %}', modals_html + '\n{% endblock %}')

# 2. Add missing JS functions and event listeners
# Let's find where to inject them. We'll inject before the end of the <script> block.

js_functions = """
    // --- FUNÇÕES DE TOAST / NOTIFICAÇÃO ---
    window.showToast = function(message, type = 'success') {
        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0 shadow-lg" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body"><i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>`;
        
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        container.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = document.getElementById(toastId);
        const bsToast = new bootstrap.Toast(toastElement, { delay: 4000 });
        bsToast.show();
        toastElement.addEventListener('hidden.bs.toast', () => toastElement.remove());
    };

    // --- LÓGICA DE GRUPOS E TEMPLATES ---
    window.criarGrupoAjax = function() {
        const input = document.getElementById('novo-grupo-nome-inline');
        const nome = input.value.trim();
        if (!nome) return;

        if (!window.currentAcaoId) {
            const newId = Date.now();
            window.localConformidades.push({ id: newId, nome: nome, itens: [], is_local: true });
            input.value = '';
            window.renderConformidades(window.localConformidades);
            window.showToast('Grupo adicionado (Modo Rascunho)');
            return;
        }

        const fd = new FormData();
        fd.append('nome', nome);
        fetch(`/acoes/acao/${window.currentAcaoId}/conformidades/grupo/criar/`, {
            method: 'POST', body: fd, headers: { 'X-CSRFToken': csrfToken }
        }).then(r => r.json()).then(data => {
            if (data.status === 'success') {
                input.value = '';
                window.initConformidades();
                window.showToast('Grupo criado com sucesso!');
            }
        });
    };

    let pendingTemplateId = null;
    let pendingTemplateModal = null;
    let optionsModal = null;

    window.showAplicarTemplateOptions = function (templateId, listModal) {
        pendingTemplateId = templateId;
        pendingTemplateModal = listModal;
        if (!optionsModal) {
            optionsModal = new bootstrap.Modal(document.getElementById('modal-aplicar-template-opcoes'));
        }
        optionsModal.show();
    };

    window.aplicarTemplate = function(templateId, modal, sobrescrever) {
        if (sobrescrever) {
            if (!confirm('Esta ação irá apagar TODAS as conformidades atuais desta ação. Deseja continuar?')) return;
        }

        if (!window.currentAcaoId) {
            window.showToast('Salve a ação primeiro para importar templates com estabilidade.', 'warning');
            return;
        }

        const formData = new FormData();
        formData.append('template_id', templateId);
        if (sobrescrever) formData.append('sobrescrever', 'true');

        fetch(`/acoes/acao/${window.currentAcaoId}/conformidades/aplicar-template/`, {
            method: 'POST', body: formData, headers: { 'X-CSRFToken': csrfToken }
        })
        .then(r => r.json())
        .then(data => {
            if (data.status === 'success') {
                modal.hide();
                window.initConformidades();
                window.showToast('Template aplicado com sucesso!');
            } else {
                window.showToast('Erro ao aplicar template: ' + data.message, 'danger');
            }
        });
    };
"""

# Event listeners to be added inside DOMContentLoaded
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
                    if (d.templates.length === 0) {
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
                // Se quiser permitir salvar template no modo criação, precisa enviar o JSON local
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

# Injecting JS Functions
if 'window.showToast' not in content:
    content = content.replace('// --- CONFORMIDADES ---', js_functions + '\n    // --- CONFORMIDADES ---')

# Injecting DOM Listeners
if 'btn-add-grupo-inline' not in content:
    # Find the end of DOMContentLoaded (last line before // --- GESTÃO DE DOCUMENTOS ---)
    content = content.replace('conformidadesTabBtn.addEventListener(\'shown.bs.tab\', () => window.initConformidades());', 
                            'conformidadesTabBtn.addEventListener(\'shown.bs.tab\', () => window.initConformidades());\n' + dom_listeners)

# Save the file
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Restored modals and logic successfully.")
