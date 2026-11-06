"""November 2026 follow-up fact-check: data changes to data/cemeteries.geojson.

1. Brinckerhoff's 77 is a count of gravestones and markers recorded in a 1919 survey (LPC designation
   report, 2012), not of people. It gets its own count_type, "markers", and stays out of both the
   people and the graves totals.
2. Every count gets a count_source_type, kept separate from count_confidence, so the map can say what
   kind of source each figure comes from (a high-confidence figure can come from a news report).
3. Mokom Sholom's JewishGen file gets an archived copy. The original URL still serves the file to
   browsers (it returns 404 to some automated clients); the 12,000 passage was checked in both copies
   on November 6, 2026.
4. Count notes that said a cemetery "publishes no total" now say no total was located.

The script is safe to rerun.

Rerun scripts/2026-10-fact-check/5_build_methodology.py afterward.
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
path = REPO / 'data' / 'cemeteries.geojson'
geo = json.load(open(path))
P = {f['properties']['name']: f['properties'] for f in geo['features'] if f['properties'].get('count')}

b = P['Brinckerhoff Cemetery']
b.update(count_type='markers', count_display='77', count_year=1919)

P['Mokom Sholom Cemetery']['count_source_archive'] = (
    'https://web.archive.org/web/20250806001046/https://www.jewishgen.org/INFOFILES/mokomcem.txt')

def source_type(p):
    lab = p['count_source_label']
    if 'Cemetery Project' in lab or 'JewishGen' in lab:
        return 'researcher'
    if lab.startswith('Wikipedia, citing'):
        return 'news'
    if lab == 'Wikipedia':
        return 'wikipedia'
    if 'Untapped Cities' in lab:
        return 'news'
    if 'Landmarks Conservancy' in lab or 'Historic Districts Council' in lab:
        return 'advocacy'
    if any(k in lab for k in ('Landmarks Preservation Commission', 'NYC Parks', 'Veterans Affairs')):
        return 'government'
    if "website" in lab or "operator" in lab or "records" in lab:
        return 'operator'
    raise ValueError(f"unclassified source for {p['name']}: {lab}")

for p in P.values():
    p['count_source_type'] = source_type(p)

# 4. Notes said a cemetery "publishes no total"; what is established is that none was located.
NOTE_FIXES = [
    ('; the cemetery publishes no total.', '; no total from the cemetery itself was located.'),
    ('; no recorded total has been published.', '; no recorded total was located.'),
    ('; no total for the whole cemetery is published.', '; no total for the whole cemetery was located.'),
]
for p in P.values():
    for old, new in NOTE_FIXES:
        if p.get('count_note'):
            p['count_note'] = p['count_note'].replace(old, new)

json.dump(geo, open(path, 'w'), ensure_ascii=False, separators=(',', ':'))
for t in sorted({p['count_source_type'] for p in P.values()}):
    print(t, [n for n, p in P.items() if p['count_source_type'] == t])
