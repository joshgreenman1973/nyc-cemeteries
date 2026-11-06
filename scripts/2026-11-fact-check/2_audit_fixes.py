"""November 2026 second pass: data and catalogue fixes to cemeteries.geojson and notables.json.

1. Merge the remaining duplicate records:
   - Uptown Trinity Cemetery (meade_id 3093): Meade's catalogue has two records with id 3093 (West
     Division, 9.44 acres; East Division, 8.28 acres). The OpenStreetMap polygon for Trinity Cemetery
     covers both divisions; merge the remaining East Division Meade point into it and sum both Meade
     footprints (17.71 acres).
   - Heart of Jesus Cemetery (OSM, Staten Island) sits inside Meade record 5045 (Polish National/
     Christian Rehoboth Cemetery, 0.70 acre); merge them and remove the duplicate Meade point.
2. Copy Meade's missing fields (meade_name, close_yr, oblit_yr, other, approx, meade_sources, and
   capitalized religion) onto the 61 OpenStreetMap features matched in June 2026, which had omitted
   them. Append an ellipsis to 253/254-character strings truncated mid-word by Meade's shapefile export.
3. Remove Mount Judah Cemetery (1912) and Hart Island (1869) from the Meade-departures overrides,
   since Meade's catalogue already gives 1912 and 1869; clear conflicting close_yr values on
   New York City Marble Cemetery (Active) and New Utrecht Cemetery (where LPC documented use through
   1997). Clarify Saint Raymond's and Calvary's multi-record notes.
4. Strip duplicate ' graves' suffix from count_display on Saint Peter's Cemetery and Lawrence Cemetery
   so the UI does not render 'about 50,000 graves graves' and 'about 89 graves graves'.
5. Update official website URLs (add Mount Judah, Chatham Square, Second Shearith Israel, St. Paul's
   Churchyard; align Calvary and Evergreens with their canonical operator URLs).
6. In notables.json, drop unsourced/contradicted claims for actor Robert Blake (1933-2023, cremated
   in Los Angeles) at Saint Peter's Cemetery (Staten Island) and artist Jeanne-Claude (1935-2009,
   donated body to science) at Hart Island, and backfill the 150th notable by sitelinks (John George
   Brown) at Green-Wood Cemetery from data/burials.json.

Safe to rerun. Run scripts/2026-10-fact-check/5_build_methodology.py afterward.
"""
import json, re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
geo_path = REPO / 'data' / 'cemeteries.geojson'
nob_path = REPO / 'data' / 'notables.json'
meade_path = REPO / 'data' / 'meade_cemeteries.json'
burials_path = REPO / 'data' / 'burials.json'

geo = json.load(open(geo_path))
nob = json.load(open(nob_path))
meade = json.load(open(meade_path))
burials = json.load(open(burials_path))

byid = {}
for r in meade:
    byid.setdefault(r['id'], []).append(r)

# 1a. Remove duplicate Meade point for Trinity East Division (meade_id 3093, source='meade')
# and set Trinity Cemetery's meade_acres to the sum of both 3093 parcels (9.4366 + 8.2768 = 17.71).
geo['features'] = [
    f for f in geo['features']
    if not (f['properties'].get('source') == 'meade' and f['properties'].get('meade_id') == 3093)
]
for f in geo['features']:
    p = f['properties']
    if p.get('meade_id') == 3093 and p.get('source') == 'osm':
        p['meade_acres'] = 17.71

# 1b. Merge Heart of Jesus Cemetery (OSM) with Polish National/Christian Rehoboth Cemetery (meade_id 5045).
r5045 = byid[5045][0]
meade_5045_acres = 0.7
for f in geo['features']:
    p = f['properties']
    if p.get('source') == 'meade' and p.get('meade_id') == 5045 and p.get('meade_acres'):
        meade_5045_acres = p['meade_acres']

geo['features'] = [
    f for f in geo['features']
    if not (f['properties'].get('source') == 'meade' and f['properties'].get('meade_id') == 5045)
]
for f in geo['features']:
    p = f['properties']
    if p['name'] == 'Heart of Jesus Cemetery' and p['borough'] == 'Staten Island':
        p.update({
            'meade_id': 5045,
            'meade_name': r5045['name'],
            'status': r5045['status'],
            'founded': 1904,
            'cem_type': r5045['type'],
            'subtype': r5045['subtype'],
            'religion': r5045['religion'],
            'close_yr': r5045['close_yr'],
            'oblit_yr': r5045['oblit_yr'],
            'other': r5045['other'] or None,
            'meade_sources': r5045['sources'],
            'approx': r5045['approx'],
            'meade_acres': meade_5045_acres,
        })

# 2. Populate missing Meade fields on all matched OSM features.
for f in geo['features']:
    p = f['properties']
    mid = p.get('meade_id')
    if p.get('source') == 'osm' and mid and mid in byid:
        r = byid[mid][0]
        if not p.get('meade_name'):
            p['meade_name'] = r['name']
        if p.get('close_yr') is None and r.get('close_yr'):
            p['close_yr'] = r['close_yr']
        if p.get('oblit_yr') is None and r.get('oblit_yr'):
            p['oblit_yr'] = r['oblit_yr']
        if not p.get('other') and r.get('other'):
            p['other'] = r['other']
        if p.get('approx') is None:
            p['approx'] = r.get('approx', False)
        if not p.get('meade_sources') and r.get('sources'):
            p['meade_sources'] = r['sources']
        if r.get('religion'):
            p['religion'] = r['religion']
        elif p.get('religion') and p['religion'][0].islower():
            p['religion'] = p['religion'].capitalize()

