# Plan: KML Support for Lines and Polygons

Implement support for non-point geometries (Lines and Polygons) in the Georeferencing module, including style extraction and interactive tooltips.

## 1. Context & Research

- **Current State**: The system only extracts `Point` geometries via `lxml`.
- **User Requirement**: Support `LineString` and `Polygon`, showing names on mouseover, and extracting styles (colors) from KML.
- **Environment**: Using SQLite (`db.sqlite3`) for development and PostgreSQL for production.
- **Persistence Decision**: We will use **`JSONField`**. 
    - **Persistence**: It is 100% persistent in both databases. In PostgreSQL, it is stored as `jsonb` (highly optimized).
    - **Compatibility**: It works on SQLite (dev) and PostgreSQL (prod) without requiring complex spatial system libraries (SpatiaLite/GDAL/PostGIS) to be installed on the Operating System. This avoids "environment hell" while providing all the flexibility needed for rendering.

## 2. Proposed Implementation Phases

### Phase 1: Database Evolution
- **Modify `georeferencias/models.py`**:
    - Rename `PontoReferencia` to `GeometriaReferencia` (or create as new).
    - Add `tipo_geometria` (`Point`, `LineString`, `Polygon`).
    - Add `coordenadas` (`JSONField`) to store lists of points.
    - Add `estilo` (`JSONField`) to store `stroke-color`, `stroke-width`, `fill-color`, etc.
    - Keep `latitude`/`longitude` as the "anchor" point for map centering and legacy support.

### Phase 2: KML Parser Enhancement
- **Modify `georeferencias/kml_parser.py`**:
    - Expand detection to include `LineString` and `Polygon`.
    - Extract coordinates as arrays:
        - `LineString`: `[[lon, lat], [lon, lat], ...]`
        - `Polygon`: `[[[lon, lat], ...]]` (handling exterior ring).
    - Implement style parsing:
        - Search for `<Style>` tags linked to Placemarks via `<styleUrl>`.
        - Parse `<LineStyle>` (color/width) and `<PolyStyle>` (color).

### Phase 3: API & View Updates
- **Modify `georeferencias/views.py`**:
    - Update the creation logic to handle the new geometry types during KML import.
    - Update API endpoints (`api_get_pontos_camada`) to return the full geometry data and styles.

### Phase 4: Frontend Map Rendering
- **Modify Leaflet logic (templates/scripts)**:
    - Add logic to check `tipo_geometria`.
    - Use `L.polyline()` and `L.polygon()` for rendering.
    - Apply styles extracted from the database.
    - **Interactivity**: Add `.bindTooltip()` with the name and description, configured to show on `mouseover`.

## 3. Verification Plan

### Automated Tests
- Create a test script `test_kml_geometries.py` to parse a sample KML with lines and polygons and verify the returned dictionary structure.
- Run `python manage.py check` for model definition validity.

### Manual Verification
- Upload a KML containing points, lines, and polygons.
- Verify if all elements appear on the map with the correct colors.
- Hover over elements to ensure Tooltips appear with names.
