# 🚀 Plano Revisão Arquitetural e Estratégia de Acesso - AGEMS

**Data:** 26/01/2026
**Status:** Proposto
**Autor:** Antigravity Agent

---

## 1. Análise Situacional
F
### Pontos Fortes Identificados:
*   **Modelo de Dados Coerente:** A hierarquia `Instrumento -> Obrigação -> Ação -> Checklist` é sólida e reflete bem o negócio.
*   **Automação Básica:** O cálculo automático de progresso (`atualizar_progresso`) via Signals no checklist é uma boa sacada de UX.
*   **Auditabilidade:** Presença de `data_cadastro` e `data_atualizacao` em quase todos os modelos principais.

### Pontos de Atenção (Gargalos):
*   **Permissões Rígidas:** O uso de verificações hardcoded como `if self.perfil == 3` dificulta a manutenção e a escalabilidade. A criação de novos perfis exige refatoração em múltiplos pontos.
*   **Lógica de Negócio nos Models:** Métodos de permissão e regras de apresentação (`get_perfil_display_completo`) estão acoplados aos modelos, violando o princípio de responsabilidade única.
*   **Risco na Integridade de Dados:** O uso de `on_delete=CASCADE` em relacionamentos críticos (como Instrumento -> Obrigações) é arriscado para um sistema regulatório, onde a perda acidental de um contrato mestre pode apagar todo o histórico de execuções.
*   **Falta de Soft Deletes:** Não há mecanismo nativo para "lixeira" ou deleção lógica, o que é crucial para auditoria.

---

## 2. Estratégia de Gestão de Perfis (RBAC - Role Based Access Control)

A estratégia recomendada é transitar do modelo atual (baseado em um campo `Integer` fixo) para o sistema de **Groups e Permissions** nativo do Django, encapsulado em regras de negócio claras.

### A Nova Estratégia: "Grupos como Papéis Funcionais"

Ao invés de verificar *quem* é o usuário (cargo), verificaremos *o que* ele pode fazer (permissão).

#### Definição Sugerida dos Grupos (Roles):

1.  **Administrador do Sistema (Superuser)**
    *   *Escopo:* Acesso irrestrito ao sistema e painel administrativo.
    
2.  **Gestor de Instrumentos (Nível Diretoria/Assessoria)**
    *   *Permissões:* `add_instrumento`, `change_instrumento`, `delete_instrumento` (lógico), `change_entidade`.
    *   *Regra de Negócio:* Visualiza tudo, mas edita preferencialmente itens da sua Diretoria.

3.  **Técnico/Fiscal (Nível Coordenação)**
    *   *Permissões:* `change_acao`, `add_checklistitem`, `view_instrumento`, `view_obrigacao`.
    *   *Regra:* Executor. Não cria contratos, apenas operacionaliza as ações e reporta progresso.

4.  **Auditoria/Visualizador**
    *   *Permissões:* Apenas permissões de leitura (`view_*`) em todos os módulos.

#### Plano de Migração de Permissões:
*   Criar um script `management command` para inicializar esses grupos e atribuir as permissões programaticamente.
*   Substituir verificações `if user.perfil == X` por `if user.has_perm('app.action')` ou mixins `PermissionRequiredMixin`.

---

## 3. Plano de Melhorias (Módulo a Módulo)

### 🛡️ Módulo: Usuários (Auth)
*   **Refatoração:** Decoplar lógica de apresentação (ex: `get_perfil_display_completo`) para *Template Tags* ou *Helpers*.
*   **Segurança:** Implementar **Logs de Auditoria de Acesso** (Middleware) para rastrear quem visualizou dados sensíveis.
*   **Validação:** Reforçar a validação de acesso hierárquico (Diretoria -> Subunidade) via *QuerySet Filtering* (Managers customizados).

### 🏢 Módulo: Entidades
*   **Integridade:** Implementar algoritmo de validação real de CNPJ no método `clean()`.
*   **UX/SEO:** Adicionar campo `slug` para URLs amigáveis (ex: `/entidades/aguas-guariroba/`).

