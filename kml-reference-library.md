# Biblioteca de Referências KML - Plano de Implementação

> **Versão:** 1.0  
> **Data:** 2026-02-09  
> **Autor:** Antigravity Agent  
> **Status:** 🔴 AGUARDANDO APROVAÇÃO

---

## 📋 Overview

Implementar um novo módulo **"Biblioteca de Referências Geográficas"** que permita aos **gestores** carregar arquivos KML com pontos de referência. Esses pontos serão persistidos no banco de dados e poderão ser visualizados no mapa da aba "Mapa de Ocorrências" das Ações de Fiscalização, **coexistindo** com os marcadores de ocorrência já existentes, sem interferir na funcionalidade atual.

### Problema Resolvido
- Fiscais precisam de pontos de referência (postes, hidrômetros, limites territoriais) para orientação durante fiscalizações
- Atualmente, não há forma de carregar esses dados de referência do campo
- A mesma base de referência deve ser reutilizável em múltiplas ações

### Usuários Impactados
| Usuário | Ação |
|---------|------|
| **Gestor** | Upload de KML, gestão de camadas |
| **Fiscal** | Visualização de camadas de referência no mapa durante fiscalização |

---

## 🎯 Success Criteria

- [ ] Gestor consegue fazer upload de arquivo KML e ver pontos extraídos
- [ ] Pontos do KML são persistidos no banco de dados
- [ ] No mapa da Ação, fiscais podem toggle camadas de referência on/off
- [ ] Pontos de referência (KML) e marcadores de ocorrência (usuário) coexistem visualmente distintos
- [ ] Funcionalidade atual de adicionar pins no mapa **NÃO é afetada**
- [ ] Arquivos KML inválidos geram mensagem de erro clara
- [ ] Limite de tamanho de arquivo é respeitado (5MB)

---

## 🛠️ Tech Stack

| Componente | Tecnologia | Justificativa |
|------------|------------|---------------|
| Backend | Django 5.1.2 (existente) | Consistência com projeto |
| Parsing KML | `fastkml` + `lxml` | Biblioteca Python robusta para KML |
| Frontend Map | Leaflet.js 1.9.4 (existente) | Já implementado |
| Camadas | L.layerGroup (Leaflet) | Separação clara de referências vs. ocorrências |
| Banco | SQLite/PostgreSQL (existente) | Persistência |

### Novas Dependências

```text
# Adicionar ao requirements.txt
fastkml==1.0.1
lxml>=4.9.0
shapely>=2.0.0
```

> ⚠️ **IMPORTANTE:** `lxml` pode requerer ferramentas de build no Windows. Alternativa: usar binário pré-compilado.

---

## 📁 File Structure (Novos Arquivos)

```
agems_sistema/
├── georeferencias/                    # [NEW] App Django
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                      # CamadaReferencia, PontoReferencia
│   ├── forms.py                       # CamadaReferenciaForm
│   ├── views.py                       # CRUD + Upload KML
│   ├── urls.py                        # Rotas do módulo
│   ├── kml_parser.py                  # Parser de arquivos KML
│   ├── tests.py                       # Testes unitários
│   └── migrations/
├── templates/
│   └── georeferencias/                # [NEW] Templates
│       ├── camada_list.html           # Lista de camadas
│       └── camada_form.html           # Upload de KML
└── templates/acoes/
    └── acao_form.html                 # [MODIFY] Adicionar toggle de camadas
```

---

## 📝 Task Breakdown

### FASE 1: Fundação (Backend)

| # | Task | Agent | INPUT→OUTPUT→VERIFY |
|---|------|-------|---------------------|
| 1.1 | Criar backup de `requirements.txt` | - | `requirements.txt` → `requirements.txt.bak` → Arquivo existe |
| 1.2 | Adicionar dependências KML ao `requirements.txt` | backend | requirements.txt → novas linhas → `pip install -r requirements.txt` sem erro |
| 1.3 | Criar app Django `georeferencias` | backend | - → novo app → `python manage.py check` OK |
| 1.4 | Implementar modelos `CamadaReferencia` e `PontoReferencia` | backend | models.py → migrations → `python manage.py migrate` OK |
| 1.5 | Implementar parser KML | backend | kml_parser.py → função extrai pontos de KML válido → teste unitário passa |
| 1.6 | Implementar views CRUD + upload | backend | views.py → endpoints funcionais → testes manuais OK |
| 1.7 | Registrar app no `INSTALLED_APPS` e urls no config | backend | settings.py, urls.py → app acessível → `/georeferencias/` retorna 200 |

