"""Sum of published burial figures, computed from the live map data.

The result is an incomplete, mixed-date sum of published figures, some approximate; it is not an
audited citywide count or a lower bound.

Rules: count only figures that measure people (count_type == 'interments'); graves or plots and
gravestone/marker counts are listed separately and never added in;
use the stated number of every figure ("more than 1.75 million" -> 1,750,000);
report each confidence tier separately so the weakly sourced figures are visible.
Writes a TSV for an independent awk re-sum.
"""
import json, sys
REPO = str(__import__('pathlib').Path(__file__).resolve().parents[2])
OUT = sys.argv[1]
g = json.load(open(f'{REPO}/data/cemeteries.geojson'))
rows = [f['properties'] for f in g['features'] if f['properties'].get('count')]
rows.sort(key=lambda p: -p['count'])

tiers = {'high': [], 'medium': [], 'low': []}
graves, markers = [], []
for p in rows:
    if p['count_type'] == 'interments':
        tiers[p['count_confidence']].append(p)
    elif p['count_type'] == 'graves':
        graves.append(p)
    elif p['count_type'] == 'markers':
        markers.append(p)
    else:
        raise ValueError(f"unknown count_type for {p['name']}: {p['count_type']}")

with open(OUT, 'w') as fh:
    for t in ('high', 'medium', 'low'):
        for p in tiers[t]:
            fh.write(f"{t}\tinterments\t{p['count']}\t{p['name']}\n")
    for p in graves:
        fh.write(f"{p['count_confidence']}\tgraves\t{p['count']}\t{p['name']}\n")
    for p in markers:
        fh.write(f"{p['count_confidence']}\tmarkers\t{p['count']}\t{p['name']}\n")

total = 0
for t in ('high', 'medium', 'low'):
    s = sum(p['count'] for p in tiers[t])
    print(f'\n{t.upper()} ({len(tiers[t])} cemeteries): {s:,}')
    for p in tiers[t]:
        print(f"   {p['count']:>11,}  {p['name']}  [{p['count_display']}; {p['count_source_label']}]")
print('\nGRAVES (not people; excluded):')
for p in graves:
    print(f"   {p['count']:>11,}  {p['name']}  [{p['count_display']}]")
print('\nGRAVESTONES AND MARKERS (not people; excluded):')
for p in markers:
    print(f"   {p['count']:>11,}  {p['name']}  [{p['count_display']}, {p.get('count_year')} survey]")
h = sum(p['count'] for p in tiers['high']); m = sum(p['count'] for p in tiers['medium']); l = sum(p['count'] for p in tiers['low'])
print(f'\nhigh only:            {h:,}')
print(f'high + medium:        {h + m:,}')
print(f'high + medium + low:  {h + m + l:,}')
