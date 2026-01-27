# 🚀 Plano Revisão Arquitetural e Estratégia de Acesso - AGEMS

**Data:** 26/01/2026
**Status:** Proposto
**Autor:** Antigravity Agent

---

## 1. Análise Situacional

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

## 4. Roteiro de Execução Sugerido

1.  **Fase 1: Integridade e Segurança (Imediato)**
    *   Implementar validações de DATA (`clean()`) nos models.
    *   Proteger relacionamentos críticos (remover `CASCADE` perigoso).
    *   Backup completo do banco antes de alterações estruturais.

2.  **Fase 2: Refatoração de Auth (Curto Prazo)**
    *   Criar estrutura de Grupos/Permissões.
    *   Migrar lógica de views para usar permissões e não "perfil numérico".

3.  **Fase 3: Performance e Polimento (Médio Prazo)**
    *   Otimização de queries (Django Debug Toolbar).
    *   Implementação de Soft Deletes.
