import os
import sys

# Mock Django setup if needed, but the parser is pure python
# Actually, the parser needs lxml. Let's run it from the venv.

from georeferencias.kml_parser import parse_kml

kml_content = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Mixed Geometry</name>
      <MultiGeometry>
        <Point><coordinates>-54.6,-20.4,0</coordinates></Point>
        <LineString><coordinates>-54.6,-20.4,0 -54.7,-20.5,0</coordinates></LineString>
      </MultiGeometry>
    </Placemark>
    <Placemark>
      <name>Separate Point</name>
      <Point><coordinates>-54.8,-20.6,0</coordinates></Point>
    </Placemark>
    <Placemark>
      <name>Separate Line</name>
      <LineString><coordinates>-54.9,-20.7,0 -55.0,-20.8,0</coordinates></LineString>
    </Placemark>
  </Document>
</kml>
"""

with open('debug_mixed.kml', 'w', encoding='utf-8') as f:
    f.write(kml_content)

print("--- Running Parser ---")
try:
    elements = parse_kml('debug_mixed.kml')
    print(f"Total elements found: {len(elements)}")
    for i, e in enumerate(elements):
        print(f"[{i}] {e['nome']} - {e['tipo_geometria']}")
except Exception as e:
    print(f"ERROR: {e}")
finally:
    if os.path.exists('debug_mixed.kml'):
        os.remove('debug_mixed.kml')
