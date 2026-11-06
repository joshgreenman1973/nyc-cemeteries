# The permanent residents — a map of New York City's cemeteries

An interactive map of 549 cemeteries, churchyards and burial grounds across the five boroughs — active, preserved and no longer extant — with founding years, status, documented counts for 40 (35 of people, four of graves and one of gravestones and markers; each with its source named and linked, a source type and a confidence label) and Wikidata-recorded notable burials for 45.

Inventory, founding years and status come from Elizabeth D. Meade's [Cemeteries of New York City](https://www.cemeteriesofnyc.com/map) catalogue; drawn boundaries come from OpenStreetMap; notable burials from Wikidata; burial counts were assembled and checked one by one against cemetery websites, city landmark reports and other published sources.

- `index.html` — the map (Leaflet, no build step)
- `methodology.html` — data sources, every burial count with its source, the totals, departures from Meade's catalogue, limitations and corrections
- `data/cemeteries.geojson` — cemetery boundaries and attributes used by the map
- `data/notables.json` — notable burials keyed by the cemetery's Wikidata ID
- `scripts/2026-10-fact-check/` — the scripts and source files used for the October 2026 corrections; `5_build_methodology.py` writes the methodology page from the data
- `scripts/2026-11-fact-check/` — the November 2026 data changes (marker counts, source types, archived link)
- `data/meade_webmap.json` — the full web map behind Meade's catalogue, including the footprint she mapped for each site and her reinterment records
- Other files in `data/` are preserved intermediates from the June 2026 build (raw Overpass output, the Meade catalogue extract, raw burial query results, Wikipedia infobox parses). The scripts that produced them were not saved.

Built June 2026; corrected October 6, 2026, after a full fact-check, and November 6, 2026, after a follow-up review. See `methodology.html` for details.
