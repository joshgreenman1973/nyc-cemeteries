"""Founding-year and status corrections, each tied to a named, checked source."""
import json

REPO = str(__import__('pathlib').Path(__file__).resolve().parents[2])
geo = json.load(open(f'{REPO}/data/cemeteries.geojson'))

LPC = 'NYC Landmarks Preservation Commission designation report ({})'
MEADE = 'https://www.cemeteriesofnyc.com/map'

# name|borough -> founding fields. founded_note explains any departure from Meade's year.
FOUNDED = {
    'Saint Raymonds Cemetery|Bronx': dict(founded=1875, founded_display='1875',
        founded_source_label="Meade's catalogue (old cemetery record)", founded_source=MEADE,
        founded_note='Meade lists the old cemetery (opened 1875) and the new cemetery (opened 1954) as separate records; this outline covers both.'),
    'Bayside Cemetery|Queens': dict(founded=1865, founded_display='1865',
        founded_source_label='JewishGen (Florence Marmor)', founded_source='https://www.jewishgen.org/InfoFiles/mokomcem.txt',
        founded_note="Founded by Congregation Shaare Tsedek. Meade's catalogue gives 1860."),
    'Moravian Cemetery|Staten Island': dict(founded=1740, founded_display='c. 1740',
        founded_source_label="Meade's catalogue notes", founded_source=MEADE,
        founded_note='Gravestones begin in 1740. Meade lists 1763, when the congregation bought its church plot, and 1842, when the cemetery was incorporated.'),
    'Old Gravesend Cemetery|Brooklyn': dict(founded=1658, founded_display='by 1658',
        founded_source_label=LPC.format(1976), founded_source='https://s-media.nyc.gov/agencies/lpc/lp/0921.pdf',
        founded_note="The burial ground existed by 1658; the earliest recorded death in Gravesend was in 1650. Meade's catalogue gives c. 1643."),
    'Chatham Square Cemetery|Manhattan': dict(founded=1683, founded_display='1683',
        founded_source_label='Congregation Shearith Israel', founded_source='https://shearithisrael.org/about/cemeteries/',
        founded_note="The land was bought in 1682 and the first burial was in 1683. Meade's catalogue gives 1656 or 1683."),
    'First Shearith Israel Cemetery|Manhattan': dict(founded=1683, founded_display='1683',
        founded_source_label='Congregation Shearith Israel', founded_source='https://shearithisrael.org/about/cemeteries/',
        founded_note="The land was bought in 1682 and the first burial was in 1683. Meade's catalogue gives 1656 or 1683."),
    'Mount Carmel Cemetery|Queens': dict(founded=1906, founded_display='1906',
        founded_source_label="Mount Carmel Cemetery's website", founded_source='http://www.mountcarmelcemetery.com/',
        founded_note="First burial December 28, 1906. Meade's catalogue gives 1902."),
    'Mount Judah Cemetery|Queens': dict(founded=1912, founded_display='1912',
        founded_source_label="Mount Judah Cemetery's website", founded_source='http://www.mountjudah.com/',
        founded_note='Incorporated 1908; first burial March 8, 1912.'),
    'Salem Fields Cemetery|Brooklyn': dict(founded=1852, founded_display='1852',
        founded_source_label="Meade's catalogue", founded_source=MEADE, founded_note=None),
    'Hart Island (City Cemetery)|Bronx': dict(founded=1869, founded_display='1869',
        founded_source_label='NYC Parks', founded_source='https://www.nycgovparks.org/parks/hart-island',
        founded_note='The city bought the island in 1868; public burials began in 1869.'),
}

STATUS = {
    'New York City Marble Cemetery|Manhattan': dict(status='Active',
        status_note="Meade's catalogue lists it as preserved, but descendants' family vaults still take occasional interments; the cemetery's register records one in October 2025.",
        status_source_label="New York City Marble Cemetery's register", status_source='http://www.nycmc.org/intermentvaults.html'),
    'New Utrecht Cemetery|Brooklyn': dict(
        status_note="Meade's catalogue lists it as closed in 1879, but the Landmarks Preservation Commission reported in 1998 that it was still in limited use, with the most recent burial in 1997.",
        status_source_label=LPC.format(1998), status_source='https://s-media.nyc.gov/agencies/lpc/lp/1978.pdf'),
    'Cypress Hills National Cemetery|Brooklyn': dict(
        status_note='Closed to new graves; eligible family members can still be buried in existing gravesites.',
        status_source_label='U.S. Department of Veterans Affairs', status_source='https://www.cem.va.gov/cems/nchp/cypresshills.asp'),
}

NEW_COUNTS = {
    'New Utrecht Cemetery|Brooklyn': dict(count=1300, count_display='approximately 1,300', count_type='interments',
        count_confidence='high', count_source='https://s-media.nyc.gov/agencies/lpc/lp/1978.pdf',
        count_source_label=LPC.format(1998), count_note='Recorded burials as of 1998.'),
}

REMOVE = {"A Cemetery for All God's Creatures|Staten Island"}  # a pet cemetery (Church of St. Andrew, est. 2004)

seen = set()
keep = []
for f in geo['features']:
    p = f['properties']
    key = f"{p['name']}|{p['borough']}"
    if key in REMOVE:
        seen.add(key); continue
    for table in (FOUNDED, STATUS, NEW_COUNTS):
        if key in table:
            seen.add(key)
            for k, v in table[key].items():
                if v is None: p.pop(k, None)
                else: p[k] = v
    if key in FOUNDED and p.get('founded_display') == str(p['founded']) and not p.get('founded_note') \
            and p['founded_source_label'] == "Meade's catalogue":
        for k in ('founded_display', 'founded_source_label', 'founded_source'): p.pop(k, None)
    keep.append(f)

missing = (set(FOUNDED) | set(STATUS) | set(NEW_COUNTS) | REMOVE) - seen
assert not missing, missing
geo['features'] = keep
json.dump(geo, open(f'{REPO}/data/cemeteries.geojson', 'w'), ensure_ascii=False, separators=(',', ':'))
print('features', len(keep))
