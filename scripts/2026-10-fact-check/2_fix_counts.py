"""Apply source-verified burial-count corrections and attach a named source to every count."""
import json

REPO = str(__import__('pathlib').Path(__file__).resolve().parents[2])
SP = str(__import__('pathlib').Path(__file__).resolve().parent)
geo = json.load(open(f'{REPO}/data/cemeteries.geojson'))

fixes = {}
for fn in ('count_fixes_A.json', 'count_fixes_B.json'):
    fixes.update(json.load(open(f'{SP}/{fn}')))

NYCCP = 'New York City Cemetery Project (Mary French), {}'
# key -> (source label, note shown under the source line or None)
LABELS = {
    'All Faiths Cemetery|Queens': ("All Faiths Cemetery's website", None),
    'Baron Hirsch Cemetery|Staten Island': (NYCCP.format(2020), None),
    'Bayside Cemetery|Queens': ('Wikipedia, citing The New York Times (2008)', None),
    'Brinckerhoff Cemetery|Queens': ('NYC Landmarks Preservation Commission designation report (2012)',
        '77 gravestones and markers were recorded in a 1919 survey; the commission says far more people were most likely buried here.'),
    'Calvary Cemetery|Queens': ("Calvary & Allied Cemeteries, the cemetery's operator",
        'A figure of about 3 million, repeated by Wikipedia and others, traces to an uncited 2008 article; the cemetery\'s own figure is used here.'),
    'Canarsie Cemetery|Brooklyn': ("Canarsie Cemetery's website", None),
    'Cedar Grove Cemetery|Queens': ("Cedar Grove Cemetery's website", None),
    'Cemetery of the Evergreens|Queens': ("The Evergreens Cemetery's website", None),
    'Cemetery of the Resurrection|Staten Island': ("Calvary & Allied Cemeteries, the cemetery's operator",
        'Includes people entombed in crypts and inurned in niches.'),
    'Cypress Hills Cemetery|Queens': ('Wikipedia', 'Wikipedia gives this figure without a citation; the cemetery publishes no total.'),
    'Cypress Hills National Cemetery|Brooklyn': ('U.S. Department of Veterans Affairs (archived 2006 page)',
        'The VA counted 21,098 interments through fiscal 2005; the cemetery is closed to new graves.'),
    'Flushing Cemetery|Queens': ('Wikipedia, citing a 1951 newspaper profile',
        'This is a 1951 figure; the cemetery has kept burying since, so the current total is higher.'),
    'Frederick Douglass Memorial Park|Staten Island': ('New York Landmarks Conservancy (2024)',
        'An estimate, not a ledger count; no recorded total has been published.'),
    'Green-Wood Cemetery|Brooklyn': ("Green-Wood Cemetery's website", 'Some other Green-Wood pages say 570,000.'),
    'Holy Cross Cemetery|Brooklyn': (NYCCP.format(2018), None),
    'Lawrence Cemetery|Queens': ('Historic Districts Council', None),
    'Linden Hill Cemetery|Queens': (NYCCP.format(2018), 'Covers the Methodist cemetery only, not the adjoining Jewish section.'),
    'Maple Grove Cemetery|Queens': ('Wikipedia', 'Wikipedia gives this figure without a citation; the cemetery publishes no total.'),
    'Mokom Sholom Cemetery|Queens': ('JewishGen (Florence Marmor, 1995)',
        'Counts only the free-burial section from 1866 to 1901; no total for the whole cemetery is published.'),
    'Montefiore Cemetery|Queens': ('Wikipedia', 'Wikipedia gives this figure without a citation; the cemetery publishes no total.'),
    'Moore-Jackson Cemetery|Queens': ('NYC Landmarks Preservation Commission designation report (1997)', None),
    'Most Holy Trinity Cemetery|Brooklyn': (NYCCP.format(2013), None),
    'Mount Carmel Cemetery|Queens': ("Mount Carmel Cemetery's website", 'Interments in Sections 1 through 5.'),
    'Mount Hebron Cemetery|Queens': ("Mount Hebron Cemetery's website", None),
    'Mount Judah Cemetery|Queens': ("Mount Judah Cemetery's website", None),
    'Mount Lebanon Cemetery|Queens': ("Mount Lebanon Cemetery's website", None),
    'Mount Olivet Cemetery|Queens': (NYCCP.format(2020), None),
    'Mount Saint Mary Cemetery|Queens': (NYCCP.format(2021), None),
    'Mount Zion Cemetery|Queens': ("Mount Zion Cemetery's website", None),
    'New York City Marble Cemetery|Manhattan': ('Untapped Cities (2012)', "A journalist's estimate; the cemetery publishes no total."),
    'New York Marble Cemetery|Manhattan': ("New York Marble Cemetery's records",
        'The register and vault lists hold 2,080 names.'),
    'Prospect Cemetery|Queens': ('Wikipedia', 'The sentence carries no direct citation; the nearest reference is a 1976 Queens Community Planning Board 12 report.'),
    'Saint Michael’s Cemetery|Queens': (NYCCP.format(2021), None),
    'Saint Peter’s Cemetery|Staten Island': (NYCCP.format(2021), None),
    'Salem Fields Cemetery|Brooklyn': (NYCCP.format(2011), None),
    'Trinity Cemetery|Manhattan': (NYCCP.format(2025), None),
    'Washington Cemetery|Brooklyn': (NYCCP.format(2016), None),
    'Woodlawn Cemetery|Bronx': ("Woodlawn Cemetery's website", None),
    'Hart Island (City Cemetery)|Bronx': ('NYC Parks', 'The City Council also reports more than 1 million burials since 1869.'),
}

done = set()
for f in geo['features']:
    p = f['properties']
    key = f"{p['name']}|{p['borough']}"
    if key in fixes:
        p.update(fixes[key]); done.add(key)
    if p.get('count'):
        lab, note = LABELS[key]
        p['count_source_label'] = lab
        if note: p['count_note'] = note
        else: p.pop('count_note', None)
    else:
        for k in ('count', 'count_display', 'count_type', 'count_confidence', 'count_source',
                  'count_source_label', 'count_note'):
            p.pop(k, None)

missing = set(fixes) - done
assert not missing, missing
json.dump(geo, open(f'{REPO}/data/cemeteries.geojson', 'w'), ensure_ascii=False, separators=(',', ':'))
rows = sorted([f['properties'] for f in geo['features'] if f['properties'].get('count')], key=lambda p: -p['count'])
for p in rows:
    print(f"{p['name']:<34} {p['count']:>9,} | {p['count_display']:<32} | {p['count_type']:<10} | {p['count_confidence']:<6} | {p['count_source_label']}")
print(len(rows), 'counts')
