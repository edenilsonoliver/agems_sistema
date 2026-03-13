# Análise de Impacto — RBAC Isolamento por Diretoria

> Baseado em: `docs/PLAN-rbac-diretoria-isolation.md`  
> Data: 2026-03-05

---

## Resumo Executivo

A implementação do isolamento RBAC por diretoria/subunidade exige alterações em **6 arquivos Python** e impacta **todos os módulos de negócio**. O risco geral é **Médio-Alto** — não há mudanças de schema de banco de dados, mas todos os usuários não-Admin passarão a enxergar um subconjunto menor de dados ao invés de tudo.

> [!CAUTION]
> **Impacto imediato para usuários em produção:** Após o deploy, usuários com perfil 1–5 deixarão de ver registros de outras diretorias. Se existem dados que cruzam diretorias (ex: ação de Diretoria A criada por usuário da Diretoria B), esses registros tornam-se "invisíveis" — mas NÃO são deletados.

---

## Mapa de Impacto por Módulo

### 1. Instrumentos (🔴 Alto)

**Estado atual:** `InstrumentoListView.get_queryset()` retorna `Instrumento.objects.all()` sem nenhum filtro de diretoria.

**Impacto da mudança:**
- Usuários de perfil 1–4 passarão a ver **apenas instrumentos da sua diretoria**
- Tentativas de acessar `/instrumentos/<pk>/editar/` de outra diretoria via URL direta → redirecionado com erro
- `InstrumentoCreateView` precisará **forçar `diretoria = user.diretoria`** para perfis 1–4 (previne manipulação de POST)

**Risco:** Médio — campo `diretoria` já existe no modelo. Sem migration.

**Ponto de atenção:** Se um instrumento foi cadastrado SEM diretoria (campo pode ser null?), ele desaparecerá das listas filtradas. → **Verificar dados existentes.**

---

### 2. Ações (🔴 Alto)

**Estado atual:** `AcaoListView.get_queryset()` só filtra perfis 3 e 4 pelo próprio usuário. Perfis 0, 1, 2 e 5 veem **todas as ações do sistema**.

**Impacto da mudança:**
- Perfis 1 e 2 passarão a ver apenas ações dentro da sua diretoria (`obrigacao__instrumento__diretoria`)
- Perfil 5 (Visualizador) passará a ver apenas ações das diretorias autorizadas
- `acoes_json` (endpoint do calendário) deve receber o mesmo filtro → calendário ficará consistente
- `AcaoUpdateView` e `AcaoDeleteView` precisam de `dispatch()` com verificação de ownership

**O que JÁ está correto (não mexer):**
- `AcaoForm.__init__` já filtra responsável/executor por diretoria do instrumento ✅
- `get_obrigacoes_por_instrumento` já filtra usuários por diretoria do instrumento ✅

**Risco:** Alto — a cadeia é `Acao → Obrigacao → Instrumento → Diretoria`. Se algum instrumento estiver sem diretoria, as ações correspondentes ficam "orfãs" e somem do filtro.

---

### 3. Dashboard (🟡 Médio)

**Estado atual:** `dashboard_principal` filtra perfis 3/4 pelo `responsavel/executor`, mas perfis 0, 1, 2 veem **contadores globais** (`Acao.objects.all()`, `Instrumento.objects.filter(status='vigente')` sem diretoria).

**Impacto da mudança:**
- Diretor verá contadores apenas da sua diretoria
- **Widgets de gráfico** (distribuição por tipo de instrumento, ações por status) também serão filtrados
- Os números nos cards de "Ações Vencidas" e "A Vencer" mudarão para a realidade da diretoria

**Risco:** Baixo — mudança é cosmética (números menores). Lógica de negócio não quebra.

---

### 4. Indicadores (🟡 Médio)

**Estado atual:** `IndicadorListView` lista `IndicadorContratual.objects.all()` — sem filtro.

**Análise:**
- `IndicadorContratual` não tem FK de diretoria (é uma definição global de indicador)
- `ValorIndicador` tem FK para `Instrumento` (contrato) → acessa diretoria indiretamente
- **Decisão recomendada:** `IndicadorContratual` permanece global (sem filtro). `ValorIndicador` filtrado por `contrato__diretoria` se houver view de listagem de valores

**Risco:** Baixo — `IndicadorContratual` é uma tabela de configuração, não de operação.

---

### 5. Entidades (🟢 Baixo / Sem mudança recomendada)

