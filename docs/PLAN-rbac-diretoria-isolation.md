# PLAN: RBAC Isolamento por Diretoria e Subunidade

## Contexto

O sistema AGEMS possui 6 perfis de acesso (0=Admin, 1=Diretor, 2=Assessor, 3=Coordenador, 4=Executor, 5=Visualizador), ligados a uma **Diretoria** e, nos perfis 2-4, também a uma **Subunidade**.

**Problema:** Usuário logado como Diretor da Diretoria A consegue ver/editar registros da Diretoria B. O `FiltrarPorDiretoriaMixin` existe em `usuarios/mixins.py` mas **não está aplicado em nenhuma view de negócio**.

---

## Auditoria do Estado Atual

| Módulo | Filtro Lista | Filtro Detail/Edit | Isolamento no Objeto |
|---|---|---|---|
| **Instrumentos** | ❌ Sem filtro | ❌ Sem filtro | Modelo tem FK `diretoria` |
| **Obrigações** | ❌ (herda instrumento) | ❌ | Acesso via `instrumento__diretoria` |
| **Ações** | ⚠️ Só perfis 3/4 filtram | ❌ Sem filtro | Acesso via `obrigacao__instrumento__diretoria` |
| **Entidades** | ❌ Sem filtro | ❌ Sem filtro | Sem campo diretoria (acesso global) |
| **Indicadores** | ❌ Sem filtro | ❌ Sem filtro | Acesso via `contrato__diretoria` |
| **Usuários** | ✅ OK (lista) | ✅ OK | `diretoria` direto no modelo |
| **Dashboard** | ⚠️ Parcial | N/A | Depende de cada widget |

### Cadeia de isolamento por modelo

```
Instrumento.diretoria  ──────────────────────────────►  Diretoria
Obrigacao.instrumento.diretoria  ──────────────────────►  Diretoria
Acao.obrigacao.instrumento.diretoria  ─────────────────►  Diretoria
ValorIndicador.contrato.diretoria  ────────────────────►  Diretoria
IndicadorContratual  (sem FK diretoria — acesso global atualmente)
Entidade  (sem FK diretoria — acesso global por design)
```

---

## Regras de Negócio

| Perfil | Acesso |
|---|---|
| 0 — Admin | Tudo sem restrição |
| 1 — Diretor | Apenas objetos da **sua Diretoria** |
| 2 — Assessor | Apenas objetos da sua **Subunidade** (ou toda a Diretoria se sem subunidade) |
| 3 — Coordenador | Apenas objetos da sua **Subunidade** |
| 4 — Executor | Apenas ações onde é **responsável ou executor** (dentro da subunidade) |
| 5 — Visualizador | Ações/instrumentos das **Diretorias autorizadas** conforme `diretorias_visualizacao` |

> **Entidades e Indicadores:** Entidade não tem FK diretoria (é compartilhada). `IndicadorContratual` também não — acesso global mantido (apenas `ValorIndicador` pode ser filtrado por instrumento).

---

## Plano de Implementação

### Fase 0 — Reforçar o `FiltrarPorDiretoriaMixin`

**Arquivo:** `usuarios/mixins.py`

Atualizar `FiltrarPorDiretoriaMixin` para suportar novos padrões de lookup:
- `diretoria` (direto)
- `instrumento__diretoria` (obrigações)
- `obrigacao__instrumento__diretoria` (ações)
- `contrato__diretoria` (indicadores)

Adicionar também `get_diretoria_filter(user)` — função utilitária que retorna o Q-filter correto baseado no perfil, reutilizável em todos os módulos.

---

### Fase 1 — Módulo Instrumentos

**Arquivo:** `instrumentos/views.py`

#### `InstrumentoListView.get_queryset`
- Perfil 0: sem filtro
- Perfis 1-4: filtrar por `diretoria=user.diretoria` (ou `diretoria=user.subunidade.diretoria`)
- Perfil 5: filtrar por `diretoria__in=user.diretorias_visualizacao.all()`

#### `InstrumentoUpdateView.dispatch` e `InstrumentoDeleteView.dispatch`
- Verificar se `instrumento.diretoria` pertence à diretoria do usuário logado
- Se não → `messages.error` + `redirect('instrumento_list')`

#### `InstrumentoCreateView.form_valid`
- Para perfis 1-4, forçar `diretoria = user.diretoria` antes de salvar (evitar POST manipulado)

