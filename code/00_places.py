"""Step 0. Build the list of places to test (data/places.csv).

Great Britain: every OS Open Names populated place of local type City, Town or Village
(OS Open Names, Ordnance Survey, Open Government Licence v3.0).
Ireland, Northern Ireland, the Isle of Man and the Channel Islands (not in OS Open Names):
GeoNames cities1000 (places of 1,000 people or more, CC BY 4.0).
Inputs are read in place, one folder above the project:
  ../../osnames_gb.tsv  and  ../../_data2/geonames/cities1000.txt
Run: python3 00_places.py
"""
import csv, os

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
OSN = os.path.join(ROOT, "..", "osnames_gb.tsv")
GEO = os.path.join(ROOT, "..", "_data2", "geonames", "cities1000.txt")

rows = []
with open(OSN, encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        if r["type"] != "populatedPlace" or r["local_type"] not in ("City", "Town", "Village"):
            continue
        area = r["county"] or r["district"] or r["region"]
        rows.append(dict(name=r["name1"], alt=r["name2"], kind=r["local_type"].lower(), area=area,
                         country=r["country"], lat=float(r["lat"]), lon=float(r["lon"]), pop="", source="OS Open Names"))

CC = {"IE": "Ireland", "IM": "Isle of Man", "JE": "Jersey", "GG": "Guernsey"}
with open(GEO, encoding="utf-8") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        cc, a1 = p[8], p[10]
        if cc in CC or (cc == "GB" and a1 == "NIR"):
            country = "Northern Ireland" if cc == "GB" else CC[cc]
            pop = int(p[14] or 0)
            kind = "city" if pop >= 100000 else ("town" if pop >= 1500 else "village")
            rows.append(dict(name=p[1], alt="", kind=kind, area=country, country=country,
                             lat=round(float(p[4]), 5), lon=round(float(p[5]), 5), pop=pop, source="GeoNames"))

# drop exact duplicate name+area entries closer than 1 km (OS lists a few places twice)
seen = {}; out = []
for r in rows:
    k = (r["name"], r["area"]); q = seen.get(k)
    if q and abs(q["lat"] - r["lat"]) < 0.01 and abs(q["lon"] - r["lon"]) < 0.015:
        continue
    seen[k] = r; out.append(r)
for i, r in enumerate(out):
    r["pid"] = i
cols = ["pid", "name", "alt", "kind", "area", "country", "lat", "lon", "pop", "source"]
with open(os.path.join(ROOT, "data", "places_in.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); [w.writerow({c: r[c] for c in cols}) for r in out]
from collections import Counter
print(len(out), Counter(r["country"] for r in out), Counter(r["kind"] for r in out))
