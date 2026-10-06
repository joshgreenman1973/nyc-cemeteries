"""Write methodology.html with every figure computed from the map's own data files."""
import json, collections, html

REPO = str(__import__('pathlib').Path(__file__).resolve().parents[2])
g = json.load(open(f'{REPO}/data/cemeteries.geojson'))
nob = json.load(open(f'{REPO}/data/notables.json'))
meade = json.load(open(f'{REPO}/data/meade_cemeteries.json'))
P = [f['properties'] for f in g['features']]
e = html.escape

st = collections.Counter(p['status'] for p in P)
n_sites = len(P)
n_founded = sum(1 for p in P if p.get('founded'))
counts = sorted([p for p in P if p.get('count')], key=lambda p: -p['count'])
n_counts = len(counts)
n_notable_cems = sum(1 for p in P if p.get('n_notables'))
n_notable_people = sum(p.get('n_notables') or 0 for p in P)
n_shipped = sum(len(v) for v in nob.values())
n_web = sum(1 for p in P if p.get('website'))
osm = [p for p in P if p['source'] == 'osm']
osm_matched = sum(1 for p in osm if p.get('meade_id'))
osm_unmatched = [p['name'] for p in osm if not p.get('meade_id')]
meade_on_map = sum(1 for p in P if p.get('meade_id'))
n_poly = sum(1 for f in g['features'] if f['geometry']['type'] != 'Point')
gw = next(p for p in P if p['name'] == 'Green-Wood Cemetery')['n_notables']

people = [p for p in counts if p['count_type'] == 'interments']
graves = [p for p in counts if p['count_type'] == 'graves']
tier = {t: [p for p in people if p['count_confidence'] == t] for t in ('high', 'medium', 'low')}
s = {t: sum(p['count'] for p in v) for t, v in tier.items()}
n = {t: len(v) for t, v in tier.items()}
graves_sum = sum(p['count'] for p in graves)
assert n_counts == len(people) + len(graves)

def fmt(x): return f'{x:,}'

WORDS = 'zero one two three four five six seven eight nine'.split()
def num(x): return WORDS[x] if x < 10 else fmt(x)

def approx(d):
    return ('about ' + d) if d[0].isdigit() and '+' not in d else d

rows = []
for p in counts:
    meas = 'graves' if p['count_type'] == 'graves' else 'people'
    note = e(p.get('count_note') or '')
    rows.append(f"<tr><td>{e(p['name'])}<span class=\"boro\">{e(p['borough'])}</span></td><td>{e(approx(p['count_display']))}</td>"
                f"<td>{meas}</td><td><a href=\"{e(p['count_source'])}\">{e(p['count_source_label'])}</a></td>"
                f"<td>{p['count_confidence']}</td><td>{note}</td></tr>")
count_table = '\n'.join(rows)

dep = []
for p in sorted(P, key=lambda p: p['name']):
    if p.get('founded_source_label') and p.get('founded_note'):
        dep.append(f"<li><strong>{e(p['name'])}</strong>, founding year {e(p['founded_display'])}: {e(p['founded_note'])} "
                   f"Source: <a href=\"{e(p['founded_source'])}\">{e(p['founded_source_label'])}</a>.</li>")
    if p.get('status_note'):
        dep.append(f"<li><strong>{e(p['name'])}</strong>, status: {e(p['status_note'])} "
                   f"Source: <a href=\"{e(p['status_source'])}\">{e(p['status_source_label'])}</a>.</li>")