**Estado atual:** `EntidadeListView` sem filtro. `Entidade` não tem campo `diretoria`.

**Análise:**
- Entidades são compartilhadas (uma concessionária pode ser fiscalizada por múltiplas diretorias)
- Adicionar FK `diretoria` no modelo exigiria **migration + decisão de dados** (qual diretoria de cada entidade existente?)
- **Recomendação:** Manter acesso global para Entidades. Bloquear apenas criação/edição por perfil (já está implementado via `get_readonly()`)

**Risco do status quo:** Baixo — dados de entidades são de referência, não operacionais por diretoria.

---

### 6. Formulário de Ação — Seleção de Instrumento (🟠 Médio)

**Estado atual:** `AcaoCreateView.get_context_data` passa `context['instrumentos'] = Instrumento.objects.all()` para o template. O dropdown inicial de seleção de instrumento mostra **todos os instrumentos**.

**Impacto da mudança:**
- Filtrar `context['instrumentos']` por diretoria do usuário logado
- Usuário de Diretoria A não verá instrumentos da Diretoria B ao criar uma ação

**Risco:** Baixo — mudança no `get_context_data`, sem impacto no modelo ou banco.

---

## Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Dados "órfãos" — instrumentos sem diretoria atribuída ficam invisíveis | 🟡 Média | Alto | Antes do deploy: `Instrumento.objects.filter(diretoria__isnull=True).count()` |
| Ações vinculadas a instrumentos sem diretoria desaparecem | 🟡 Média | Alto | Mesma verificação acima |
| Usuários logados perdem acesso a dados que criaram de outra diretoria | 🟠 Possível | Médio | Verificar se existem UPDATEs com usuário de diretoria diferente do instrumento |
| Endpoint AJAX `acoes_json` (calendário) retorna conjunto diferente | 🟢 Certa | Baixo | Apenas consistência — esperado pelo usuário |
| Performance — queries com chain longa (`obrigacao__instrumento__diretoria`) | 🟢 Baixa | Baixo | Índices já existem no modelo; adicionar `select_related` |

---

## Verificações Pré-Deploy (Obrigatórias)

Execute estes scripts no ambiente de desenvolvimento **antes** de implementar:

```python
# Verificar instrumentos sem diretoria (ficarão invisíveis após o filtro)
from instrumentos.models import Instrumento
orfaos = Instrumento.objects.filter(diretoria__isnull=True)
print(f"Instrumentos sem diretoria: {orfaos.count()}")

# Verificar ações cujo instrumento não tem diretoria
from acoes.models import Acao
acoes_sem_dir = Acao.objects.filter(obrigacao__instrumento__diretoria__isnull=True)
print(f"Ações sem diretoria no instrumento: {acoes_sem_dir.count()}")

# Verificar usuários sem diretoria (ficam sem acesso algum)
from usuarios.models import Usuario
sem_dir = Usuario.objects.filter(perfil__in=[1,2,3,4], diretoria__isnull=True)
print(f"Usuários perfil 1-4 sem diretoria: {sem_dir.count()}")
```

---

## Ordem de Implementação Recomendada (sem risco de regressão)

```
1. usuarios/mixins.py      ← Utilitário `get_diretoria_filter(user, prefix)`
2. instrumentos/views.py   ← Filtro simples (FK direto: instrumento.diretoria)
3. acoes/views.py          ← Filtro em lista + dispatch em edit/delete + acoes_json
4. acoes/forms.py          ← Filtrar context['instrumentos'] por diretoria
5. dashboards/views.py     ← Aplicar filtro nos contadores de perfis 1/2
6. indicadores/views.py    ← Apenas ValorIndicador se houver listagem
```

> [!TIP]
> Implementar e testar **uma fase por vez**. Cada fase é independente e pode ser revertida por `.bak` sem afetar as demais.

---

## Estimativa de Esforço

| Fase | Arquivo | Linhas Novas | Complexidade |
|---|---|---|---|
| 0 | `mixins.py` | ~25 | Baixa |
| 1 | `instrumentos/views.py` | ~20 | Baixa |
| 2 | `acoes/views.py` | ~30 | Média |
| 3 | `acoes/forms.py` | ~5 | Baixa |
| 4 | `dashboards/views.py` | ~15 | Média |
| 5 | `indicadores/views.py` | ~10 | Baixa |
| **Total** | **6 arquivos** | **~105 linhas** | **Média** |
