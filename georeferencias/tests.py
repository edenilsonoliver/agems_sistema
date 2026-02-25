from django.test import TestCase, SimpleTestCase
from .models import CamadaReferencia, PontoReferencia
from .kml_parser import parse_kml
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
            elementos = parse_kml(tmp_path)
            self.assertEqual(len(elementos), 3)
            
            # 1. Ponto
            ponto = [e for e in elementos if e['tipo_geometria'] == 'Point'][0]
            self.assertEqual(ponto['nome'], 'Ponto Teste')
            self.assertAlmostEqual(ponto['latitude'], -20.4697)
            
            # 2. Linha
            linha = [e for e in elementos if e['tipo_geometria'] == 'LineString'][0]
            self.assertEqual(linha['nome'], 'Linha Teste')
            self.assertEqual(linha['estilo']['stroke_color'], '#0000ff') # aabbggrr 7fff0000 -> rr=00, gg=00, bb=ff
            self.assertEqual(len(linha['coordenadas']), 2)
            
            # 3. Polígono
            poly = [e for e in elementos if e['tipo_geometria'] == 'Polygon'][0]
            self.assertEqual(poly['nome'], 'Poligono Teste')
            self.assertEqual(poly['estilo']['fill_color'], '#00ff00')
            self.assertEqual(len(poly['coordenadas'][0]), 4) # Exterior ring
            
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

class CamadaModelTest(TestCase):
    def test_create_camada_with_point(self):
        camada = CamadaReferencia.objects.create(nome="Teste Camada", cor_marcador="#000000")
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
