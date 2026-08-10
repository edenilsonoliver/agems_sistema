import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_kml(file_path):
    """
    Lê um arquivo KML e retorna um dicionário contendo:
    - 'elementos': lista de dicionários com 'nome', 'descricao', 'tipo_geometria',
                   'latitude', 'longitude', 'coordenadas', 'estilo'
    - 'descartados': lista de elementos descartados com justificativa
    """
    elementos_encontrados = []
    descartados = []

    try:
        parser = etree.XMLParser(recover=True, resolve_entities=False, no_network=True)
        tree = etree.parse(file_path, parser)
        root = tree.getroot()

        if root is None:
            return {'elementos': [], 'descartados': [{'name': 'Arquivo KML', 'reason': 'Arquivo XML/KML raiz não encontrado.'}]}

        ns = root.nsmap.get(None) if hasattr(root, 'nsmap') else None
        namespaces = {'kml': ns} if ns else None

        def find_all(element, tag):
            if ns:
                return element.findall(f'.//kml:{tag}', namespaces)
            return element.findall(f'.//{tag}')

        def find(element, tag):
            if ns:
                return element.find(f'kml:{tag}', namespaces)
            return element.find(tag)

        def get_text(element, tag):
            node = find(element, tag)
            return node.text.strip() if node is not None and node.text else None

        # 1. Mapear Estilos Básicos (<Style>)
        estilos_map = {}
        for style in find_all(root, 'Style'):
            s_id = style.get('id')
            if not s_id:
                continue

            estilo = extract_style_dict(style, find, get_text)
            if estilo:
                estilos_map[f"#{s_id}"] = estilo

        # 2. Mapear Mapeamentos de Estilos (<StyleMap>)
        for style_map in find_all(root, 'StyleMap'):
            sm_id = style_map.get('id')
            if not sm_id:
                continue

            normal_url = None
            pairs = find_all(style_map, 'Pair')
            for pair in pairs:
                key = get_text(pair, 'key')
                s_url = get_text(pair, 'styleUrl')
                if key == 'normal' and s_url:
                    normal_url = s_url
                    break
                elif s_url and not normal_url:
                    normal_url = s_url

            if normal_url and normal_url in estilos_map:
                estilos_map[f"#{sm_id}"] = estilos_map[normal_url].copy()

        # 3. Processar cada Placemark
        placemarks = find_all(root, 'Placemark')
        for index, pm in enumerate(placemarks, 1):
            name = get_text(pm, 'name') or f'Elemento #{index}'

            desc = pm.find('.//kml:description', namespaces) if ns else pm.find('.//description')
            desc_text = desc.text.strip() if desc is not None and desc.text else ''

            extended_data = extract_extended_data(pm, find_all, find, get_text)
            if extended_data and not desc_text:
                desc_text = extended_data

            style_url = get_text(pm, 'styleUrl')
            pm_style = estilos_map.get(style_url, {}).copy()

            inline_style = find(pm, 'Style')
            if inline_style is not None:
                inline_dict = extract_style_dict(inline_style, find, get_text)
                pm_style.update(inline_dict)

            pm_geometries = extract_geometries_from_pm(pm, find_all, find)

            if not pm_geometries:
                descartados.append({
                    'name': name,
                    'reason': 'Nenhuma geometria (Ponto, Linha ou Polígono) válida encontrada.'
                })
                continue

            valid_geom_count = 0
            for tipo, raw_coords in pm_geometries:
                coords_parsed = parse_kml_coordinates(raw_coords)
                if not coords_parsed:
                    continue

                valid_geom_count += 1

                anchor_lat, anchor_lon = 0, 0
                if tipo == 'Point':
                    anchor_lon, anchor_lat = coords_parsed[0]
                    coords_final = coords_parsed[0]  # [lon, lat]
                elif tipo == 'LineString':
                    anchor_lon, anchor_lat = coords_parsed[0]
                    coords_final = coords_parsed  # [[lon, lat], ...]
                elif tipo == 'Polygon':
                    anchor_lon, anchor_lat = coords_parsed[0]
                    coords_final = [coords_parsed]  # [[[lon, lat], ...]]

                elementos_encontrados.append({
                    'nome': name,
                    'descricao': desc_text,
                    'tipo_geometria': tipo,
                    'latitude': anchor_lat,
                    'longitude': anchor_lon,
                    'coordenadas': coords_final,
                    'estilo': pm_style
                })

            if valid_geom_count == 0:
                descartados.append({
                    'name': name,
                    'reason': 'Coordenadas com formato ou valores inválidos.'
                })

    except Exception as e:
        logger.error(f"Erro ao processar KML {file_path}: {e}")
        raise ValueError(f"Erro ao processar estrutura do KML: {str(e)}")

    return {
        'elementos': elementos_encontrados,
        'descartados': descartados
    }

