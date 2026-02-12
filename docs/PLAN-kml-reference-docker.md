# KML Reference Library - Docker Implementation Plan

## Overview
Implement a system to upload, persist, and display KML reference layers on the Fiscalization Map, executing all operations strictly within the project's Docker environment.

## Goal
Enable managers to visualize geographic references (e.g., pipelines, protected areas) alongside inspection markers without mixing data.

## Environment & Constraints
-   **Platform:** Docker (Linux container)
-   **Service Name:** `web` (from `docker-compose.yml`)
-   **State:** Code files are mounted from host to container (`volumes: .:/app`).
-   **Command Execution:** STRICTLY via `docker compose exec -T web ...`
-   **Python Environment:** System python inside container (no venv activation needed inside, but packages must be installed).

## Success Criteria
1.  `fastkml`, `lxml`, `shapely` installed in running container.
2.  Database migrations applied successfully without data loss.
3.  Admin can upload a valid KML file.
4.  Map displays KML points when layer is toggled.
5.  No regression in existing map functionality.

## Task Breakdown

### Phase 1: Environment Verification & Setup
- [ ] **Verify Container**: Check if `web` service is up.
- [ ] **Install Dependencies**: `pip install` inside container logic (runtime fix).
- [ ] **Validate Imports**: Run a one-liner python script inside docker to confirm libraries are loadable.

### Phase 2: Database Migration
- [ ] **Make Migrations**: `makemigrations georeferencias` inside docker.
- [ ] **Apply Migrations**: `migrate` inside docker.
- [ ] **Verify Tables**: Check `georeferencias_camadareferencia` table exists.

### Phase 3: Code Implementation (Review)
- [ ] **Models**: `georeferencias/models.py` (Created)
- [ ] **Views**: `georeferencias/views.py` (Created)
- [ ] **URLs**: `georeferencias/urls.py` & `config/urls.py` (Created/Updated)
- [ ] **Templates**: `camada_list.html`, `camada_form.html` (Created)
- [ ] **Map Integration**: `templates/acoes/acao_form.html` (Updated)

### Phase 4: Verification & Testing
- [ ] **Test Parser**: Run `python manage.py test georeferencias` inside docker.
- [ ] **Manual Test**: Upload `test_data/exemplo.kml` via UI.
- [ ] **Map Verification**: Open an action, toggle layer, check points.

## Rollback Strategy
1.  **Dependency Failure**: Revert `requirements.txt`.
2.  **Migration Failure**: `migrate georeferencias zero`.
3.  **Code Failure**: Restore `.bak` files.

## Verification Checklist (Phase X)
- [ ] Dependencies installed in Docker
- [ ] Migrations applied
- [ ] Tests passed (`manage.py test`)
- [ ] UI functioning (Upload & Map)