---

### Fase 2 — Módulo Ações

**Arquivo:** `acoes/views.py`

#### `AcaoListView.get_queryset`
- Perfil 0: sem filtro
- Perfil 1: `obrigacao__instrumento__diretoria=user.diretoria`
- Perfis 2, 3: `obrigacao__instrumento__diretoria=user.diretoria` (ou subunidade)
- Perfil 4: ações onde é `responsavel=user` OR `executores=user` **dentro da diretoria**
- Perfil 5: `obrigacao__instrumento__diretoria__in=user.diretorias_visualizacao.all()`

#### `AcaoUpdateView.dispatch` e `AcaoDeleteView.dispatch`
- Verificar se `acao.obrigacao.instrumento.diretoria` é compatível com o usuário
- Se não: redirecionar com erro

#### `acoes_json` (endpoint calendário)
- Aplicar o mesmo filtro que `AcaoListView.get_queryset`

#### `get_context_data` dos forms de criação/edição
- `context['instrumentos']` deve ser filtrado por diretoria (não `Instrumento.objects.all()`)

---

### Fase 3 — Módulo Indicadores

**Arquivo:** `indicadores/views.py`

#### `ValorIndicador` já tem FK para `Instrumento` (contrato)
- `IndicadorListView`: `IndicadorContratual` não tem FK diretoria — manter acesso global (**apenas visualização**)
- `ValorIndicadorListView` (se existir): filtrar por `contrato__diretoria`

**Decisão de design:** Como `IndicadorContratual` é uma definição de indicador sem vínculo de diretoria, ele permanece global para leitura. Apenas os *valores* são filtrados por instrumento/diretoria.

---

### Fase 4 — Dashboard

**Arquivo:** `dashboards/views.py`

- Counts e widgets que mostram total de ações, instrumentos, etc. devem respeitar o filtro de diretoria
- Adaptar `queryset` de cada widget para usar a lógica de isolamento

---

### Fase 5 — Formulários (Seleção de objetos relacionados)

**Arquivos:** `acoes/forms.py`, `instrumentos/forms.py`

Em forms que têm campos de FK (ex: Instrumento ao criar Ação), filtrar os querysets:
- `instrumento` no formulário de ação: mostrar apenas instrumentos da diretoria do usuário
- Isso **já existe** parcialmente para usuários responsáveis/executores — generalizar o padrão

---

## Estratégia de Implementação (não-disruptiva)

> [!IMPORTANT]
> A implementação será **aditiva**: adicionar `dispatch()` nas views de edição/deleção para verificar ownership. Não reescrever lógica existente, apenas sobrepor filtros.

**Ordem recomendada:**
1. Criar função utilitária `get_diretoria_queryset_filter(user, lookup_prefix='')` no `usuarios/mixins.py`
2. Aplicar em `InstrumentoListView` (mais simples — FK direto)
3. Aplicar em `AcaoListView` (cadeia mais longa)
4. Aplicar `dispatch()` em todas as Update/Delete views
5. Dashboard
6. Forms (querysets filtrados)

---

## Arquivos a Modificar

| Arquivo | Tipo de Mudança |
|---|---|
| `usuarios/mixins.py` | Reforçar `FiltrarPorDiretoriaMixin` + utilitário |
| `instrumentos/views.py` | Filtros em List, dispatch em Update/Delete, force diretoria em Create |
| `acoes/views.py` | Filtros em List/acoes_json, dispatch em Update/Delete, filtro de instrumentos no form |
| `acoes/forms.py` | Filtrar queryset de `instrumento` por diretoria do usuário |
| `indicadores/views.py` | Filtrar ValorIndicador por diretoria via instrumento |
| `dashboards/views.py` | Aplicar filtros de diretoria nos contadores/widgets |

---

## Análise de Risco

### Probabilidade de quebrar algo: Média (controlável)

| Risco | Prob. | Impacto | Origem |
|---|---|---|---|
| Instrumentos/Ações sem diretoria ficam invisíveis | 🟡 Média | Alto | Dados históricos sem diretoria preenchida |
| Usuário perfil 1-4 sem `diretoria` preenchida vê tudo vazio | 🟠 Baixa | Alto | Cadastro incompleto de usuário |
| Ação de edição vinculada a instrumento de outra diretoria | 🟢 Baixa | Médio | Dado legado inconsistente |
| Dashboard mostra números menores para Diretor | 🟢 Certa | Baixo | Comportamento **esperado e correto** |
| Performance (joins mais longos) | 🟢 Baixa | Baixo | Índices FK já existem nos modelos |