dep_list = '\n'.join(dep)

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Methodology — The permanent residents</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
<style>
body {{ font-family: 'Source Sans 3', sans-serif; color: #1f2421; background: #f4f1e8; margin: 0; line-height: 1.55; }}
main {{ max-width: 860px; margin: 0 auto; padding: 40px 22px 80px; }}
h1 {{ font-family: 'Cormorant Garamond', serif; font-size: 34px; font-weight: 700; margin: 0 0 4px; }}
h2 {{ font-family: 'Cormorant Garamond', serif; font-size: 24px; font-weight: 600; margin: 34px 0 8px; border-bottom: 1px solid #c9c3b2; padding-bottom: 4px; }}
p, li {{ font-size: 15px; }}
a {{ color: #3d5743; }}
.back {{ font-size: 13px; letter-spacing: .07em; text-transform: uppercase; text-decoration: none; border: 1px solid #1f2421; padding: 5px 11px; color: #1f2421; display: inline-block; margin-bottom: 26px; }}
.back:hover {{ background: #1f2421; color: #f4f1e8; }}
code {{ background: #ebe6d8; padding: 1px 5px; font-size: 13px; }}
.tablewrap {{ overflow-x: auto; }}
table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
th, td {{ text-align: left; vertical-align: top; padding: 5px 8px 5px 0; border-bottom: 1px solid #ddd6c4; }}
th {{ font-size: 11px; text-transform: uppercase; letter-spacing: .06em; color: #6b675c; font-weight: 600; }}
td:nth-child(2) {{ white-space: nowrap; }}
.boro {{ display: block; color: #6b675c; font-size: 11.5px; }}
.totals td {{ font-size: 14px; }}
.totals td:last-child {{ text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }}
</style>
</head>
<body>
<main>
<a class="back" href="index.html">← Back to the map</a>
<h1>Methodology</h1>
<p>The permanent residents: a map of New York City's cemeteries. Built June 2026; corrected October 6, 2026, after a full fact-check (see <a href="#corrections">Corrections</a>).</p>

<h2>What this map shows</h2>
<p>{fmt(n_sites)} cemeteries, churchyards and burial grounds across the five boroughs, including ones that no longer physically exist. Each is labeled with a status: <strong>Active</strong> ({st['Active']}, still taking burials), <strong>Preserved</strong> ({st['Preserved']}, historic and still there but no longer taking burials) or <strong>No longer extant</strong> ({st['Obliterated']}, paved over, built upon or otherwise gone; Elizabeth Meade's term for these in her catalogue is "obliterated"). Founding years are shown for {n_founded} of them, documented burial counts for {n_counts} (each with its source named and linked, and a confidence label) and lists of notable people buried there for {n_notable_cems} ({fmt(n_notable_people)} people recorded in Wikidata). By default the map shows active and preserved cemeteries; toggle "No longer extant" to reveal the vanished ones.</p>
<p>Some burial grounds appear as more than one point. Meade's catalogue keeps separate records for a surviving part of a cemetery and a part that was destroyed (for instance where a street was cut through), and for separate parcels, and the map follows her records.</p>

<h2>Data sources</h2>
<ul>
<li><strong>The cemetery inventory, founding years and status:</strong> the <a href="https://www.cemeteriesofnyc.com/map">Cemeteries of New York City</a> catalogue by Elizabeth D. Meade, PhD, which she built for her doctoral dissertation in anthropology at the CUNY Graduate Center, <a href="https://academicworks.cuny.edu/gc_etds/3725">"Prepare for Death and Follow Me": An Archaeological Survey of the Historic Period Cemeteries of New York City</a> (2020). Through documentary research she identified 527 burial sites in the city and mapped each one. Her catalogue has {len(meade)} records, because some sites are split into parts; the map includes {meade_on_map} of them. Four that repeat a cemetery already shown were left off: destroyed edges of Washington, Cypress Hills and Mount Carmel cemeteries, and a second Cypress Hills parcel. Used here are her name, type, religion, status, founding, closing and obliteration years, notes, location-precision flag and per-site citations, which appear in each cemetery's detail panel. Her published map is an embedded Esri/ArcGIS web map; the underlying feature data was read from that map's public service. See her site for her full methodology and bibliography.</li>
<li><strong>Boundaries of cemeteries:</strong> OpenStreetMap, queried via the Overpass API (June 10, 2026) for features tagged <code>landuse=cemetery</code> or <code>amenity=grave_yard</code> and clipped to the borough boundaries published by the Department of City Planning. These supply the {n_poly} drawn outlines (plus {len(osm) - n_poly} OpenStreetMap points). Each was matched to its record in Meade's catalogue by name and location, and every match was checked by hand in October 2026. One, {e(', '.join(osm_unmatched))} on Staten Island, has no clear catalogue match, so its status comes from OpenStreetMap.</li>
<li><strong>Satellite imagery (optional toggle):</strong> Esri World Imagery (Maxar, Earthstar Geographics), shown only inside the cemetery outlines. Sites mapped as single points show nothing under the satellite view.</li>
<li><strong>Official websites:</strong> the cemetery's own or its operator's website, linked from the detail panel for {n_web} cemeteries. They come from Wikidata's official-website property (P856) and OpenStreetMap <code>website</code> tags, and every link was tested in October 2026.</li>
<li><strong>Notable burials:</strong> Wikidata's "place of burial" property (P119). Each person listed has a Wikidata entry recording burial at that cemetery. Lists are sorted by the number of Wikidata sitelinks (Wikipedia language editions plus other Wikimedia projects), a rough proxy for prominence. Birth and death years and one-line descriptions also come from Wikidata.</li>
<li><strong>Burial counts:</strong> assembled cemetery by cemetery from, in order of preference, the cemetery or its operator; government records (New York City Landmarks Preservation Commission designation reports, NYC Parks, the U.S. Department of Veterans Affairs); Wikipedia sentences that cite a reliable source; and researched secondary sources, chiefly the <a href="https://nycemetery.wordpress.com/">New York City Cemetery Project</a> by historian Mary French. Every count is listed with its source in the table below.</li>
</ul>

<h2 id="counts">Burial counts and their sources</h2>
<p>Each figure was checked against the source page or document linked here; none was estimated or extrapolated. Where a source gives a minimum ("more than," "over") the map says "more than"; where it gives an approximation the map keeps it ("about," "an estimated"). The stated number is used for sizing the map circles and for the totals below. The map prepends "about" to bare numbers, since none of these is an audited tally.</p>
<p><strong>Confidence labels.</strong> High: the cemetery or its operator, a government body, or a Wikipedia sentence that cites a reliable source. Medium: a single researched secondary source. Low: a figure whose own sourcing is weak, such as an uncited Wikipedia sentence, an advocacy group's estimate or a decades-old snapshot. "People" counts interments; "graves" counts graves or plots, which can hold more than one person.</p>
<div class="tablewrap"><table>
<thead><tr><th>Cemetery</th><th>Figure</th><th>Counts</th><th>Source</th><th>Confidence</th><th>Note</th></tr></thead>
<tbody>
{count_table}
</tbody></table></div>

<h2>Adding up the counts</h2>
<p>Taking only the figures that count people, each at its stated number:</p>
<div class="tablewrap"><table class="totals">
<tr><td>High-confidence sources ({n['high']} cemeteries)</td><td>{fmt(s['high'])}</td></tr>
<tr><td>Plus medium-confidence sources ({n['medium']} more)</td><td>{fmt(s['high'] + s['medium'])}</td></tr>
<tr><td>Plus low-confidence sources ({num(n['low'])} more)</td><td>{fmt(s['high'] + s['medium'] + s['low'])}</td></tr>
</table></div>
<p>The conservative figure is the middle one: about {round((s['high'] + s['medium']) / 1e5) / 10} million people buried in the {n['high'] + n['medium']} cemeteries with a reasonably sourced count. The {num(len(graves))} grave counts ({fmt(graves_sum)} graves) are left out, because a grave can hold more than one person. These totals are floors for a small share of the city's {fmt(n_sites)} sites, not a citywide count: most cemeteries publish no figure, several figures are years old, and Mokom Sholom's covers only one section. Calvary is counted at its operator's figure of 1.75 million rather than the widely repeated 3 million.</p>

<h2>Why most cemeteries have no count</h2>
<p>There is no central, authoritative dataset of how many people are buried in New York City's cemeteries. The New York State Division of Cemeteries asks cemetery corporations to report their "Number of Body Burials" for each year on their <a href="https://dos.ny.gov/annual-financial-report-cemetery-corporation-parts-1-3-printable">annual financial reports</a>, but these are yearly figures, not running totals, and we found no published dataset of them. The Diocese of Brooklyn's cemetery office publishes no totals; the Archdiocese of New York's cemetery arm gives figures for Calvary and Resurrection and a combined figure for its five cemeteries. The open-data portals (New York State's Public Cemetery Locations, NYC Open Data, the federal USGS gazetteer) carry locations only. Find A Grave's per-cemetery figures count volunteer-created memorials rather than actual interments, and its terms prohibit automated collection, so it is not used. Absence of a number on the map is not a claim that few people are buried there.</p>

<h2>Where the map departs from Meade's catalogue</h2>
<p>Founding years and statuses follow Meade's catalogue except in these cases, where a primary or better-documented source disagrees. Each is also explained in the cemetery's detail panel. Founding years otherwise keep Meade's qualifiers ("c. 1654," "1746 or 1751").</p>
<ul>
{dep_list}
</ul>

<h2>What "notable" means here</h2>
<ul>
<li>A person appears only if Wikidata records the cemetery as their place of burial. This undercounts reality everywhere: Green-Wood says it has 580,000 permanent residents, and the map lists {gw} of them.</li>
<li>Coverage is uneven across cemeteries and eras and reflects who gets a Wikipedia article. Cemeteries showing "no notable burials recorded" may simply be under-documented.</li>
<li>Trinity Church has three burial grounds in Manhattan, and Wikidata often records burials only at an umbrella "Trinity Church Cemetery" item. The map assigns those people to the churchyard at Broadway and Wall Street, St. Paul's Chapel or the uptown cemetery at 155th Street using Trinity's <a href="https://registers.trinitywallstreet.org/churchyard/">churchyard register</a>, its <a href="https://trinitychurchnyc.org/sites/default/files/2021-03/200617_cemetery_walking_tour_final.pdf">uptown walking-tour guide</a> and other documentation. People who could not be placed are left off. People Wikidata records at the uptown cemetery who died before it opened in 1842 are also left off, since no reinterment is documented for them.</li>
<li>Wikidata burial claims were spot-checked for the most prominent people at the largest cemeteries; claims contradicted by a reliable source were removed (see Corrections). Others were taken as recorded and may contain errors.</li>
<li>For cemeteries with more than 150 recorded notables, the map lists the 150 with the most sitelinks ({fmt(n_shipped)} people in all).</li>
</ul>

<h2>Known limitations</h2>
<ul>
<li>The map is only as complete as its inventories. Meade's catalogue is the most thorough public accounting of the city's burial grounds, but small family plots and undocumented grounds are certainly missing.</li>
<li>For destroyed and some preserved sites, the point marks an approximate location, not a boundary. Where Meade could not fix the exact site, the detail panel says the location is approximate.</li>
<li>Burial counts were published in different years, and active cemeteries keep growing.</li>
<li>Religion labels come from Meade's catalogue where it gives one, otherwise from OpenStreetMap tags, and are incomplete.</li>
</ul>

<h2>Reproducibility</h2>
<p>The raw inputs and intermediate files are in the project repository: the Overpass query and its output, the Meade catalogue extract (<code>data/meade_cemeteries.json</code>), Wikidata query results and Wikipedia infobox parses. The scripts that first processed them in June 2026 were not saved. The October 2026 corrections were made with scripts that are saved in <code>scripts/2026-10-fact-check/</code>. The map's data files are <code>data/cemeteries.geojson</code> and <code>data/notables.json</code>.</p>

<h2 id="corrections">Corrections</h2>
<p>October 6, 2026. A full fact-check of the map found and fixed these errors:</p>
<ul>
<li>47 entries duplicated a cemetery already on the map, usually once from OpenStreetMap and once from Meade's catalogue, often with conflicting statuses (Chatham Square's Shearith Israel cemetery, for one, was shown as both active and preserved). The duplicates were merged, the total fell from 594 to {fmt(n_sites)} and the active count from 126 to {st['Active']}. Union Field and New Union Field cemeteries had been matched to each other's records.</li>
<li>Three catalogue sites at the water's edge had been dropped by the borough clipping and were restored: the Wallabout Bay prison-ship burials, the Swinburne Island crematorium and the Lawrence family plot at College Point. A pet cemetery at the Church of St. Andrew on Staten Island was removed.</li>
<li>Burial counts corrected to the cemeteries' own or official figures: Calvary (about 3 million to more than 1.75 million), Mount Carmel (85,000 plots to 135,000 people), Mount Hebron (220,000 to 217,000), Woodlawn (300,000 to 310,000), the Evergreens (526,000 to 538,000), Moore-Jackson (48 to at least 51 graves). Saint Raymond's figure of half a million was a capacity, not a count, and was removed. Flushing's 41,000 is now labeled as a 1951 figure. New Utrecht's count of about 1,300 was added. Several confidence labels were lowered where the source turned out to be uncited.</li>
<li>Founding years corrected for Saint Raymond's (1954, the new section, to 1875), Bayside, Moravian, Old Gravesend, Lawrence (Astoria), Hart Island, First Shearith Israel, Mount Judah and Salem Fields; Calvary's (1848) was added. New York City Marble Cemetery, which still takes family interments, is now shown as active.</li>
<li>Of 77 people listed at the uptown Trinity Church Cemetery, 38 are buried at Trinity's churchyard at Broadway and Wall Street and one at St. Paul's Chapel, and they were moved there; 27 who could not be placed with confidence, or who are buried elsewhere, were removed. The uptown cemetery's own notables (John James Audubon, Ralph Ellison, Ed Koch and others) were added. Margaret Sanger (buried in Fishkill, N.Y.), Albert Fish (Sing Sing) and William Livingston (moved to Green-Wood in 1844) were removed from cemeteries where they are not buried, and Laurie Bird, recorded at two cemeteries, from both. Four misspelled names were fixed, including Lucky Luciano and Phoebe Cary.</li>
<li>Broken or redirected website links were fixed; the Flatbush African Burial Ground link had begun redirecting to an unrelated site and was removed.</li>
<li>The methodology had misstated what is published about Catholic cemetery totals and the state's burial reports, Wikidata's coverage of Green-Wood and the availability of the pipeline scripts, and has been corrected.</li>
</ul>
</main>
</body>
</html>
"""
open(f'{REPO}/methodology.html', 'w').write(page)
print('written', len(page))
print(dict(n_sites=n_sites, st=dict(st), n_founded=n_founded, n_counts=n_counts, n_notable_cems=n_notable_cems,
           n_notable_people=n_notable_people, n_shipped=n_shipped, n_web=n_web, osm=len(osm), osm_matched=osm_matched,
           meade_on_map=meade_on_map, gw=gw, tiers=s, n=n, graves=graves_sum))