def extract_style_dict(style_node, find_func, get_text_func):
    """Extrai dict de propriedades de estilo de um nó <Style>."""
    estilo = {}

    line_style = find_func(style_node, 'LineStyle')
    if line_style is not None:
        color_kml = get_text_func(line_style, 'color')
        if color_kml:
            estilo['stroke_color'] = kml_color_to_hex(color_kml)
            estilo['stroke_opacity'] = get_kml_color_opacity(color_kml)
        width = get_text_func(line_style, 'width')
        if width:
            try:
                estilo['stroke_width'] = float(width)
            except ValueError:
                pass

    poly_style = find_func(style_node, 'PolyStyle')
    if poly_style is not None:
        color_kml = get_text_func(poly_style, 'color')
        if color_kml:
            estilo['fill_color'] = kml_color_to_hex(color_kml)
            estilo['fill_opacity'] = get_kml_color_opacity(color_kml)
        fill = get_text_func(poly_style, 'fill')
        if fill == '0':
            estilo['fill_opacity'] = 0.0

    icon_style = find_func(style_node, 'IconStyle')
    if icon_style is not None:
        color_kml = get_text_func(icon_style, 'color')
        if color_kml:
            estilo['icon_color'] = kml_color_to_hex(color_kml)
            estilo['icon_opacity'] = get_kml_color_opacity(color_kml)
        scale = get_text_func(icon_style, 'scale')
        if scale:
            try:
                estilo['icon_scale'] = float(scale)
            except ValueError:
                pass

        icon_node = find_func(icon_style, 'Icon')
        if icon_node is not None:
            href = get_text_func(icon_node, 'href')
            if href:
                estilo['icon_href'] = href

    return estilo

def extract_extended_data(pm_node, find_all_func, find_func, get_text_func):
    """Extrai tabela simples HTML de nós <ExtendedData> / <Data>."""
    data_nodes = find_all_func(pm_node, 'Data')
    if not data_nodes:
        return ''
    
    rows = []
    for d in data_nodes:
        name = d.get('name') or ''
        val = get_text_func(d, 'value') or ''
        if name or val:
            rows.append(f"<tr><th>{name}</th><td>{val}</td></tr>")
    
    if rows:
        return f"<table class='table table-sm text-muted'>{''.join(rows)}</table>"
    return ''

def extract_geometries_from_pm(pm_node, find_all_func, find_func):
    """Extrai todas as geometrias do Placemark, inclusive MultiGeometry."""
    geometries = []

    def collect(node):
        # Polígonos
        for poly in find_all_func(node, 'Polygon'):
            coords_text = None
            coords_node = find_func(poly, 'coordinates')
            if coords_node is not None and coords_node.text:
                coords_text = coords_node.text
            else:
                for elem in poly.iter():
                    if elem.tag.endswith('coordinates') and elem.text and elem.text.strip():
                        coords_text = elem.text
                        break
            if coords_text:
                geometries.append(('Polygon', coords_text))

        # Linhas
        for line in find_all_func(node, 'LineString'):
            coords_node = find_func(line, 'coordinates')
            if coords_node is not None and coords_node.text:
                geometries.append(('LineString', coords_node.text))

        # Pontos
        for point in find_all_func(node, 'Point'):
            coords_node = find_func(point, 'coordinates')
            if coords_node is not None and coords_node.text:
                geometries.append(('Point', coords_node.text))

    collect(pm_node)

    for multi in find_all_func(pm_node, 'MultiGeometry'):
        collect(multi)

    return geometries

def kml_color_to_hex(kml_color):
    """Converte aabbggrr (KML) para #rrggbb (Hex CSS)"""
    kml_color = kml_color.strip()
    if len(kml_color) == 8:
        r = kml_color[6:8]
        g = kml_color[4:6]
        b = kml_color[2:4]
        return f"#{r}{g}{b}"
    elif len(kml_color) == 6:
        r = kml_color[4:6]
        g = kml_color[2:4]
        b = kml_color[0:2]
        return f"#{r}{g}{b}"
    return "#3388ff"

def get_kml_color_opacity(kml_color):
    """Extrai o valor de transparência alpha (0.0 a 1.0) do KML aabbggrr."""
    kml_color = kml_color.strip()
    if len(kml_color) == 8:
        alpha_hex = kml_color[:2]
        try:
            return round(int(alpha_hex, 16) / 255.0, 2)
        except ValueError:
            pass
    return 1.0

def parse_kml_coordinates(coords_text):
    """
    Converte string de coordenadas KML em lista de tuplas [lon, lat].
    Garante que valores numéricos estejam nos limites válidos de Lat/Lon.
    """
    try:
        points = []
        clean_text = coords_text.strip()
        for tuple_str in clean_text.split():
            c = tuple_str.split(',')
            if len(c) >= 2:
                lon = float(c[0])
                lat = float(c[1])
                if -180.0 <= lon <= 180.0 and -90.0 <= lat <= 90.0:
                    points.append([lon, lat])
        return points if points else None
    except Exception:
        return None
