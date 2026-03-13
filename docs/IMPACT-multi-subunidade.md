# IMPACT: Análise de Risco - Múltiplas Subunidades

A migração de um campo direto (`ForeignKey`) para um relacionamento de muitos-para-muitos (`ManyToManyField`) é uma alteração estrutural profunda que exige cuidado extremo com a persistência de dados.

---

## 🚦 Riscos Identificados

| Categoria | Risco | Impacto | Mitigação |
|:---|:---:|:---:|:---|
| **Integridade de Dados** | Perda do vínculo atual durante a migração. | Alto | Criaremos o campo novo `subunidades` mantendo o antigo `subunidade` temporariamente. Um script via Django Shell fará o "de-para" antes da deleção do campo antigo. |
| **Performance** | Lentidão em consultas complexas com ManyToMany (Joins extras). | Médio | Utilização de `prefetch_related('subunidades')` em todas as views de listagem para evitar o problema N+1. |
| **RBAC / Segurança** | Falha na lógica de filtragem `Q(subunidades=user.subunidade)` permitindo acesso indevido. | Alto | Bateria de testes de PoC (como a do CATENE vs CATEGAS) será rodada especificamente para o cenário de Múltiplas Subunidades. |
| **UX / Interface** | Confusão do usuário ao selecionar múltiplas unidades. | Baixo | Uso de widgets de seleção múltipla claros (como Select2 ou checkboxes) com labels de sigla da diretoria. |

---

## 🛠️ Mitigação Técnica: O Script de Migração

Antes de qualquer `migrate`, o plano prevê o seguinte fluxo seguro:
1. Adicionar campo `subunidades` (M2M).
2. Gerar migration.
3. **Executar script de dados:**
   ```python
   for inst in Instrumento.objects.all():
       if inst.subunidade:
           inst.subunidades.add(inst.subunidade)
   ```
4. Verificar se a contagem de vínculos bate.
5. Só então, desativar o campo antigo.

---

> **CONSIDERAÇÃO FINAL:** Esta mudança elimina a "gambiarra" de campo único e permite que o sistema escale para casos complexos onde um contrato atravessa várias coordenações. É a abordagem correta e definitiva para o AGEMS.
