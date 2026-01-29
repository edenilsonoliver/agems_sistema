// CORREÇÃO: Renderização de documentos existentes
// Substituir a função renderExistingAssets para documentos

function renderExistingAssets(type) {
    const container = document.getElementById(`${type}-hidden-forms`);
    const forms = container.querySelectorAll(`[class^="hidden-${type.slice(0, -1)}"]`);

    forms.forEach(form => {
        const index = form.dataset.index;
        const idInput = form.querySelector('input[name$="-id"]');

        // Só renderiza se for item existente (tem PK)
        if (idInput && idInput.value) {
            if (type === 'docs') {
                const fileInput = form.querySelector('input[type="file"]');
                const descInput = form.querySelector('input[name$="-descricao"]');
                
                if (fileInput && fileInput.value) {
                    // Extrair apenas o nome do arquivo do caminho completo
                    const fullPath = fileInput.value;
                    const fileName = fullPath.split('/').pop().split('\\').pop();
                    
                    renderDocRow(null, index, true, {
                        name: fileName,
                        url: fullPath,
                        descricao: descInput ? descInput.value : ''
                    });
                }
            } else if (type === 'fotos') {
                const imgLink = form.querySelector('a');
                const descInput = document.querySelector(`input[name="fotos-${index}-legenda"]`);
                const coords = form.dataset.coordenadas;
                const dateReg = form.dataset.registro;
                const dateEnv = form.dataset.envio;

                if (imgLink) {
                    renderFotoRow(null, index, coords, dateReg || dateEnv, null, true, {
                        url: imgLink.href,
                        legenda: descInput ? descInput.value : ''
                    });
                }
            }
        }
    });
}
