# Correction Plan: Map Tab Placement

## Problem Analysis
The user reports the Map and Reference Layers appearing in the "Documentos/Evidências" tab.
**Cause:** In the previous layout fix, the `#mapa-content` tab pane (`<div class="tab-pane ...">`) was inadvertently closed **immediately and prematurely** after the info alert.
**Result:** The Map, Layer Control, and Pin List are currently residing **outside** of any specific tab pane. This makes them visible continuously or renders them partly mixed with other tabs, breaking the tab switching logic.

## Goal
Move all Map-related components BACK inside the `#mapa-content` container so they only appear when the "Mapa de Ocorrências" tab is active.

## Required Changes

### [MODIFY] `templates/acoes/acao_form.html`

1.  **Locate the Premature Close**:
    -   Find the `</div>` that currently closes `#mapa-content` right after the `.alert-info`.
    -   **Action**: Remove this specific closing tag.

2.  **Enclose Content**:
    -   Ensure the following blocks are nested *inside* `#mapa-content`:
        -   `<!-- Controle de Camadas -->`
        -   `<!-- Container do Mapa -->`
        -   `<!-- LISTA DE PINS ABAIXO DO MAPA -->`
        -   The helper text (`Coordenadas capturadas...`).

3.  **Verify Closure**:
    -   Ensure the `#mapa-content` div is closed **only after** all the above elements, just before the `<hr class="my-4">`.

## Verification Plan
1.  **Code Review**: Check HTML indentation and nesting of `mapa-content`.
2.  **Visual Check**: Confirm Map is **HIDDEN** when "Documentos" tab is active.
3.  **Visual Check**: Confirm Map is **VISIBLE** when "Mapa de Ocorrências" tab is active.
