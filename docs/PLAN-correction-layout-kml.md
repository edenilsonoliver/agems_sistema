# Correction Plan: Layout & KML Module

## Overview
Address critical UI/UX regressions in the "Edit Action" map tab and resolve reported errors in the new KML Reference module.

## Problems Identified
1.  **Layout Broken in `acao_form.html`**:
    -   Map container is "cut in half".
    -   Elements are disorganized (messy).
    -   Likely cause: Unclosed or incorrectly nested `<div>` tags (Map inside `.alert`).
2.  **Error in "Mapas/Referências"**:
    -   User reported error in the module.
    -   Likely causes: Template syntax errors, URL configuration, or Permission checks.

## Task Breakdown

### Phase 1: Fix Map Layout (Action Form)
- [ ] **Restructure HTML**: Move `#mapa-fiscalizacao` OUT of `.alert`.
- [ ] **Fix Grid System**: Use `row` and `col` to organize the "Layers Card" and "Map".
- [ ] **Styling**: Ensure Map has defined height (e.g., `min-height: 500px`).

### Phase 2: Debug & Fix KML Module
- [ ] **Inspect Templates**: Check `camada_list.html` and `camada_form.html` for syntax errors.
- [ ] **Inspect Views**: Verify `views.py` imports and context data.
- [ ] **Verify Navigation**: Check `base_modern.html` link generation.

### Phase 3: Verification
- [ ] **Visual Check**: Render Layout (Manual).
- [ ] **Functional Check**: Access `/georeferencias/` without error.