### 📜 Módulo: Instrumentos & Obrigações
*   **Segurança Crítica:** Alterar `on_delete=CASCADE` nas Obrigações para `PROTECT` (impedir deleção de contrato se houver obrigações) ou implementar `SoftDeleteModel`.
*   **Consistência:** Implementar validação cruzada de datas no `clean()` (Garantir que `data_fim` >= `data_inicio`).
*   **Unicidade:** Avaliar se o campo `nup` (Protocolo) deve ser `unique=True` para evitar duplicidade de processos.

### ⚡ Módulo: Ações & Checklists
*   **Performance:** Utilizar `select_related` e `prefetch_related` nas Views de listagem para mitigar o problema de N+1 queries.
*   **Concorrência:** Revisar o método `atualizar_progresso` para garantir atomicidade, prevenindo inconsistências se múltiplos usuários editarem checklists simultaneamente.
*   **QuerySets:** Criar Managers customizados (ex: `Acao.objects.atrasadas()`, `Acao.objects.minhas(user)`) para limpar a lógica das views.

---

## 4. Roteiro de Execução

1.  **Fase 1: Integridade e Segurança (Concluído ✅)**
    *   [x] Implementar validações de DATA (`clean()`) nos models (Instrumentos e Ações).
    *   [x] Proteger relacionamentos críticos (`on_delete=PROTECT` em Obrigações e Ações).
    *   [x] Corrigir dependências do ambiente (`django-import-export`).

2.  **Fase 2: Refatoração de Auth (Concluído ✅)**
    *   [x] Criar estrutura automatizada de Grupos/Permissões (`management command: setup_permissions`).
    *   [x] Migrar lógica de views para `PermissionRequiredMixin` (Instrumentos, Entidades, Ações).
    *   [x] Atualizar formulários e models de Usuário para sincronizar Perfil -> Grupo Django.
    *   [x] Atualizar nomenclatura de perfis para refletir funções (Gestor, Técnico, Visualizador).

3.  **Fase 3: Performance e Polimento (Pendente - Próximo Passo 🚀)**
    *   [ ] **Otimização de Queries:** Usar `select_related` e `prefetch_related` para resolver problemas de N+1 (especialmente em listagens e API check).
    *   [ ] **Soft Deletes:** Implementar mecanismo de deleção lógica para garantir auditoria completa.
    *   [ ] **API Performance:** Revisar endpoints JSON do calendário e formulários dinâmicos.
    *   [ ] **Auditoria:** Implementar logs de acesso simples (Middleware).

4.  **Fase 4: Kanban e Polimento**
    **Objetivo:** Integrar a visão Kanban aos novos filtros de visibilidade e refinar a experiência do usuário.

    ### 4.1. Visibilidade do Kanban
    - **Problema:** A visão Kanban pode estar exibindo todas as ações ou apenas as do responsável, sem considerar os executores.
    - **Solução:** Aplicar o mesmo filtro `Q(responsavel) | Q(executores)` na view do Kanban.

    ### 4.2. Notificações (Planejamento)
    - **Objetivo:** Alertar usuários sobre prazos próximos.
    - **Estratégia:** Criar comando de management para verificar datas e criar alertas no sistema/email.

5.  **Fase 5: Melhoria em Ações e Obrigações**
    **Objetivo:** Enriquecer o registro de Ações com tipagem robusta e gestão documental comprobatória.

    ### 5.1. Tipos de Ação Personalizáveis
    - **Requisito:** Permitir tipagem (Fiscalização, Monitoramento, Visita Técnica, etc.).
    - **Ação:** Refinar cadastro de `TipoAcao` e adaptar formulário da Ação para destacar este campo.
    - **Customização:** Avaliar campos dinâmicos por tipo (futuro).

    ### 5.2. Gestão de Evidências e Documentos
    - **Requisito:** Aba "Documentos/Evidências" para anexar PDFs, DOCs, XLSs.
    - **Rastreabilidade:** Registrar quem enviou e quando.
    - **Ação:** Criar modelo `AcaoDocumento`.

    ### 5.3. Registro Fotográfico (Fiscalização)
    - **Requisito:** Área específica para fotos de campo.
    - **Ação:** Criar modelo `AcaoFoto` com suporte a metadados visualizáveis (galeria).
    - **Interface:** Implementar sistema de abas na edição da Ação (Dados, Checklist, Docs, Fotos).

---
**Última atualização:** 27/01/2026 - FASE 4 Concluída. Iniciando Planejamento da FASE 5.