### FASE 2: Interface de Gestão

| # | Task | Agent | INPUT→OUTPUT→VERIFY |
|---|------|-------|---------------------|
| 2.1 | Criar template `camada_list.html` | frontend | - → lista camadas existentes → visual OK |
| 2.2 | Criar template `camada_form.html` com upload | frontend | - → form com drag-drop KML → upload funcional |
| 2.3 | Adicionar item no menu administrativo | frontend | sidebar → link "Referências Geográficas" → navegação OK |

### FASE 3: Integração no Mapa (Coexistência)

| # | Task | Agent | INPUT→OUTPUT→VERIFY |
|---|------|-------|---------------------|
| 3.1 | Criar backup de `acao_form.html` | - | arquivo → `.bak` → backup existe |
| 3.2 | Criar endpoint API para listar camadas disponíveis | backend | /georeferencias/api/camadas/ → JSON com camadas → retorno correto |
| 3.3 | Criar endpoint API para pontos de uma camada | backend | /georeferencias/api/camada/{id}/pontos/ → JSON com pontos → retorno correto |
| 3.4 | Adicionar UI de toggle de camadas no mapa | frontend | acao_form.html → checkboxes de camadas → toggles visíveis |
| 3.5 | Implementar carregamento de pontos de referência no Leaflet | frontend | JS → nova layerGroup → pontos aparecem com estilo distinto |
| 3.6 | Garantir que clique no mapa cria apenas marcador de ocorrência | frontend | clique → popup de novo marcador (não referência) → comportamento preservado |

### FASE 4: Segurança e Validação

| # | Task | Agent | INPUT→OUTPUT→VERIFY |
|---|------|-------|---------------------|
| 4.1 | Implementar validação de extensão e tamanho do arquivo | backend | upload .txt → erro → upload .kml 10MB → erro → upload .kml 2MB → OK |
| 4.2 | Implementar sanitização do conteúdo KML | backend | KML com script malicioso → rejeitado → KML válido → aceito |
| 4.3 | Restringir acesso a gestores (permissions) | backend | fiscal acessa /georeferencias/criar/ → 403 → gestor → 200 |

### FASE X: Verificação Final

| # | Check | Command/Action |
|---|-------|----------------|
| X.1 | Lint Python | `python -m py_compile georeferencias/*.py` |
| X.2 | Migrations OK | `python manage.py migrate --check` |
| X.3 | Testes passam | `python manage.py test georeferencias` |
| X.4 | Funcionalidade manual | Ver seção "Verificação Manual" abaixo |
| X.5 | Backup pode restaurar | Comparar `.bak` com original se necessário |

---

## ✅ Plano de Verificação

### Testes Automatizados (Novos)

Criar em `georeferencias/tests.py`:

```python
# Testes a implementar:
# 1. TestKMLParser: Parsing de KML válido retorna pontos
# 2. TestKMLParser: KML inválido levanta exceção
# 3. TestCamadaReferenciaModel: Criação de camada com pontos
# 4. TestCamadaReferenciaView: Upload requer autenticação e permissão
# 5. TestCamadaReferenciaView: Upload de KML válido cria pontos
# 6. TestAPIEndpoints: Listagem de camadas retorna JSON correto
```

**Comando:** `python manage.py test georeferencias -v 2`

### Verificação Manual (Passo a Passo)

> **Pré-requisito:** Servidor rodando com `python manage.py runserver`

#### Teste 1: Upload de KML pelo Gestor
1. Fazer login como **gestor** (ou superuser)
2. Navegar para `/georeferencias/`
3. Clicar em "Nova Camada de Referência"
4. Preencher nome: "Postes Zona Sul"
5. Selecionar um arquivo KML válido (< 5MB)
6. Clicar em "Salvar"
7. **Esperado:** Mensagem de sucesso, camada aparece na lista com contagem de pontos

#### Teste 2: Rejeição de Arquivo Inválido
1. Repetir passos 1-4 acima
2. Selecionar um arquivo `.txt` ou `.pdf`
3. Clicar em "Salvar"
4. **Esperado:** Mensagem de erro "Formato de arquivo inválido"

