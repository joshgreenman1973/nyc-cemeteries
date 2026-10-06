"""Conservative burial total, computed from the live map data.

Rules: count only figures that measure people (interments), not graves or plots;
use the low end of every figure ("more than 1.75 million" -> 1,750,000);
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
graves = []
for p in rows:
    (graves if p['count_type'] == 'graves' else tiers[p['count_confidence']]).append(p)

with open(OUT, 'w') as fh:
    for t in ('high', 'medium', 'low'):
        for p in tiers[t]:
            fh.write(f"{t}\tinterments\t{p['count']}\t{p['name']}\n")
    for p in graves:
        fh.write(f"{p['count_confidence']}\tgraves\t{p['count']}\t{p['name']}\n")

total = 0
for t in ('high', 'medium', 'low'):
    s = sum(p['count'] for p in tiers[t])
    print(f'\n{t.upper()} ({len(tiers[t])} cemeteries): {s:,}')
    for p in tiers[t]:
        print(f"   {p['count']:>11,}  {p['name']}  [{p['count_display']}; {p['count_source_label']}]")
print('\nGRAVES (not people; excluded):')
for p in graves:
    print(f"   {p['count']:>11,}  {p['name']}  [{p['count_display']}]")
h = sum(p['count'] for p in tiers['high']); m = sum(p['count'] for p in tiers['medium']); l = sum(p['count'] for p in tiers['low'])
print(f'\nhigh only:            {h:,}')
print(f'high + medium:        {h + m:,}')
print(f'high + medium + low:  {h + m + l:,}')
