import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_kml(file_path):
    """
    Lê um arquivo KML e retorna uma lista de dicionários com 'nome', 'descricao', 'latitude', 'longitude'.
    Utiliza lxml para maior robustez e independência de versão do fastkml.
    Extrai apenas geometrias do tipo POINT.
    """
    pontos_encontrados = []
    
    try:
        # Parse XML (Security Hardened)
        # recover=True: tenta ignorar erros de sintaxe leves
        # resolve_entities=False: PREVINE XXE (XML External Entity attacks)
        # no_network=True: PREVINE acesso a rede externa durante parse
        parser = etree.XMLParser(recover=True, resolve_entities=False, no_network=True)
        tree = etree.parse(file_path, parser)
        root = tree.getroot()
        
        # Handle Namespace
        # O namespace padrão (None) geralmente é o do KML.
        # Se houver, lxml coloca no nsmap com chave None (ou outra se especificado).
        ns = root.nsmap.get(None) if hasattr(root, 'nsmap') else None
        
        # Mapa de namespaces para find/findall
        namespaces = {'kml': ns} if ns else None

        # Função auxiliar para buscar com ou sem namespace
        def find_all(element, tag):
            if ns:
                return element.findall(f'.//kml:{tag}', namespaces)
            return element.findall(f'.//{tag}')

        def find(element, tag):
            if ns:
                return element.find(f'kml:{tag}', namespaces)
            return element.find(tag)
        
        def get_text(element, tag):
            # Procura filho direto
            # find procura direto se for ./tag ou kml:tag
            # Se a estrutura for complexa, adjust. Mas Placemark -> name é padrão.
            if ns:
                node = element.find(f'kml:{tag}', namespaces)
            else:
                node = element.find(tag)
            return node.text if node is not None else None

        # Encontrar todos os Placemarks (profundidade qualquer)
        placemarks = find_all(root, 'Placemark')
        
        logger.info(f"Encontrados {len(placemarks)} Placemarks no KML.")

        for pm in placemarks:
            # Extrair Nome e Descrição
            name = get_text(pm, 'name') or 'Sem Nome'
            desc = get_text(pm, 'description') or ''
            
            # Verificar se tem Point
            point = find(pm, 'Point')
            if point is not None:
                # Extrair coordinates
                coords_node = find(point, 'coordinates')
                if coords_node is not None and coords_node.text:
                    coords_text = coords_node.text.strip()
                    # Formato: lon,lat,alt (espaço separando tuplas se for LineString, mas Point é um so)
                    parts = coords_text.split(',')
                    if len(parts) >= 2:
                        try:
                            lon = float(parts[0])
                            lat = float(parts[1])
                            
                            pontos_encontrados.append({
                                'nome': name,
                                'descricao': desc,
                                'latitude': lat,
                                'longitude': lon
                            })
                        except ValueError:
                            logger.warning(f"Coordenadas inválidas para Placemark '{name}': {coords_text}")

            else:
                # Se não tem Point, pode ser MultiGeometry? 
                # Por simplificação, focamos em Point direto ou dentro de MultiGeometry
                # Se quiser suporte a MultiGeometry, precisa recurse.
                # Vamos tentar buscar Point dentro do Placemark recursivamente se não achou direto?
                # find_all procura recursivo (.//).
                # find('Point') procura filho direto.
                # Placemark pode ter MultiGeometry -> Point.
                # Vamos usar find_all('Point') dentro do Placemark e pegar o primeiro?
                points_recursive = find_all(pm, 'Point')
                if points_recursive and not point:
                    # Pegar o primeiro ponto encontrado na geometria complexa
                    p_node = points_recursive[0]
                    coords_node = find(p_node, 'coordinates')
                    if coords_node is not None and coords_node.text:
                        coords_text = coords_node.text.strip()
                        parts = coords_text.split(',')
                        if len(parts) >= 2:
                            try:
                                lon = float(parts[0])
                                lat = float(parts[1])
                                pontos_encontrados.append({
                                    'nome': name,
                                    'descricao': desc,
                                    'latitude': lat,
                                    'longitude': lon
                                })
                            except ValueError:
                                pass

    except Exception as e:
        logger.error(f"Erro ao processar KML {file_path}: {e}")
        raise ValueError(f"Erro ao processar estrutura do KML: {str(e)}")
        
    return pontos_encontrados
