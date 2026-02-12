from django.test import TestCase, SimpleTestCase
from .models import CamadaReferencia
from .kml_parser import parse_kml
import os
import tempfile

class KMLParserTest(SimpleTestCase):
    def test_parse_simple_kml(self):
        kml_content = """<?xml version="1.0" encoding="UTF-8"?>
<kml>
  <Document>
    <Placemark>
      <name>Ponto Teste</name>
      <description>Teste de descrição</description>
      <Point>
        <coordinates>-54.6201,-20.4697,0</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>"""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.kml', delete=False) as tmp:
            tmp.write(kml_content.encode('utf-8'))
            tmp_path = tmp.name
            
        try:
            pontos = parse_kml(tmp_path)
            self.assertEqual(len(pontos), 1)
            self.assertEqual(pontos[0]['nome'], 'Ponto Teste')
            # KML coordinates are lon,lat. Point y is lat.
            self.assertAlmostEqual(pontos[0]['latitude'], -20.4697)
            self.assertAlmostEqual(pontos[0]['longitude'], -54.6201)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

class CamadaModelTest(TestCase):
    def test_create_camada(self):
        camada = CamadaReferencia.objects.create(nome="Teste Camada", cor_marcador="#000000")
        self.assertEqual(str(camada), "Teste Camada")
