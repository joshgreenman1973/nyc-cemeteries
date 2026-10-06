"""Re-sort Trinity's notable burials among its three Manhattan burial grounds and drop
burials contradicted by sources.

Wikidata item Q7842673 ("Trinity Church Cemetery") is an umbrella for three places; the map
had pinned all 77 of its people to the uptown cemetery. Placements below follow Trinity's own
churchyard register (registers.trinitywallstreet.org), Trinity's uptown walking-tour guide,
Political Graveyard and the people's Wikipedia articles.
"""
import json

REPO = str(__import__('pathlib').Path(__file__).resolve().parents[2])
SP = str(__import__('pathlib').Path(__file__).resolve().parent)
geo = json.load(open(f'{REPO}/data/cemeteries.geojson'))
nob = json.load(open(f'{REPO}/data/notables.json'))
wd = json.load(open(f'{SP}/trinity_wikidata.json'))

UPTOWN_FROM_UMBRELLA = ['John Jacob Astor I', 'Caroline Webster Schermerhorn Astor', 'William Backhouse Astor, Jr.',
    'John Jacob Astor IV', 'Madeleine Astor', 'Eliza Jumel', 'Jerry Orbach', 'John Jacob Astor III',
    'William A. Chanler', 'William Backhouse Astor, Sr.', 'Rita de Acosta Lydig']
DOWNTOWN_FROM_UMBRELLA = ['Robert Fulton', 'Albert Gallatin', 'Elizabeth Schuyler Hamilton', 'Angelica Schuyler Church',
    'Philip Hamilton', 'Francis Lewis', 'William Bradford', 'James Lawrence', 'Hugh Williamson', 'John Morin Scott',
    'Franklin Wharton', 'Richard Morris', 'Elias Neau', 'John Watts Jr.', 'Mary Alexander', 'Sarah Livingston',
    'John Duer', 'Nathaniel Marston', 'Phebe Taylor Winthrop', 'Sarah Cornell Clarkson', 'Edward William Laight', 'Bache McEvers',
    'John W. Mulligan', 'Samuel Swartwout', 'John J. Morgan', 'William Bayard Jr.', 'James Nicholson', 'John Lamb',
    'Frederic James de Peyster', 'John Sloss Hobart', 'Thomas J. Oakley', 'John Alsop', 'Aaron Hackley',
    'Robert Swartwout', 'James Gordon', 'John R. Fellows', 'Charles L. Livingston', 'John Ward']
ST_PAULS_FROM_UMBRELLA = ['Stephen Rochefontaine']
# Wikidata's churchyard item: drop those buried elsewhere or contested; Morgan Dix is uptown (Trinity walking tour)
CHURCHYARD_DROP = {'William Livingston',      # reinterred at Green-Wood, 1844
                   'John Watts de Peyster',   # family vault, St. Paul's Church, Tivoli, N.Y.
                   'Luther Martin'}           # sources conflict (Trinity vs. St. John's burying ground)
MOVE_UPTOWN = {'Morgan Dix'}
# Contradicted elsewhere: (cemetery QID, name)
DROP = [('Q239043', 'Margaret Sanger'),        # buried in Fishkill, N.Y.
        ('Q2972524', 'Albert Fish'),           # buried in Sing Sing Prison Cemetery per his Wikipedia article
        ('Q2972524', 'Laurie Bird'),           # recorded at two cemeteries; unresolved
        ('Q113307925', 'Laurie Bird')]

def fmt(z):
    return {'n': z['n'], 'd': z['d'], 'b': z['b'], 'x': z['x'], 'w': z['w'], 'l': z['l']}

def labeled(z):
    return not (z['n'].startswith('Q') and z['n'][1:].isdigit())

umb = {x['n']: x for x in nob['Q7842673']}
def take(names):
    missing = [n for n in names if n not in umb]
    assert not missing, missing
    return [umb[n] for n in names]

uptown = [fmt(z) for z in wd['Q42720261'] if labeled(z) and not (z['x'] and int(z['x']) < 1842)]
churchyard_wd = [fmt(z) for z in wd['Q42720227'] if labeled(z)]
moved = [z for z in churchyard_wd if z['n'] in MOVE_UPTOWN]
assert len(moved) == len(MOVE_UPTOWN)
churchyard = [z for z in churchyard_wd if z['n'] not in CHURCHYARD_DROP | MOVE_UPTOWN]
assert len(churchyard_wd) - len(churchyard) == len(CHURCHYARD_DROP | MOVE_UPTOWN)
st_pauls = [fmt(z) for z in wd['Q42720282'] if labeled(z)]

def merge(base, extra):
    names = {z['n'] for z in base}
    out = base + [z for z in extra if z['n'] not in names]
    return sorted(out, key=lambda z: -z['l'])

new = {
    'Q42720261': merge(uptown + moved, take(UPTOWN_FROM_UMBRELLA)),
    'Q42720227': merge(churchyard, take(DOWNTOWN_FROM_UMBRELLA)),
    'Q42720282': merge(st_pauls, take(ST_PAULS_FROM_UMBRELLA)),
}
del nob['Q7842673']
nob.update(new)

dropped = 0
for q, name in DROP:
    before = len(nob[q])
    nob[q] = [x for x in nob[q] if x['n'] != name]
    assert len(nob[q]) == before - 1, (q, name)
    dropped += 1

# point map features at the right items and refresh their notable counts
qmap = {'Trinity Cemetery|Manhattan': 'Q42720261', 'Trinity Churchyard|Manhattan': 'Q42720227',
        "St. Paul's Churchyard|Manhattan": 'Q42720282'}
hit = set()
for f in geo['features']:
    p = f['properties']
    key = f"{p['name']}|{p['borough']}"
    if key in qmap:
        p['wikidata'] = qmap[key]; p['n_notables'] = len(nob[qmap[key]]); hit.add(key)
    for q, name in DROP:
        if p.get('wikidata') == q:
            p['n_notables'] -= 1
assert hit == set(qmap), set(qmap) - hit

json.dump(nob, open(f'{REPO}/data/notables.json', 'w'), ensure_ascii=False, separators=(',', ':'))
json.dump(geo, open(f'{REPO}/data/cemeteries.geojson', 'w'), ensure_ascii=False, separators=(',', ':'))
for q, v in new.items():
    print(q, len(v), [z['n'] for z in v[:8]])
print('dropped', dropped)