# Mark 253/254-char shapefile-truncated strings with an ellipsis if cut mid-sentence.
for f in geo['features']:
    p = f['properties']
    for k in ('other', 'meade_sources'):
        v = p.get(k)
        if v and len(v.rstrip('…')) in (253, 254):
            base = v.rstrip('…')
            if not base.endswith(('.', ')')) and not base.endswith('1890'):
                p[k] = base + '…'

# 3. Clean up departures and conflicting close_yr values.
for f in geo['features']:
    p = f['properties']
    # Mount Judah (1912) and Hart Island (1869) match Meade's open_yr; not departures from Meade.
    if p['name'] in ('Mount Judah Cemetery', 'Hart Island (City Cemetery)'):
        for k in ('founded_display', 'founded_source_label', 'founded_source', 'founded_note'):
            p.pop(k, None)
    # Clear close_yr where status or status_note supersedes Meade's closing year.
    if p['name'] in ('New York City Marble Cemetery', 'New Utrecht Cemetery'):
        p['close_yr'] = None
    if p['name'] == 'Saint Raymond’s Cemetery':
        p['founded_note'] = (
            "Meade lists the old cemetery (opened 1875, shown separately as Preserved) and the new "
            "cemetery (opened 1954, 110 acres) as separate records; this outline and the Wikidata "
            "notables here cover both."
        )
    if p['name'] == 'Calvary Cemetery' and p['borough'] == 'Queens':
        p['count_note'] = (
            "Covers all four divisions of Calvary (First through Fourth, 365 acres), which the map "
            "draws as Calvary Cemetery and New Calvary Cemetery (plus separate catalogue points for "
            "Third and Fourth Calvary). A figure of about 3 million, repeated by Wikipedia and others, "
            "traces to an uncited 2008 article; the cemetery's own figure is used here. The operator "
            "separately says almost 2 million people are buried across its five cemeteries combined."
        )

# 4. Fix 'graves graves' duplication in count_display.
for f in geo['features']:
    p = f['properties']
    if p.get('count_type') == 'graves' and p.get('count_display', '').endswith(' graves'):
        p['count_display'] = p['count_display'][:-len(' graves')]

# 5. Official website additions and canonical URL updates.
WEBSITES = {
    'Calvary Cemetery|Queens': 'https://calvaryandalliedcemeteries.com/calvary-cemetery/',
    'Cemetery of the Evergreens|Queens': 'https://www.theevergreenscemetery.org/',
    'Mount Judah Cemetery|Queens': 'https://www.mountjudah.com/',
    'Chatham Square Cemetery|Manhattan': 'https://shearithisrael.org/about/cemeteries/',
    'Second Cemetery of Congregation Shearith Israel|Manhattan': 'https://shearithisrael.org/about/cemeteries/',
    'Third Cemetery of the Spanish-Portuguese Synagogue|Manhattan': 'https://shearithisrael.org/about/cemeteries/',
    "St. Paul's Churchyard|Manhattan": 'https://trinitychurchnyc.org/visit-history/places/churchyards-registers',
}
for f in geo['features']:
    p = f['properties']
    key = f"{p['name']}|{p['borough']}"
    if key in WEBSITES:
        p['website'] = WEBSITES[key]

# 6. Notables fixes: drop Robert Blake (Q7591318) and Jeanne-Claude (Q2646503); backfill Green-Wood to 150.
DROP_NOTABLES = [
    ('Q7591318', 'Robert Blake'),
    ('Q2646503', 'Jeanne-Claude'),
]
for q, name in DROP_NOTABLES:
    before = len(nob[q])
    nob[q] = [x for x in nob[q] if x['n'] != name]
    if len(nob[q]) != before:
        for f in geo['features']:
            p = f['properties']
            if p.get('wikidata') == q:
                p['n_notables'] = len(nob[q])

# Backfill Green-Wood (Q239043) to 150 shipped notables from burials.json
gw_existing = {x['n'] for x in nob['Q239043']}
for item in burials['Q239043']:
    if len(nob['Q239043']) >= 150:
        break
    if item['name'] not in gw_existing and item['name'] != 'Margaret Sanger':
        nob['Q239043'].append({
            'n': item['name'],
            'd': item['desc'],
            'b': item['birth'],
            'x': item['death'],
            'w': item['enwiki'],
            'l': item['links'],
        })
        gw_existing.add(item['name'])

assert len(nob['Q239043']) == 150, len(nob['Q239043'])

json.dump(geo, open(geo_path, 'w'), ensure_ascii=False, separators=(',', ':'))
json.dump(nob, open(nob_path, 'w'), ensure_ascii=False, separators=(',', ':'))
print('Updated cemeteries:', len(geo['features']), '| Green-Wood shipped notables:', len(nob['Q239043']))
