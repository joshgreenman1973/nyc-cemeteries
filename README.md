# The permanent residents — a map of New York City's cemeteries

An interactive map of every named cemetery, churchyard and burial ground in the five boroughs that is mapped in OpenStreetMap: 111 sites, with documented burial counts for 33 of them (each linked to its source and labeled with a confidence level) and Wikidata-recorded notable burials for 44 of them (about 2,800 people).

- `index.html` — the map (Leaflet, no build step)
- `methodology.html` — full data sources, assumptions and limitations
- `data/cemeteries.geojson` — cemetery boundaries and attributes used by the map
- `data/notables.json` — notable burials keyed by the cemetery's Wikidata ID
- Other files in `data/` are preserved intermediates from the pipeline (raw Overpass output, raw burial query results, Wikipedia infobox parses)

Built June 2026. Sources: OpenStreetMap (locations), Wikidata (notable burials), cemetery websites / Wikipedia / the New York City Cemetery Project (burial counts). See `methodology.html` for details.
