"""Add mapped acreage to outlined cemeteries and mark the Calvary divisions covered by Calvary's count.

Acreage is the area of each OpenStreetMap outline (equirectangular projection at NYC's latitude),
rounded to the acre. Calvary's operator gives one figure for the whole cemetery and describes its
four divisions (First through Fourth Calvary, 365 acres) on the same page:
https://calvaryandalliedcemeteries.com/calvary-cemetery/
"""
import json, math
from pathlib import Path
from shapely.geometry import shape
from shapely.ops import transform

REPO = Path(__file__).resolve().parents[2]
p = REPO / 'data' / 'cemeteries.geojson'
geo = json.load(open(p))
k = math.cos(math.radians(40.7))

for f in geo['features']:
    q = f['properties']
    if f['geometry']['type'] != 'Point':
        s = transform(lambda x, y, z=None: (x * 111320 * k, y * 110574), shape(f['geometry']))
        q['acres'] = round(s.area / 4046.86)
    if q['name'] == 'Calvary Cemetery' and q['borough'] == 'Queens':
        q['count_note'] = ('Covers all four divisions of Calvary (First through Fourth, 365 acres), which the map draws as '
                           'Calvary Cemetery and New Calvary Cemetery. A figure of about 3 million, repeated by Wikipedia and others, '
                           "traces to an uncited 2008 article; the cemetery's own figure is used here. The operator separately says "
                           'almost 2 million people are buried across its five cemeteries combined.')
    if q['borough'] == 'Queens' and (q['name'] == 'New Calvary Cemetery' or q['name'].startswith('New Calvary Cemetery (')):
        q['count_included_in'] = 'Calvary Cemetery'

json.dump(geo, open(p, 'w'), ensure_ascii=False, separators=(',', ':'))
print([ (f['properties']['name'], f['properties'].get('acres')) for f in geo['features']
        if f['properties'].get('count_included_in')])
