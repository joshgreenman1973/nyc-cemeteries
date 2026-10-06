"""Attach Meade's mapped footprint (acres) and her reinterment field to each site on the map.

Source: the web map behind cemeteriesofnyc.com (ArcGIS item 1f55b634df7e4e29a55f88fe134b9fb4), saved as
data/meade_webmap.json. Its first layer holds polygons for the 463 records whose location is known; its second
layer marks only a general vicinity for the rest, and Meade notes those shapes do not represent size, so they
get no acreage. Geometry is Web Mercator; it is converted to latitude/longitude and measured on an
equirectangular projection at New York City's latitude. The original June extract (data/meade_cemeteries.json)
kept only each shape's center and dropped the reinterment field.
"""
import json, math
from pathlib import Path
from shapely.geometry import Polygon
from shapely.validation import make_valid

REPO = Path(__file__).resolve().parents[2]
web = json.load(open(REPO / 'data' / 'meade_webmap.json'))
geo_path = REPO / 'data' / 'cemeteries.geojson'
geo = json.load(open(geo_path))

R, K = 6378137.0, math.cos(math.radians(40.7))
def lonlat(x, y):
    return math.degrees(x / R), math.degrees(2 * math.atan(math.exp(y / R)) - math.pi / 2)

recs = {}  # id -> list of {acres, reinterment, center}
for li, layer in enumerate(web['operationalLayers']):
    for L in layer['featureCollection']['layers']:
        for f in L['featureSet']['features']:
            a = f['attributes']
            shape = None
            for ring in f['geometry']['rings']:
                p = make_valid(Polygon([(lo * 111320 * K, la * 110574) for lo, la in (lonlat(x, y) for x, y in ring)]))
                shape = p if shape is None else shape.symmetric_difference(p)
            c = shape.centroid
            recs.setdefault(a['id'], []).append({
                'acres': shape.area / 4046.86 if li == 0 else None,   # vicinity shapes are not sizes
                'reinterment': (a.get("REINTERM'T") or '').strip(),
                'center': (c.y / 110574, c.x / (111320 * K)),
            })

n_area = n_rein = 0
for f in geo['features']:
    p = f['properties']
    p.pop('acres', None)  # superseded by Meade's footprint
    v = recs.get(p.get('meade_id'))
    if not v:
        continue
    lat, lon = p['center']
    r = min(v, key=lambda t: (t['center'][0] - lat) ** 2 + (t['center'][1] - lon) ** 2)
    if r['acres'] is not None:
        p['meade_acres'] = round(r['acres'], 2); n_area += 1
    if r['reinterment'] and r['reinterment'].lower() not in ('n/a', 'unknown', ''):
        p['reinterment'] = r['reinterment']; n_rein += 1
    else:
        p.pop('reinterment', None)

json.dump(geo, open(geo_path, 'w'), ensure_ascii=False, separators=(',', ':'))
print('sites with a footprint:', n_area, '| with a reinterment entry:', n_rein)
