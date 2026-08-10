from django.test import TestCase, SimpleTestCase
from .models import CamadaReferencia, PontoReferencia
from .kml_parser import parse_kml
from .kml_validator import validate_kml_file
import os
import tempfile

class KMLParserTest(SimpleTestCase):
    def test_parse_complex_kml(self):
        kml_content = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Style id="linhaAzul">
      <LineStyle>
        <color>7fff0000</color> <!-- Blue, 50% opacity -->
        <width>4</width>
      </LineStyle>
    </Style>
    <Style id="poligonoVerde">
      <PolyStyle>
        <color>ff00ff00</color> <!-- Green, 100% opacity -->
      </PolyStyle>
    </Style>
    
    <Placemark>
      <name>Ponto Teste</name>
      <Point><coordinates>-54.6201,-20.4697,0</coordinates></Point>
    </Placemark>
    
    <Placemark>
      <name>Linha Teste</name>
      <styleUrl>#linhaAzul</styleUrl>
      <LineString>
        <coordinates>-54.6201,-20.4697,0 -54.6301,-20.4797,0</coordinates>
      </LineString>
    </Placemark>
    
    <Placemark>
      <name>Poligono Teste</name>
      <styleUrl>#poligonoVerde</styleUrl>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>-54.6201,-20.4697,0 -54.6301,-20.4697,0 -54.6301,-20.4797,0 -54.6201,-20.4697,0</coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>"""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.kml', delete=False) as tmp:
            tmp.write(kml_content.encode('utf-8'))
            tmp_path = tmp.name
            
        try:
            parse_result = parse_kml(tmp_path)
            elementos = parse_result.get('elementos', [])
            self.assertEqual(len(elementos), 3)
            
            # 1. Ponto
            ponto = [e for e in elementos if e['tipo_geometria'] == 'Point'][0]
            self.assertEqual(ponto['nome'], 'Ponto Teste')
            self.assertAlmostEqual(ponto['latitude'], -20.4697)
            
            # 2. Linha
            linha = [e for e in elementos if e['tipo_geometria'] == 'LineString'][0]
            self.assertEqual(linha['nome'], 'Linha Teste')
            self.assertEqual(linha['estilo']['stroke_color'], '#0000ff')
            self.assertEqual(len(linha['coordenadas']), 2)
            
            # 3. Polígono
            poly = [e for e in elementos if e['tipo_geometria'] == 'Polygon'][0]
            self.assertEqual(poly['nome'], 'Poligono Teste')
            self.assertEqual(poly['estilo']['fill_color'], '#00ff00')
            self.assertEqual(len(poly['coordenadas'][0]), 4)
            
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_kml_validator_with_valid_and_invalid_placemarks(self):
        kml_content = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Ponto Valido</name>
      <Point><coordinates>-54.6201,-20.4697,0</coordinates></Point>
    </Placemark>
    <Placemark>
      <name>Ponto Invalido Lat/Lon</name>
      <Point><coordinates>-999.0,999.0,0</coordinates></Point>
    </Placemark>
  </Document>
</kml>"""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.kml', delete=False) as tmp:
            tmp.write(kml_content.encode('utf-8'))
            tmp_path = tmp.name

        try:
            val_res = validate_kml_file(tmp_path)
            self.assertTrue(val_res['is_valid'])
            self.assertEqual(val_res['valid_placemarks_count'], 1)
            self.assertEqual(val_res['discarded_placemarks_count'], 1)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_kml_validator_with_document_root(self):
        kml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="http://earth.google.com/kml/2.0">
  <Placemark>
    <name>Ponto Document Root</name>
    <Point><coordinates>-54.6201,-20.4697,0</coordinates></Point>
  </Placemark>
</Document>"""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.kml', delete=False) as tmp:
            tmp.write(kml_content.encode('utf-8'))
            tmp_path = tmp.name

        try:
            val_res = validate_kml_file(tmp_path)
            self.assertTrue(val_res['is_valid'])
            self.assertEqual(val_res['valid_placemarks_count'], 1)
            self.assertEqual(val_res['total_placemarks'], 1)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

class CamadaModelTest(TestCase):
    def test_create_camada_with_point(self):
        camada = CamadaReferencia.objects.create(nome="Teste Camada")
        ponto = PontoReferencia.objects.create(
            camada=camada,
            nome="Elemento Teste",
            tipo_geometria='LineString',
            latitude=-20.4697,
            longitude=-54.6201,
            coordenadas_json=[[-54.6201, -20.4697], [-54.6301, -20.4797]]
        )
        self.assertEqual(ponto.tipo_geometria, 'LineString')
        self.assertEqual(ponto.coordenadas_json[0][0], -54.6201)
