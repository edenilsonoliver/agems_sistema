---
description: Como modificar código com segurança (Protocolo de Sobrevivência)
---

# 🛑 Protocolo Obrigatório - MODO PARANOICO (ATUALIZADO)

1.  **PROIBIÇÃO DE REESTRUTURAÇÃO (RefatBan)**: Ao corrigir um bug (ex: filtro), é **TERMINANTEMENTE PROIBIDO** mover blocos de lugar, unificar scripts ou "limpar" o código adjacente. A correção deve ser um remendo cirúrgico **NO LOCAL ORIGINAL**.
2.  **INVENTÁRIO DE ESCOPO**: Antes de editar qualquer arquivo que contenha lógica (`.js`, `.py`, `.html`), o agente deve listar mentalmente (ou via log) todas as funções afetadas e garantir que 100% delas permaneçam funcionais após o edit.
3.  **BACKUPS COMPULSÓRIOS (.bak)**: Crie uma cópia de segurança antes de encostar no arquivo. Restaure-a IMEDIATAMENTE se notar regressão em botões que antes funcionavam.
4.  **DJANGO TAG INTEGRITY**: Nunca use `replace()` ou regex em strings que contenham tags Django sem testar se o balanceamento de `{% endblock %}` ou `{% endif %}` foi preservado.
5.  **AUDITORIA PÓS-GRAVAÇÃO**: NUNCA declare vitória sem usar `view_file` para ver o resultado final no disco. A mensagem de "Sucesso" da ferramenta de escrita não é prova de funcionamento.
6.  **ZERO ALUCINAÇÃO DE ESCOPO**: Se você não vê a função no seu `view_file` atual, não presuma que ela "já existe". Releia o arquivo inteiro se necessário.
7.  **TRANSPARÊNCIA TOTAL NO FRACASSO**: Se o usuário reclamar de regressão ("Você fudeu o botão X"), PARE. Admita o erro, restaure o backup e comece do zero com abordagem cirúrgica.

> 🔴 **Regra de Ouro:** Estabilidade e previsibilidade valem mais que organização de código.
