import logging
from lxml import etree

logger = logging.getLogger(__name__)

def validate_kml_file(file_input):
    """
    Valida a integridade e segurança de um arquivo KML.
    file_input: pode ser um caminho (str) ou um objeto de arquivo (UploadedFile / BytesIO).
    
    Retorna um dicionário:
    {
        'is_valid': bool,
        'error_message': str ou None,
        'total_placemarks': int,
        'valid_placemarks_count': int,
        'discarded_placemarks_count': int,
        'discarded_details': list of dicts [{'name': str, 'reason': str}]
    }
    """
    result = {
        'is_valid': True,
        'error_message': None,
        'total_placemarks': 0,
        'valid_placemarks_count': 0,
        'discarded_placemarks_count': 0,
        'discarded_details': []
    }
    
    try:
        # Se for um objeto de arquivo, garantir ponteiro no inicio
        if hasattr(file_input, 'seek'):
            file_input.seek(0)

        # Parser seguro contra XXE (XML External Entity)
        parser = etree.XMLParser(recover=True, resolve_entities=False, no_network=True)
        tree = etree.parse(file_input, parser)
        
        if hasattr(file_input, 'seek'):
            file_input.seek(0)

        root = tree.getroot()
        if root is None:
            result['is_valid'] = False
            result['error_message'] = "Não foi possível identificar a estrutura raiz do arquivo XML."
            return result

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

        placemarks = find_all(root, 'Placemark')
        result['total_placemarks'] = len(placemarks)

        # Validar aceitação de tag raiz (kml, Document, Folder ou presença de Placemarks)
        tag_name = root.tag.split('}')[-1] if '}' in root.tag else root.tag
        valid_root_tags = ['kml', 'document', 'folder']

        if tag_name.lower() not in valid_root_tags and len(placemarks) == 0:
            result['is_valid'] = False
            result['error_message'] = "O arquivo não possui uma tag raiz KML válida (<kml>, <Document> ou <Folder>)."
            return result

        if len(placemarks) == 0:
            result['is_valid'] = False
            result['error_message'] = "Nenhum elemento <Placemark> foi encontrado no arquivo KML."
            return result

        # Inspecionar cada Placemark para checagem de coordenadas válidas
        for index, pm in enumerate(placemarks, 1):
            pm_name = get_text(pm, 'name') or f"Elemento #{index}"
            
            # Buscar geometrias
            points = find_all(pm, 'Point')
            lines = find_all(pm, 'LineString')
            polys = find_all(pm, 'Polygon')
            multis = find_all(pm, 'MultiGeometry')
            
            if not (points or lines or polys or multis):
                result['discarded_placemarks_count'] += 1
                result['discarded_details'].append({
                    'name': pm_name,
                    'reason': 'Nenhuma geometria (Ponto, Linha ou Polígono) encontrada.'
                })
                continue

            # Validar coordenadas das geometrias encontradas
            has_valid_geom = False
            geom_error_reason = ""

            all_geom_nodes = points + lines + polys
            for multi in multis:
                all_geom_nodes.extend(find_all(multi, 'Point'))
                all_geom_nodes.extend(find_all(multi, 'LineString'))
                all_geom_nodes.extend(find_all(multi, 'Polygon'))

            for g_node in all_geom_nodes:
                coords_node = find(g_node, 'coordinates')
                if coords_node is None:
                    coords_node = g_node.find('.//kml:coordinates', namespaces) if ns else g_node.find('.//coordinates')

                if coords_node is None or not coords_node.text or not coords_node.text.strip():
                    geom_error_reason = "Nó de coordenadas ausente ou vazio."
                    continue

                parsed_coords = _parse_and_validate_coords(coords_node.text.strip())
                if not parsed_coords:
                    geom_error_reason = "Coordenadas com valores inválidos fora dos limites numéricos de Lat/Lon (-90 a 90, -180 a 180)."
                    continue
                else:
                    has_valid_geom = True
                    break

            if has_valid_geom:
                result['valid_placemarks_count'] += 1
            else:
                result['discarded_placemarks_count'] += 1
                result['discarded_details'].append({
                    'name': pm_name,
                    'reason': geom_error_reason or 'Coordenadas inválidas ou malformadas.'
                })

        if result['valid_placemarks_count'] == 0:
            result['is_valid'] = False
            result['error_message'] = "Todos os elementos <Placemark> no arquivo KML contêm geometrias ou coordenadas inválidas."

    except etree.XMLSyntaxError as err:
        result['is_valid'] = False
        result['error_message'] = f"Erro de sintaxe XML no KML: {str(err)}"
    except Exception as e:
        logger.error(f"Erro ao validar KML: {e}")
        result['is_valid'] = False
        result['error_message'] = f"Erro na validação do KML: {str(e)}"

    return result

def _parse_and_validate_coords(coords_text):
    """
    Parseia e valida se as coordenadas estão no formato [lon, lat] com limites numéricos válidos.
    """
    try:
        points = []
        for tuple_str in coords_text.strip().split():
            c = tuple_str.split(',')
            if len(c) >= 2:
                lon = float(c[0])
                lat = float(c[1])
                if -180.0 <= lon <= 180.0 and -90.0 <= lat <= 90.0:
                    points.append([lon, lat])
        return points if points else None
    except Exception:
        return None
