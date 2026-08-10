# System Design & UI Guidelines - AGEMS Sistema

Este documento define os padrões visuais, estruturais e de interface do usuário (UI) para o sistema AGEMS. Ele deve ser utilizado como **regra global (Global Rule)** para qualquer agente, IA ou desenvolvedor que for criar novas telas, componentes ou modificar o layout existente, garantindo consistência em toda a aplicação.

---

## 1. Stack Base de Frontend
- **Framework CSS:** Bootstrap 5 (utilizar classes nativas sempre que possível).
- **Ícones:** Bootstrap Icons (prioritário) e Font Awesome (secundário).
- **Tipografia:** 'Inter', sans-serif (via Google Fonts).

---

## 2. Paleta de Cores (Design Tokens)

As cores base do sistema estão definidas como variáveis CSS na raiz (`:root`) do arquivo `base_modern.html`. Sempre utilize as variáveis CSS nativas ou as classes equivalentes.

| Propriedade / Classe | Cor Hex | Uso Principal |
| :--- | :--- | :--- |
| `--primary-color` | `#0066B3` | Ações principais, links, destaques. |
| `--secondary-color` | `#6c757d` | Textos secundários, bordas discretas. |
| `--success-color` | `#198754` | Mensagens de sucesso, status positivo, botões de salvar. |
| `--danger-color` | `#dc3545` | Erros, status crítico, botões de exclusão. |
| `--warning-color` | `#ffc107` | Alertas, status de atenção. |
| `--info-color` | `#0dcaf0` | Informações, badges neutros. |
| `--gold-color` | `#FFC300` | Destaques específicos (ex: `.bg-gold`). |
| `--dark-color` | `#212529` | Textos fortes, fundos escuros. |
| `--light-color` | `#f8f9fa` | Fundos de painéis, cabeçalhos de tabela. |

### Fundos Específicos
- **Body Background:** `#f5f7fa`
- **Gradiente Padrão AGEMS (Sidebar, Header Brand, Botões Primários):** `linear-gradient(135deg, #0066B3 0%, #004A8F 100%)`

---

## 3. Tipografia e Layout Base

- **Fonte Padrão:** `'Inter', sans-serif`.
- **Cor de Texto Base:** `#333` (com `#1a1a1a` para títulos).
- **Sidebar (Menu Lateral):** 
  - Largura: `260px` (`--sidebar-width`).
  - Fundo: Gradiente Padrão AGEMS.
  - Links: Brancos translúcidos (`rgba(255, 255, 255, 0.8)`), ficam opacos no `.active` e no `:hover`.
- **Header (Barra Superior):**
  - Altura: `70px` (`--header-height`).
  - Fundo: Branco com sombra sutil (`box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05)`).

---

## 4. Componentes UI Padrão

Sempre que criar um novo componente (Cards, Tabelas, Botões), siga as estruturas pré-definidas no CSS do projeto.

### 4.1. Tabelas Modernas (`.modern-table`)
Qualquer tabela de listagem de dados deve utilizar a classe `.modern-table` para aplicar bordas arredondadas e efeito de hover.
```html
<table class="table modern-table">
    <thead>
        <tr>
            <th>Coluna 1</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Dado 1</td>
        </tr>
    </tbody>
</table>
```
- **Thead:** Fundo `#f8f9fa`, texto `#495057`, fonte em peso 600.
- **Tbody Tr Hover:** Fundo `#f8f9fa`.

### 4.2. Cards de Estatística / Resumo (`.stat-card`)
Usados em Dashboards ou cabeçalhos de resumos. Têm efeito de elevação no hover.
```html
<div class="stat-card fade-in">
    <div class="stat-icon primary">
        <i class="bi bi-graph-up"></i>
    </div>
    <div class="stat-value">123</div>
    <div class="stat-label">Total de Registros</div>
</div>
```
- A classe `.stat-icon` pode ter modificadores como `.primary`, `.success`, `.warning`, `.danger`.

### 4.3. Botões
Os botões primários têm design com gradiente e elevação (efeito "lift") no hover.
- Use `.btn .btn-primary` nativo do projeto (já estilizado).
- **Efeito Hover Primário:** `transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);`

### 4.4. Formulários e Inputs
- Utilizar o padrão do Bootstrap 5 / Django Crispy Forms.
- **Inputs de Arquivo Customizados:** O sistema já customiza o `input[type="file"]::file-selector-button` (cor `#f8f9fa` e bordas arredondadas). Não crie customizações adicionais conflitantes.
- **Preview de Imagem:** Utiliza-se `.clearablefileinput` (Django) que exibe miniaturas padronizadas (`max-width: 150px`, `border-radius: 8px`).

### 4.5. Badges de Status
Ao exibir status (Ativo, Inativo, Concluído, etc), utilize badges arredondados (`.rounded-pill` no Bootstrap 5).
```html
<span class="badge bg-success rounded-pill">Ativo</span>
```
- Existe um badge dourado customizado `.bg-gold`.

---

## 5. Padrões de Animação e Interação

- **Fade-In:** Elementos que carregam dinamicamente na tela (como cards e tabelas) devem utilizar a classe `.fade-in` (`animation: fadeIn 0.5s ease`).
- **Transições:** Hover em botões e cards usam `transition: all 0.3s ease`.
- **Alertas Django:** São renderizados no topo, auto-descartados (`.alert-dismissible`) por JS após 5 segundos, e os de erro (`alert-danger`) têm uma borda esquerda em destaque (`border-left: 6px solid #b02a37`).

---

## 6. Regras de Ouro (Golden Rules para a IA)

1. **NUNCA injete CSS inline** (`style="..."`) para tentar forçar cores, a menos que seja um cálculo dinâmico (como larguras de barra de progresso). Use classes de utilitários do Bootstrap (ex: `text-primary`, `bg-light`, `mt-3`, `d-flex`).
2. **NUNCA use TailwindCSS**. O framework do projeto é Bootstrap 5 Vanilla.
3. **Mantenha a responsividade:** Utilize o sistema de grids (`row`, `col-md-6`, `col-lg-4`) nativo do Bootstrap.
4. Ao adicionar novos ícones, dê prioridade aos **Bootstrap Icons** (`<i class="bi bi-nome-do-icone"></i>`).
5. **Não recrie a roda:** Se precisar de um modal, aba, ou dropdown, use os componentes JavaScript nativos do Bootstrap 5.
6. Qualquer nova página que necessite de layout padrão com Sidebar e Header deve obrigatoriamente estender `{% extends "base_modern.html" %}` e alocar o HTML dentro da tag `{% block content %}`.
