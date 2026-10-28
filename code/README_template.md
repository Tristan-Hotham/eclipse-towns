# When did your town last see a total eclipse?

Every total and annular solar eclipse whose central shadow crossed Britain, Ireland, the Isle of Man or the Channel Islands between AD 1000 and 2200, computed from first principles and tested at {{places.n|int}} cities, towns and villages and on a 4 km grid. Search any place for its last and next total eclipse.

**Interactive version:** https://tristan-hotham.github.io/eclipse-towns/

This repository holds the interactive page, derived data and the analysis code for the data study *When did your town last see a total eclipse? Every path of totality over Britain and Ireland, AD 1000 to 2200* by Dr Tristan Hotham (Independent researcher, ORCID 0000-0003-4931-9349). Paper and archived release: https://doi.org/10.5281/zenodo.23729635

## Headline results

{{README_HEADLINES}}

## Files

- `index.html`: the interactive page (Leaflet map of every path with a century slider, place search, charts, tables). It fetches `data/places_page.json` for the search and `img/count.png` and `img/last.png` for the optional map shading.
- `header.png`: social card.
- `data/eclipses.csv`: one row per eclipse in the window whose total or annular shadow touched the study area: date (Julian calendar before 15 October 1582, Gregorian after), the date in the British calendar (Julian until 1752), peak hour (UT), global type, type over the study area (total, annular or hybrid), land area inside the path (km², 4 km grid), land area in Great Britain and in Ireland, number of places and of cities and towns in totality or annularity, the longest central phase at a listed place and where, and the Delta T used.
- `data/eclipses_all.csv`: every solar eclipse of AD 1000 to 2200 with its global type and peak, from Astronomy Engine.
- `data/places.csv`: the {{places.n|int}} places with, for each, the number of total and annular eclipses from 1000 to 2200, the last total before 28 October 2026 and its duration, the next total and its duration, the last and next annular, the longest gap between totals, and every central eclipse with its duration in seconds.
- `data/grid.csv`: the land cells of the 0.04 by 0.06 degree grid with the number of totals and annulars and the last and next total.
- `data/paths.geojson`: the path of each eclipse over the study area (filled outline of the central shadow with the Sun up) and its centre line.
- `data/validation.csv`: computed results against published statements about named places.
- `data/deltat.csv`: the Delta T sensitivity test.
- `data/places_in.csv`: the input place list. `data/page_data.json` and `data/places_page.json`: compact data for the page.
- `data/results.json`: every number quoted on the page, in the paper, the blog post and the collage.
- `img/`: map shading for the page.
- `code/`: Python scripts, run in order: `00_places.py` (place list), `01_eclipses.py` (all eclipses, screening, grid and place scans; `eclib.py` holds the geometry), `02_deltat.py` (Delta T test), `03_analysis.py` (tables, paths, results), `04_build_site.py` (page and README, with `prose.py`), `05_figures.py` (paper and blog figures), `06_header.py` (social card), `07_paper.py` (paper PDF via xelatex), `08_release.py` (blog post and Zenodo files).
- `release/`: paper PDF and LaTeX source, blog post and figures, Zenodo files. `reddit/`: collage and post text.

## Method in brief

{{README_METHOD}}

## How to rerun

Python 3 with numpy, scipy, shapely, contourpy, matplotlib, Pillow and astronomy-engine (`pip install astronomy-engine`; Playwright for the header, xelatex for the paper). From `code/`: `python3 00_places.py && python3 01_eclipses.py && python3 02_deltat.py && python3 03_analysis.py && python3 04_build_site.py`. Step 1 takes about 45 minutes on two cores. Inputs read from one folder up and not included: `osnames_gb.tsv` (OS Open Names), `_data2/geonames/cities1000.txt` (GeoNames) and the Natural Earth land outline used by the lighthouse study (`did-lighthouses-work/release/build/ne10m_land_british_isles.json`).

## Sources and licence

- Eclipse geometry: Astronomy Engine by Don Cross, https://github.com/cosinekitty/astronomy (MIT licence), version 2.1.19, with its default Delta T model: the polynomial expressions of Espenak and Meeus used in the NASA Five Millennium Canon of Solar Eclipses (Espenak, F. and Meeus, J. (2006) NASA Technical Publication TP-2006-214141).
- Places in Great Britain: OS Open Names, Ordnance Survey, Open Government Licence v3.0. Contains OS data © Crown copyright and database right 2026.
- Places in Ireland, Northern Ireland, the Isle of Man and the Channel Islands: GeoNames, cities1000 (https://www.geonames.org/, CC BY 4.0).
- Coastline: Natural Earth 1:10m land (public domain).
- History and published checks: English Wikipedia (CC BY-SA 4.0): List of solar eclipses visible from the British Isles; Solar eclipse of August 2, 1133; Solar eclipse of May 3, 1715; Solar eclipse of May 22, 1724; Solar eclipse of June 29, 1927; Solar eclipse of August 11, 1999; Solar eclipse of September 23, 2090; Solar eclipse of August 21, 2017; ΔT (timekeeping). Only facts and short quotations are used.
- Base map tiles on the page: Esri. Map library: Leaflet.

The derived data and the page text are released under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/); please credit OS Open Names and GeoNames as above when reusing the place data. Code is MIT (see `LICENSE`).

Companion studies: [Within sight](https://tristan-hotham.github.io/within-sight/) and [Is Domesday destiny?](https://tristan-hotham.github.io/domesday-destiny/). Blog: https://blog.tristanhotham.com/

## Citation

Hotham, T. (2026) *When did your town last see a total eclipse? Every path of totality over Britain and Ireland, AD 1000 to 2200*. Zenodo. https://doi.org/10.5281/zenodo.23729635

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
