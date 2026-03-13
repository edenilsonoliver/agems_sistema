# Análise de Impacto e Risco — Restrições do Executor e Notificações

> Baseado em: `docs/PLAN-executor-restrictions.md`  
> Data: 2026-03-05

---

## Resumo Executivo

A implementação impõe restrições de UX (interface) e segurança back-end para que Executores (Técnicos de Perfil 4) manipulem apenas campos de finalização de Ação e tenham criação/edição em Instrumentos e Entidades completamente bloqueada. O risco geral dessa implementação é **Baixo-Médio**. Não há alteração de banco de dados nem migrations necessárias.

---

## Mapa de Riscos por Componente

### 1. Bloqueio Global em Instrumentos, Obrigações e Entidades (🟢 Risco Baixo)
**Mudança:** Verificar/adicionar `dispatch()` e `get_readonly()` nas views de criação e edição (`CreateView`/`UpdateView`) em `instrumentos/views.py` e `entidades/views.py` para rejeitar o perfil 4.
**Impacto:**
- O botão de "Salvar" ficará oculto para técnicos.
- Se algum técnico tentava criar essas entidades antes, ele não poderá mais e precisará pedir a um coordenador.
**Riscos:**
- Nenhum risco proativo a dados existentes. É puramente restrição de acesso a views de mutação. Acesso de leitura e listagem permanece igual.

### 2. AçãoForm com `executor_readonly` (🟡 Risco Médio)
**Mudança:** Iterar todos os campos do `AcaoForm` e definir `field.disabled = True` se não compor o escopo do Executor (Status, Finalização, Relatório).
**Impacto:**
- **Segurança garantida:** Campos `disabled` no HTML não vão no payload POST. O Django preservará os valores originais que já estão no banco porque instanciará o ModelForm com a `instance` existente.
**Riscos:**
- **Risco de UI:** Se houver campos dinâmicos em Javascript que disparam baseados nesses inputs agora bloqueados, o AJAX pode falhar silenciosamente (improvável, pois os selects de instrumento e entidade de escopo não mudaram de ID, apenas de estado).
- **Validação de Data:** Se a data_inicio puder ser antes do dia atual, e um Executor salvar a ação atrasada hoje, o ModelForm passará porque o campo inicial já estava gravado. Isso é o comportamento correto.

### 3. Sistema de Notificações com o Signal `m2m_changed` (🔴 Risco Mais Sensível)
**Mudança:** Criar um receiver `m2m_changed` em `Acao.executores.through` para disparar `Notificacao.criar_notificacao` quando novos usuários entrarem ma M2M.
**Impacto:**
- Quando o coordenador adicionar um técnico no form, ao invés de salvar silenciamente, um registro de notificação para aquele técnico será gerado.
**Riscos:**
- **Performance:** O signal M2M é disparado após a transação do Model Principal. Múltiplos executores gerarão múltiplos inserts rápidos na tabela de Alertas. Em lote (`post_save`) não é um grande problema, pois é muito pequeno.
- **Sobrescrita/Flood:** Se o Coordenador fica retirando e adicionando o Técnico da lista, o signal repetirá o push e gerará notificações duplicadas. 
  - *Mitigação Proposta:* Verificar se o tipo de modificação é `post_add` (só nas adições). Antes de criar o alerta, verificar se **já não existe** Notificacao de tipo `atribuicao` recém gerada ou na mesma hora.

---

## Tabela de Mitigações Recomendada (Pre-Deploy)

| Vulnerabilidade / Aspecto | Tratamento no Plano | Probabilidade |
| :--- | :--- | :--- |
| **Executor usar inspecionar elemento no browser pra habilitar (enable) o disabled** | Se ele fizer isso, os dados chegam no POST. Teremos que tratar a validação no `clean_field` ou não aceitar campos se ele for perfil 4. | 🟠 Improvável (mas mitigado usando interceptação na view) |
| **Pânico no Load da M2M (Circular Imports)** | No signal, o Model `Acao` e `Notificacoes` não podem conflitar. Faremos bind com `sender=Acao.executores.through`. | 🟢 Muito Baixo |
| **Bloqueio Incorreto do Dono (Responsável)** | View garante validação precisa: `if request.user == obj.responsavel -> Libera tudo`. | 🟢 Baixo |

### Recomendação Final
Podemos prosseguir, mas com **Backups de form.py e signal.py** para Rollback instantâneo. A abordagem continua cirúrgica e segura, similar ao RBAC anterior.
