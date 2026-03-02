import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_kml(file_path):
    """
    Lê um arquivo KML e retorna uma lista de dicionários com:
    'nome', 'descricao', 'tipo_geometria', 'latitude', 'longitude', 'coordenadas', 'estilo'
    """
    elementos_encontrados = []
    
    try:
        parser = etree.XMLParser(recover=True, resolve_entities=False, no_network=True)
        tree = etree.parse(file_path, parser)
        root = tree.getroot()
        
        # Namespace handling
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

        # 1. Mapear Estilos (Dicionário id -> estilo)
        estilos_map = {}
        for style in find_all(root, 'Style'):
            s_id = style.get('id')
            if not s_id: continue
            
            estilo = {}
            # Cor de Linha (Stroke)
            line_style = find(style, 'LineStyle')
            if line_style is not None:
                color_kml = get_text(line_style, 'color') # aabbggrr
                if color_kml:
                    estilo['stroke_color'] = kml_color_to_hex(color_kml)
                    estilo['stroke_opacity'] = int(color_kml[:2], 16) / 255.0
                
                width = get_text(line_style, 'width')
                if width:
                    estilo['stroke_width'] = float(width)

            # Cor de Preenchimento (Fill)
            poly_style = find(style, 'PolyStyle')
            if poly_style is not None:
                color_kml = get_text(poly_style, 'color')
                if color_kml:
                    estilo['fill_color'] = kml_color_to_hex(color_kml)
                    estilo['fill_opacity'] = int(color_kml[:2], 16) / 255.0
                
                fill = get_text(poly_style, 'fill')
                if fill == '0': estilo['fill_opacity'] = 0

            # Cor de Ícone (Point Style)
            icon_style = find(style, 'IconStyle')
            if icon_style is not None:
                color_kml = get_text(icon_style, 'color')
                if color_kml:
                    estilo['icon_color'] = kml_color_to_hex(color_kml)
                    estilo['icon_opacity'] = int(color_kml[:2], 16) / 255.0

            if estilo:
                estilos_map[f"#{s_id}"] = estilo

        # 2. Processar Placemarks
        for pm in find_all(root, 'Placemark'):
            name = get_text(pm, 'name') or 'Sem Nome'
            desc = pm.find('.//kml:description', namespaces) if ns else pm.find('.//description')
            desc_text = desc.text.strip() if desc is not None and desc.text else ''
            
            # Extrair Estilo do Placemark
            style_url = get_text(pm, 'styleUrl')
            pm_style = estilos_map.get(style_url, {}).copy()

            # Coletar todas as geometrias do Placemark
            pm_geometries = []
            
            # Polígonos
            for poly in find_all(pm, 'Polygon'):
                ext_ring = poly.find('.//kml:outerBoundaryIs//kml:coordinates', namespaces) if ns else poly.find('.//outerBoundaryIs//coordinates')
                if ext_ring is not None and ext_ring.text:
                    pm_geometries.append(('Polygon', ext_ring.text))
            
            # Linhas
            for line in find_all(pm, 'LineString'):
                coords_node = find(line, 'coordinates')
                if coords_node is not None and coords_node.text:
                    pm_geometries.append(('LineString', coords_node.text))
            
            # Pontos
            for point in find_all(pm, 'Point'):
                coords_node = find(point, 'coordinates')
                if coords_node is not None and coords_node.text:
                    pm_geometries.append(('Point', coords_node.text))

            # Processar cada geometria encontrada
            for tipo, raw_coords in pm_geometries:
                coords_parsed = parse_kml_coordinates(raw_coords)
                if not coords_parsed: continue

                # Âncora (usar o primeiro ponto para centralizar)
                anchor_lat, anchor_lon = 0, 0
                if tipo == 'Point':
                    anchor_lon, anchor_lat = coords_parsed[0]
                    coords_final = coords_parsed[0] # [lon, lat]
                elif tipo == 'LineString':
                    anchor_lon, anchor_lat = coords_parsed[0]
                    coords_final = coords_parsed # [[lon, lat], ...]
                elif tipo == 'Polygon':
                    anchor_lon, anchor_lat = coords_parsed[0]
                    coords_final = [coords_parsed] # [[[lon, lat], ...]]

                elementos_encontrados.append({
                    'nome': name,
                    'descricao': desc_text,
                    'tipo_geometria': tipo,
                    'latitude': anchor_lat,
                    'longitude': anchor_lon,
                    'coordenadas': coords_final,
                    'estilo': pm_style
                })

    except Exception as e:
        logger.error(f"Erro ao processar KML {file_path}: {e}")
        raise ValueError(f"Erro ao processar estrutura do KML: {str(e)}")
        
    return elementos_encontrados

def kml_color_to_hex(kml_color):
    """Converte aabbggrr (KML) para #rrggbb (Hex)"""
    # KML color é aabbggrr (alpha, blue, green, red)
    if len(kml_color) == 8:
        # aabbggrr -> rrggbb
        r = kml_color[6:8]
        g = kml_color[4:6]
        b = kml_color[2:4]
        return f"#{r}{g}{b}"
    return "#3388ff"

def parse_kml_coordinates(coords_text):
    """
    Converte string de coordenadas KML em lista de tuplas [lon, lat].
    """
    try:
        points = []
        # Limpar espaços e quebras de linha
        clean_text = coords_text.strip()
        for tuple_str in clean_text.split():
            c = tuple_str.split(',')
            if len(c) >= 2:
                points.append([float(c[0]), float(c[1])])
        return points
    except:
        return None
