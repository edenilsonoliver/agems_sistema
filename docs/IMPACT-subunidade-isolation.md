# IMPACT: Análise de Risco - Isolamento Rigoroso por Subunidade

Esta análise avalia os impactos da inserção da rastreabilidade por **Subunidade** no modelo `Instrumento` e a refatoração dos filtros do RBAC (Role-Based Access Control) dentro da plataforma AGEMS.

---

## 🚦 Tabela Consolidada de Riscos e Impactos

| Componente Afetado | Gravidade | Descrição do Risco | Estratégia de Mitigação |
|:---|:---:|:---|:---|
| **`instrumentos.models.Instrumento`** | ALTA | **Quebra de Banco de Dados:** Adicionar uma coluna estrutural (`subunidade`) num banco em produção pode causar erros de integridade se não for `null=True`, exigindo recarga de dados default. | O novo campo será criado como `null=True, blank=True` com `on_delete=models.PROTECT`. Migração limpa gerada pelo Django limitará o downtime. |
| **`usuarios.mixins.get_diretoria_filter`** | ALTA | **Cegueira de Dados (Data Blackout):** Alterar o retorno dos filtros para checar rigidamente `subunidade=user.subunidade` fará com que todos os dados legados (sem subunidade) sumam da vista dos perfis 2, 3 e 4 da noite para o dia. | **Fallback de Transição:** O filtro para perfis 2, 3 e 4 buscará: `(subunidade=user.subunidade) OR (subunidade IS NULL AND diretoria=user.subunidade.diretoria)`. Isso mantém os dados antigos visíveis até que o Admin os reclassifique na Subunidade correta. |
| **`instrumentos.views.InstrumentoCreateView`** | MÉDIA | **Fraude no Cadastro:** Um usuário Perfil 4 poderia manipular o POST (inspecionar elemento) e forçar a criação de um Instrumento na Subunidade de outro grupo (Ex: Técnico da CATENE salvando na CATEGAS). | **Injeção Back-End:** O campo `subunidade` no `InstrumentoForm` ficará bloqueado para os perfis < 1. A View no `form_valid()` injetará compulsoriamente: `form.instance.subunidade = request.user.subunidade`. |
| **`acoes.forms.AcaoForm`** | ALTA | **Vazamento de Pessoal (Executores Cruzados):** Hoje o formulário lista *todos* os usuários daquela Diretoria no campo de Executores. Mesmo mudando o Instrumento para pertencer a uma subunidade, o query de usuários pode continuar vazando a diretoria inteira se não for reescrito. | **Refatoração Direta:** O `AcaoForm.__init__` será reescrito para checar se `Instrumento.subunidade` existe. Se sim, o menu _dropdown_ trará **somente** os usuários logados naquela `subunidade`. |
| **Dashboard e Count Views** | BAIXA | **Inconsistência Numérica:** Diretores validarem números e os totais não baterem com as listas que as Subunidades informam. | Nenhuma mudança massiva. O cenário do Diretor fica preservado pois o `Q` filter de "Filtrar Tudo Abaixo da Minha Diretoria" permanece para ele. |

---

## 🛠️ O Plano de Ação Seguro (Step-by-Step)

Para minimizar as chances de downtime (tempo fora do ar) e quebra da aplicação durante a produção, utilizaremos uma abordagem **"Non-Breaking" (Não Destrutiva)**:

1. **Alteração Mínimo-Invasiva do `models.py`:**
   Daremos vida ao campo `subunidade` silenciosamente (`null=True, blank=True`). Faremos os preenchimentos do BD (Makemigrations & Migrate). Ninguém vai notar, pois a interface não mudou ainda.
2. **Atualização Condicional dos `mixins.py`:**
   Implementaremos a lógica de "Fallback de Retrocompatibilidade" detalhada na tabela acima. Um código tolerante a falhas transicionais.
3. **Bloqueio Injetivo dos Forms:**
   Apenas depois de garantir os passos 1 e 2, subimos a modificação nos forms (`InstrumentoForm`, `AcaoForm`) trancando e injetando a amarra da subunidade por trás da cortina (Backend-First validation).

---

> 📝 **NOTA DE AVALIAÇÃO:** A mudança possui *risco sistêmico real*, mas as técnicas de "Fallback Tolerante" descritas acima zeram as chances de "blackout" de dados do dia pra noite. Os usuários continuarão trabalhando perfeitamente amanhã de manhã. Você valida essa abordagem Non-Breaking? Se sim, começo a alterar `models.py` e criar a Migration.