### O que NÃO vai quebrar de jeito nenhum

- **Autenticação e login** — não tocamos nisso
- **`AcaoForm` (responsável/executor)** — já filtrado por diretoria, não mexemos ✅
- **Formulários de criação** — lógica não muda, só queryset fica menor
- **Salvamento de dados** — zero mudanças de model ou migration
- **Exclusão de dados** — apenas adicionamos verificação *antes* de permitir

---

## 🔴 Protocolo de Segurança Obrigatório (sejaparanoico)

### PASSO 1 — Verificar dados antes de qualquer código

> [!CAUTION]
> Este passo é obrigatório. Se qualquer contador retornar > 0, corrigir os dados **antes** de implementar os filtros.

```powershell
.\venv\Scripts\python.exe manage.py shell -c "
from instrumentos.models import Instrumento
from acoes.models import Acao
from usuarios.models import Usuario

orfaos_inst = Instrumento.objects.filter(diretoria__isnull=True).count()
orfaos_acoes = Acao.objects.filter(obrigacao__instrumento__diretoria__isnull=True).count()
sem_dir = Usuario.objects.filter(perfil__in=[1,2,3,4], diretoria__isnull=True).count()

print(f'Instrumentos sem diretoria: {orfaos_inst}')
print(f'Acoes sem diretoria no instrumento: {orfaos_acoes}')
print(f'Usuarios perfil 1-4 sem diretoria: {sem_dir}')

if orfaos_inst == 0 and orfaos_acoes == 0 and sem_dir == 0:
    print('OK — dados limpos, seguro para implementar')
else:
    print('ATENCAO — corrija os dados antes de implementar os filtros')
"
```

### PASSO 2 — Criar backups antes de cada arquivo modificado

```powershell
# Antes de cada fase, criar .bak do arquivo alvo
Copy-Item "usuarios\mixins.py" "usuarios\mixins.py.bak" -Force
Copy-Item "instrumentos\views.py" "instrumentos\views.py.bak" -Force
Copy-Item "acoes\views.py" "acoes\views.py.bak" -Force
Copy-Item "acoes\forms.py" "acoes\forms.py.bak" -Force
Copy-Item "dashboards\views.py" "dashboards\views.py.bak" -Force
```

### PASSO 3 — Implementar e testar por fase (não tudo de uma vez)

```
Fase 0 (mixins.py) → manage.py check → OK?
Fase 1 (instrumentos) → testar login Diretoria A e B → OK?
Fase 2 (acoes) → testar lista + calendário + edição → OK?
Fase 3 (forms) → criar ação e verificar instrumentos filtrados → OK?
Fase 4 (dashboard) → verificar contadores → OK?
```

Se qualquer fase quebrar → restaurar `.bak` da fase afetada e investigar antes de continuar.

### PASSO 4 — Testar com usuário real de cada perfil

Após cada fase, logar com um usuário de cada perfil e verificar:
1. Login como **Admin (0)** → deve ver tudo (sem mudança)
2. Login como **Diretor (1)** → ver apenas sua diretoria
3. Login como **Assessor (2)** → ver apenas sua subunidade
4. Login como **Executor (4)** → ver apenas ações onde é responsável/executor
5. Login como **Visualizador (5)** → ver apenas diretorias autorizadas

---

## Verificação Final

### Testes Automatizados
```powershell
.\venv\Scripts\python.exe manage.py test usuarios instrumentos acoes --verbosity=2
```

### Django Check (após cada fase)
```powershell
.\venv\Scripts\python.exe manage.py check
```

### Cenários Manuais de Validação
1. **Diretor A** → listar instrumentos → apenas da Diretoria A ✓
2. URL direta `/instrumentos/<pk_B>/editar/` (Diretoria B) → redireciona com erro ✓
3. **Assessor Subunidade X** → criar ação → form mostra só instrumentos da Diretoria A ✓
4. **Executor** → listar ações → só onde é responsável ou executor ✓
5. **Visualizador** → ver só registros das diretorias autorizadas ✓
6. **Admin** → ver tudo sem restrição (regressão) ✓
