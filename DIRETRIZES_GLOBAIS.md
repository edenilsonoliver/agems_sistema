# Diretrizes Globais de Desenvolvimento - AGEMS Sistema

Este documento estabelece os protocolos MANDATÓRIOS para qualquer desenvolvimento ou manutenção no sistema.

## 1. Protocolo de Planejamento (Planning First)
*   **Regra:** NUNCA inicie a codificação de uma tarefa complexa sem antes apresentar um **Plano de Implementação** formal.
*   **Motivo:** Evitar retrabalho, alinhar expectativas de negócio e prever impactos colaterais.
*   **Ação:** Criar e validar o artefato `implementation_plan.md` com o usuário antes de passar para a fase de `EXECUTION`.

## 2. Segurança Defensiva e Rollback
*   **Regra:** ANTES de editar qualquer arquivo crítico (Views, Models, Configs), crie uma cópia de backup manual com extensão `.bak` ou `.backup`.
*   **Comando Padrão:** `copy arquivo.py arquivo.py.bak_motivo`
*   **Motivo:** Ferramentas de IA ou editores podem falhar. O backup manual é a última linha de defesa para restauração imediata.

## 3. Validação de Requisitos e Negócio
*   **Regra:** NÃO assuma regras de negócio (ex: "só o dono vê a ação"). PERGUNTE e confirme.
*   **Exemplo:** Ações têm `Responsável` (dono) E `Executores` (colaboradores). Ambos precisam de visibilidade.
*   **Ação:** Validar escopo de acesso e permissões antes de aplicar filtros.

## 4. Consistência Sistêmica
*   **Regra:** Uma regra de negócio (visibilidade, permissão) deve ser aplicada UNIFORMEMENTE em todas as interfaces.
*   **Checklist:** Se alterou o Dashboard, verifique:
    - [ ] Listagem Principal
    - [ ] Kanban / Quadros
    - [ ] Calendários / Agendas
    - [ ] Relatórios / Exports
    - [ ] APIs / Endpoints JSON

## 5. Senioridade na Execução
*   **Regra:** Revise seus próprios passos. Se um comando falhar, não tente "forçar". Pare, analise o erro, corrija a rota e comunique com transparência.
