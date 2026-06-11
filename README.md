# The permanent residents — a map of New York City's cemeteries

An interactive map of 594 cemeteries, churchyards and burial grounds across the five boroughs — active, preserved and obliterated — with founding years, status, documented burial counts for 40 (each linked to its source and labeled with a confidence level) and Wikidata-recorded notable burials for 44 (about 2,800 people).

Inventory, founding years and status come from Elizabeth D. Meade's [Cemeteries of New York City](https://www.cemeteriesofnyc.com/map) catalogue; drawn boundaries of active cemeteries come from OpenStreetMap; notable burials from Wikidata; burial counts assembled and source-verified one by one.

- `index.html` — the map (Leaflet, no build step)
- `methodology.html` — full data sources, assumptions and limitations
- `data/cemeteries.geojson` — cemetery boundaries and attributes used by the map
- `data/notables.json` — notable burials keyed by the cemetery's Wikidata ID
- Other files in `data/` are preserved intermediates from the pipeline (raw Overpass output, raw burial query results, Wikipedia infobox parses)

Built June 2026. Sources: OpenStreetMap (locations), Wikidata (notable burials), cemetery websites / Wikipedia / the New York City Cemetery Project (burial counts). See `methodology.html` for details.
