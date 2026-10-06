"""Merge OpenStreetMap cemeteries that duplicate a record in Meade's catalogue.

Each pair below was checked by hand: the Meade point lies inside (or within a few
metres of) the OSM shape and names the same burial ground. The OSM feature keeps
its shape, Wikidata link, count, website and notables; it takes Meade's status,
founding year, type, notes and citations, and the duplicate Meade point is removed.
"""
import json, re, math, sys

REPO = str(__import__('pathlib').Path(__file__).resolve().parents[2])
geo = json.load(open(f'{REPO}/data/cemeteries.geojson'))
meade = json.load(open(f'{REPO}/data/meade_cemeteries.json'))

# (OSM name, Meade id, Meade lat) — lat disambiguates Meade ids used twice
MERGES = [
    ('Ahawith Chesed Cemetery', 4003, None), ('All Faiths Cemetery', 4048, None),
    ('Washington Cemetery|Staten Island', 5003, None),
    ('Beth Olom Cemetery', 2003, None), ('Bethel Cemetery', 5006, None),
    ('Blazing Star Cemetery', 5008, None), ('Bloomingdale Road Cemetery', 5042, None),
    ('Brinckerhoff Cemetery', 4016, None), ('Calvary Cemetery', 4018, None),
    ('Cemetery of the Resurrection', 5011, None), ('Charleston Cemetery', 5085, None),
    ('Chatham Square Cemetery', 30221, None), ('Cornell Burial Ground', 4023, None),
    ('Enslaved African and Kingsbridge Burial Grounds', 1042, None),
    ('Grace Cemetery', 4038, None), ('Holy Cross Cemetery', 2020, None),
    ('Jesuit Cemetery, Fordham University', 1013, None),
    ("Lake/Silvie's Cemetery", 5030, None), ('Lawrence Cemetery', 4044, None),
    ('Linden Hill Cemetery', 4047, None), ('Merrill Cemetery', 5035, None),
    ('New Calvary Cemetery', 4066, None), ('New Utrecht Cemetery', 2031, None),
    ('Ocean View Cemetery', 5044, None), ('Old West Farms Soldiers Cemetery', 1052, None),
    ('Pelham Cemetery', 1033, None), ('Quaker Cemetery', 2033, None),
    ('Reformed Church on Staten Island Cemetery', 5046, None),
    ('Rezeau-Van Pelt Cemetery', 5082, None),
    ('Rossville A.M.E. Zion Church Cemetery', 5053, None),
    ("Saint Ann's Graveyard", 1036, None), ("Saint Peter's Graveyard", 1038, None),
    ('Second Cemetery of Congregation Shearith Israel', 30531, None),
    ("Snug Harbor Sailor's Cemetery", 5055, None),
    ('Southside Burial Ground', 4087, None),
    ("St. John's Lutheran Church Cemetery", 5059, None),
    ("St. Mary's of the Assumption Church Cemetery", 5063, None),
    ('Sylvan Cemetery - Patterson Cemetery', 5076, None),
    ('Third Cemetery of the Spanish-Portuguese Synagogue', 3095, None),
    ('Trinity Cemetery', 3093, 40.832967),
    ('Van Courtlandt Family Vault', 1048, None), ('Willet Family Burial Ground', 4092, None),
    ('Wyckoff-Snediker Cemetery', 4093, None), ('Zion Episcopal Cemetery', 4094, None),
    ('Hart Island (City Cemetery)', 1029, None),
    # Union Field and New Union Field were cross-matched; re-pair them.
    ('Union Field Cemetery', 4089, None), ('New Union Field Cemetery', 4010, None),
]
# OSM point features that duplicate another OSM feature at the same site
DROP_OSM = [('Asbury Methodist Cemetery', 'Staten Island')]

byid = {}
for r in meade:
    byid.setdefault(r['id'], []).append(r)

def year(s):
    m = re.search(r'\d{4}', str(s or ''))
    return int(m.group()) if m else None

def year_display(s):
    s = str(s or '').strip()
    if not year(s):
        return None
    s = re.sub(r'^(circa|ca\.?)\s*', 'c. ', s, flags=re.I)
    s = re.sub(r'^c\.(?=\d)', 'c. ', s)
    return s

feats = geo['features']
def find_osm(key):
    name, _, boro = key.partition('|')
    hits = [f for f in feats if f['properties']['name'] == name and f['properties']['source'] == 'osm'
            and (not boro or f['properties']['borough'] == boro)]
    assert len(hits) == 1, (key, len(hits))
    return hits[0]

def find_meade_point(mid, lat):
    hits = [f for f in feats if f['properties']['source'] == 'meade' and f['properties'].get('meade_id') == mid]
    if lat is not None:
        hits = [f for f in hits if abs(f['properties']['center'][0] - lat) < 1e-4]
    return hits

def meade_record(mid, lat):
    recs = byid[mid]
    if lat is not None:
        recs = [r for r in recs if abs(r['lat'] - lat) < 1e-4]
    assert len(recs) == 1, (mid, lat, len(recs))
    return recs[0]

removed, log = [], []
for key, mid, lat in MERGES:
    o = find_osm(key)
    p = o['properties']
    r = meade_record(mid, lat)
    before = (p['status'], p.get('founded'))
    p.update({
        'meade_id': mid, 'meade_name': r['name'], 'status': r['status'],
        'founded': year(r['open_yr']), 'cem_type': r['type'], 'subtype': r['subtype'],
        'close_yr': r['close_yr'], 'oblit_yr': r['oblit_yr'], 'other': r['other'],
        'meade_sources': r['sources'], 'approx': r['approx'],
    })
    if r.get('religion'):
        p['religion'] = r['religion']
    pts = find_meade_point(mid, lat if lat is not None else None)
    if mid == 4089:
        assert not pts  # was consumed by the wrong OSM feature; nothing to remove
    else:
        assert len(pts) == 1, (key, mid, len(pts))
        removed.append(pts[0])
    log.append(f"{key}: {before} -> {(p['status'], p['founded'])} [{r['name']}]")

for name, boro in DROP_OSM:
    hits = [f for f in feats if f['properties']['name'] == name and f['properties']['borough'] == boro]
    assert len(hits) == 1
    removed.append(hits[0])
    log.append(f'dropped duplicate OSM point: {name}')

ids = {id(f) for f in removed}
geo['features'] = [f for f in feats if id(f) not in ids]

# Founding-year display keeps Meade's qualifiers ("c. 1643", "1656 or 1683")
for f in geo['features']:
    p = f['properties']
    if p.get('meade_id'):
        recs = byid[p['meade_id']]
        raw = recs[0]['open_yr']
        d = year_display(raw)
        if d and not re.fullmatch(r'\d{4}', d):
            p['founded_display'] = d
        else:
            p.pop('founded_display', None)

json.dump(geo, open(f'{REPO}/data/cemeteries.geojson', 'w'), ensure_ascii=False, separators=(',', ':'))
print('\n'.join(log))
print('removed', len(removed), 'features; total now', len(geo['features']))