#### Teste 3: Visualização no Mapa da Ação
1. Navegar para `/acoes/{id}/editar/` (ação de fiscalização existente)
2. Ir para aba "Mapa"
3. Verificar presença de dropdown/checkboxes "Camadas de Referência"
4. Marcar a camada "Postes Zona Sul"
5. **Esperado:** Pontos de referência aparecem no mapa com **ícone/cor diferente** dos marcadores de ocorrência

#### Teste 4: Coexistência de Funcionalidades
1. No mesmo mapa do Teste 3
2. Clicar em um ponto **vazio** do mapa (não em um ponto de referência)
3. **Esperado:** Popup de "Registrar Ponto" aparece (funcionalidade original preservada)
4. Adicionar um marcador de ocorrência
5. **Esperado:** Novo marcador aparece com estilo de ocorrência, distinto das referências

#### Teste 5: Permissões (Segurança)
1. Fazer login como **fiscal** (usuário sem permissão de gestão)
2. Tentar acessar `/georeferencias/criar/`
3. **Esperado:** Redirecionamento para login ou página 403 Forbidden

---

## 🔐 Considerações de Segurança (Global Rules)

| Regra | Implementação |
|-------|---------------|
| Backup antes de modificar | `.bak` criado para cada arquivo modificado |
| Validação de input | Extensão, MIME type, tamanho, conteúdo KML |
| Sem hardcode de secrets | N/A (não requer credenciais) |
| Autorização verificada | `@permission_required('georeferencias.add_camadareferencia')` |
| Não expor stack traces | Try/except com mensagens genéricas para usuário |

---

## 📊 Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────────┐
│                          GESTOR                                     │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │ /georeferencias/ → Upload KML → Parser → Salva no DB        │   │
│   └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       BANCO DE DADOS                                │
│   ┌─────────────────────┐   ┌─────────────────────────────────────┐ │
│   │ CamadaReferencia    │   │ PontoReferencia                     │ │
│   │ ├─ id               │   │ ├─ id                               │ │
│   │ ├─ nome             │◄──│ ├─ camada_id (FK)                   │ │
│   │ ├─ arquivo_kml      │   │ ├─ nome                             │ │
│   │ ├─ cor_marcador     │   │ ├─ latitude                         │ │
│   │ └─ ativo            │   │ └─ longitude                        │ │
│   └─────────────────────┘   └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          FISCAL                                     │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │ /acoes/{id}/editar/ → Mapa → Toggle Camadas                 │   │
│   │                                                             │   │
│   │   referenciasLayer (KML) ←──┐                               │   │
│   │   marcadoresLayer (Pins) ←──┼── Coexistem no mesmo mapa     │   │
│   │                             │                               │   │
│   │   [Toggle Camadas] ─────────┘                               │   │
│   └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ⏱️ Estimativa de Esforço

| Fase | Tarefas | Estimativa |
|------|---------|------------|
| Fase 1 | 7 | ~2-3 horas |
| Fase 2 | 3 | ~1-2 horas |
| Fase 3 | 6 | ~2-3 horas |
| Fase 4 | 3 | ~1 hora |
| Fase X | 5 | ~30 min |
| **Total** | **24** | **~7-9 horas** |

---

## 🗒️ Notas Importantes

1. **KMZ não suportado inicialmente:** Arquivos KMZ (KML compactado) requerem descompactação. Pode ser adicionado em versão futura.

2. **Limite de pontos por camada:** Considerar limite de ~5000 pontos por camada para evitar sobrecarga no frontend.

3. **Estilo visual distinto:** Usar ícones/cores completamente diferentes para referências (ex: azul/círculo) vs. ocorrências (ex: vermelho/marcador).

4. **Fallback para `omnivore`:** Se `fastkml` apresentar problemas no Windows, alternativa é processar KML no frontend com `leaflet-omnivore`.

---

## ✅ Checklist de Aprovação

- [ ] Revisei e concordo com a arquitetura proposta
- [ ] O escopo das tarefas está adequado
- [ ] As estimativas são realistas
- [ ] Os critérios de verificação são claros
- [ ] Posso fornecer arquivo KML de teste para validação

**Próximos Passos após Aprovação:**
1. Criar branch `feature/kml-reference-library`
2. Executar Fase 1 (Backend Foundation)
3. Verificar a cada fase
