"""Step 3. Turn the eclipse scans into tables, paths and every number used in the outputs.

Inputs: data/eclipses_all.csv, data/places_in.csv, work/place_hits.csv, work/grid_*.npz (step 1),
data/deltat.csv (step 2), and the Natural Earth 1:10m land outline for the
British Isles as extracted for the lighthouse project (../../did-lighthouses-work/release/build/).
Outputs: data/eclipses.csv, data/places.csv, data/grid.csv, data/paths.geojson, data/validation.csv,
data/page_data.json, data/results.json, overlay images for the page (img/*.png).
Run: python3 03_analysis.py
"""
import csv, glob, json, math, os
from collections import Counter, defaultdict
import numpy as np
import contourpy
import eclib
import shapely
from shapely.geometry import shape, Polygon, MultiPolygon, mapping
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
D = lambda *p: os.path.join(ROOT, "data", *p)
WORK = os.path.join(ROOT, "work")
TODAY = "2026-10-28"; Y0, Y1 = 1000, 2200
GLAT = np.round(np.arange(49.0, 61.0 + 1e-9, 0.04), 4); GLON = np.round(np.arange(-11.0, 2.0 + 1e-9, 0.06), 4)
LA, LO = np.meshgrid(GLAT, GLON, indexing="ij")
R = {}

# ---------- land mask (Britain, Ireland, Man, Channel Islands; France and the Low Countries removed) ----------
COAST = os.path.join(ROOT, "..", "did-lighthouses-work", "release", "build", "ne10m_land_british_isles.json")
parts = []
for g in json.load(open(COAST)):
    for p in shape(g).geoms:
        x0, y0, x1, y1 = p.bounds
        if (x0 > -2.0 and y0 <= 49.01 and p.area > 1) or x0 > 3.0 or y0 > 61.0:
            continue
        parts.append(p)
LAND = unary_union(parts); shapely.prepare(LAND)
land = shapely.contains_xy(LAND, LO, LA)
ISL = sorted(parts, key=lambda p: -p.area)
GB, IE = ISL[0], ISL[1]
shapely.prepare(GB); shapely.prepare(IE)
cell_km2 = (0.04 * 111.32) * (0.06 * 111.32 * np.cos(np.radians(LA)))
R["grid"] = dict(cells=int(land.sum()), cell_lat_deg=0.04, cell_lon_deg=0.06, land_km2=float((cell_km2 * land).sum()))

# ---------- eclipses ----------
allx = list(csv.DictReader(open(D("eclipses_all.csv"))))
R["global"] = dict(n=len(allx), **{k: sum(1 for e in allx if e["global_kind"] == k) for k in ("total", "annular", "partial")})
R["global"]["hybrid_or_other"] = R["global"]["n"] - R["global"]["total"] - R["global"]["annular"] - R["global"]["partial"]
EX = {e["date"]: e for e in allx}
places = list(csv.DictReader(open(D("places_in.csv"), encoding="utf-8")))
for p in places:
    p["lat"] = float(p["lat"]); p["lon"] = float(p["lon"])
hits = defaultdict(list)
for h in csv.DictReader(open(os.path.join(WORK, "place_hits.csv"))):
    hits[h["eclipse"]].append((int(h["pid"]), int(h["kind"]), float(h["dur_s"])))

ecl = []
grids = {}
for f in sorted(glob.glob(os.path.join(WORK, "grid_[0-9]*.npz"))):
    eid = os.path.basename(f)[5:-4]
    z = np.load(f); grids[eid] = dict(gmin=z["gmin"], dur=z["dur"], kind=z["kind"])

cities = {}
for e_id, g in grids.items():
    kd = g["kind"]; cen = kd != 0
    tl = cen & land & (kd == 1); al = cen & land & (kd == -1)
    ph = hits.get(e_id, [])
    pt = [h for h in ph if h[1] == 1]; pa = [h for h in ph if h[1] == -1]
    land_any = bool(tl.any() or al.any() or ph)
    if tl.any() or pt:
        rk = "hybrid" if (al.any() or pa) else "total"
    else:
        rk = "annular"
    # longest central phase on land and the nearest listed place to it
    best = None
    if ph:
        pid, k, d = max(ph, key=lambda h: h[2]); best = (d, places[pid]["name"], places[pid]["area"])
    ex = EX[e_id]
    y = int(e_id[:4])
    ecl.append(dict(eclipse=e_id, brit_date=ex["brit_date"], year=y, peak_hour_ut=ex["peak_hour_ut"], global_kind=ex["global_kind"],
                    regional_kind=rk, on_land=int(land_any), total_land_km2=round(float((cell_km2 * tl).sum())),
                    annular_land_km2=round(float((cell_km2 * al).sum())),
                    gb_km2=round(float((cell_km2 * (tl | al) * shapely.contains_xy(GB, LO, LA)).sum())),
                    ireland_km2=round(float((cell_km2 * (tl | al) * shapely.contains_xy(IE, LO, LA)).sum())),
                    places_total=len(pt), places_annular=len(pa),
                    towns_total=sum(1 for h in pt if places[h[0]]["kind"] in ("town", "city")),
                    towns_annular=sum(1 for h in pa if places[h[0]]["kind"] in ("town", "city")),
                    max_dur_s=round(best[0]) if best else 0, max_dur_place=f"{best[1]}, {best[2]}" if best else "",
                    max_dur_land_s=round(max(float((g["dur"] * land).max()), best[0] if best else 0)),
                    delta_t_s=ex["delta_t_s"]))
ecl.sort(key=lambda e: e["eclipse"])
with open(D("eclipses.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(ecl[0])); w.writeheader(); w.writerows(ecl)
EL = [e for e in ecl if e["on_land"]]
R["eclipses"] = dict(touching_region=len(ecl), on_land=len(EL),
                     total=sum(1 for e in EL if e["regional_kind"] == "total"),
                     annular=sum(1 for e in EL if e["regional_kind"] == "annular"),
                     hybrid=sum(1 for e in EL if e["regional_kind"] == "hybrid"),
                     sea_only=[e["eclipse"] for e in ecl if not e["on_land"]])
TOT = [e for e in EL if e["regional_kind"] in ("total", "hybrid") and (e["places_total"] > 0 or e["total_land_km2"] > 0)]
R["eclipses"]["with_totality_on_land"] = len(TOT)
R["eclipses"]["total_before_today"] = sum(1 for e in TOT if e["eclipse"] < TODAY)
R["eclipses"]["total_after_today"] = sum(1 for e in TOT if e["eclipse"] > TODAY)
cent = Counter((e["year"] - 1) // 100 + 1 for e in TOT)
R["by_century"] = [dict(century=c, totals=cent.get(c, 0), annulars=sum(1 for e in EL if (e["year"] - 1) // 100 + 1 == c and e["regional_kind"] == "annular"))
                   for c in range(11, 23)]
big = sorted(TOT, key=lambda e: -e["total_land_km2"])
R["biggest"] = [dict(eclipse=e["eclipse"], km2=e["total_land_km2"], towns=e["towns_total"], places=e["places_total"]) for e in big[:8]]
R["most_towns"] = max(TOT, key=lambda e: e["towns_total"])["eclipse"]
gaps = [(int(b["year"]) - int(a["year"]), a["eclipse"], b["eclipse"]) for a, b in zip(TOT, TOT[1:])]
R["region_gap_max"] = dict(zip(("years", "from", "to"), max(gaps)))
R["region_gap_mean"] = round(float(np.mean([g[0] for g in gaps])), 1)

# ---------- per place ----------
PH = defaultdict(list)
for e_id, hs in hits.items():
    for pid, k, d in hs:
        PH[pid].append((e_id, k, d))
prow = []
for p in places:
    hs = sorted(PH.get(int(p["pid"]), []))
    tots = [h for h in hs if h[1] == 1]; ann = [h for h in hs if h[1] == -1]
    last = [h for h in tots if h[0] < TODAY]; nxt = [h for h in tots if h[0] > TODAY]
    ys = [int(h[0][:4]) for h in tots]
    gp = [b - a for a, b in zip(ys, ys[1:])]
    prow.append(dict(pid=p["pid"], name=p["name"], alt=p["alt"], kind=p["kind"], area=p["area"], country=p["country"],
                     lat=p["lat"], lon=p["lon"], source=p["source"], n_total=len(tots), n_annular=len(ann),
                     last_total=last[-1][0] if last else "", last_total_dur_s=round(last[-1][2]) if last else "",
                     next_total=nxt[0][0] if nxt else "", next_total_dur_s=round(nxt[0][2]) if nxt else "",
                     last_annular=([h for h in ann if h[0] < TODAY] or [("",)])[-1][0],
                     next_annular=([h for h in ann if h[0] > TODAY] or [("",)])[0][0],
                     longest_gap_years=max(gp) if gp else "",
                     totals=";".join(f"{h[0]}:{round(h[2])}" for h in tots), annulars=";".join(f"{h[0]}:{round(h[2])}" for h in ann)))
with open(D("places.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(prow[0])); w.writeheader(); w.writerows(prow)
towns = [p for p in prow if p["kind"] in ("town", "city")]
R["places"] = dict(n=len(prow), towns=len(towns), villages=len(prow) - len(towns),
                   gb=sum(1 for p in prow if p["source"] == "OS Open Names"), other=sum(1 for p in prow if p["source"] == "GeoNames"))
def share(rows, f): return sum(1 for p in rows if f(p)) / len(rows)
R["towns"] = dict(
    n=len(towns),
    never_window=sum(1 for p in towns if p["n_total"] == 0), never_window_share=share(towns, lambda p: p["n_total"] == 0),
    none_since_1000=sum(1 for p in towns if not p["last_total"]), none_since_1000_share=share(towns, lambda p: not p["last_total"]),
    none_until_2200=sum(1 for p in towns if not p["next_total"]), none_until_2200_share=share(towns, lambda p: not p["next_total"]),
    since_1900=sum(1 for p in towns if p["last_total"] and p["last_total"] >= "1900"),
    next_2090=sum(1 for p in towns if p["next_total"].startswith("2090")),
    mean_n=float(np.mean([p["n_total"] for p in towns])),
    max_n=max(p["n_total"] for p in towns),
    max_n_places=[f"{p['name']}" for p in towns if p["n_total"] == max(q["n_total"] for q in towns)][:12],
    dist={str(k): v for k, v in sorted(Counter(p["n_total"] for p in towns).items())})
lastc = Counter((int(p["last_total"][:4]) - 1) // 100 + 1 if p["last_total"] else 0 for p in towns)
R["towns"]["last_by_century"] = {str(k): v for k, v in sorted(lastc.items())}
gp = [p for p in towns if p["longest_gap_years"] != ""]
lg = max(gp, key=lambda p: p["longest_gap_years"])
R["towns"]["never_list"] = [[p["name"], p["area"]] for p in towns if p["n_total"] == 0]
R["towns"]["longest_gap"] = dict(years=lg["longest_gap_years"], n_with_gap=len(gp), n_at_max=sum(1 for p in gp if p["longest_gap_years"] == lg["longest_gap_years"]),
                                 places=sorted({p["name"] for p in gp if p["longest_gap_years"] == lg["longest_gap_years"]})[:10])
R["towns"]["shortest_gap"] = min(p["longest_gap_years"] for p in gp)
# shortest gap between two totals at any town
sg = []
for p in towns:
    ys = [int(x.split(":")[0][:4]) for x in p["totals"].split(";") if x]
    sg += [(b - a, p["name"], a, b) for a, b in zip(ys, ys[1:])]
mn = min(sg)
R["towns"]["min_interval"] = dict(years=mn[0], places=sorted({s[1] for s in sg if s[0] == mn[0]})[:12], pairs=sorted({(s[2], s[3]) for s in sg if s[0] == mn[0]}))
# longest wait to come: years from the last total (or 1000) to the next (or beyond 2200) for towns today
def wait(p):
    a = int(p["last_total"][:4]) if p["last_total"] else None; b = int(p["next_total"][:4]) if p["next_total"] else None
    return a, b
R["towns"]["years_since_last_median"] = float(np.median([2026 - int(p["last_total"][:4]) for p in towns if p["last_total"]]))

# ---------- named places ----------
NAMED = [("London", "City"), ("Birmingham", "City"), ("Manchester", "City"), ("Liverpool", "City"), ("Leeds", "City"), ("Sheffield", "City"),
         ("Bristol", "City"), ("Newcastle upon Tyne", "City"), ("Glasgow", "City"), ("Edinburgh", "City"), ("Cardiff", "City"), ("Belfast", "Northern Ireland"),
         ("Dublin", "Ireland"), ("Cork", "Ireland"), ("Galway", "Ireland"), ("Aberdeen", "City"), ("Inverness", "City"), ("York", "City"), ("Norwich", "City"),
         ("Plymouth", "City"), ("Exeter", "City"), ("Truro", "City"), ("Penzance", "Town"), ("Swansea", "City"), ("Douglas", "Isle of Man"), ("Giggleswick", "village"),
         ("Southport", "Town"), ("St Anne", "Guernsey"), ("Derby", "City"), ("Lancaster", "City"), ("Dover", "Town"), ("Hastings", "Town"), ("Morecambe", "Town"),
         ("Ayr", "Town"), ("Carlisle", "City"), ("Stornoway", "Town"), ("Lerwick", "Town"), ("Kirkwall", "Town"), ("Oxford", "City"), ("Cambridge", "City"), ("Southampton", "City"), ("Carrickfergus", "Northern Ireland"), ("Hexham", "Town"), ("Durham", "City"), ("Bradford", "City"), ("Halifax", "Town"), ("Ashford", "Kent"), ("Folkestone", "Town"), ("Omagh", "Northern Ireland"), ("Fraserburgh", "Town"), ("Dundee", "City"), ("Newquay", "Town"), ("Poole", "Town"), ("Bantry", "Ireland"), ("Clifden", "Ireland")]
def find(name, hint):
    c = [p for p in prow if p["name"] == name]
    if len(c) > 1:
        c2 = [p for p in c if p["area"] == hint] or [p for p in c if p["kind"] == hint.lower() or p["country"] == hint]
        c = c2 or c
    if len(c) > 1:
        c = sorted(c, key=lambda p: {"city": 0, "town": 1, "village": 2}[p["kind"]])
    return c[0] if c else None
NP = {}
for n, h in NAMED:
    p = find(n, h)
    if p: NP[n] = dict(name=p["name"], area=p["area"], lat=p["lat"], lon=p["lon"], n_total=p["n_total"], n_annular=p["n_annular"],
                       last=p["last_total"], last_dur=p["last_total_dur_s"], next=p["next_total"], next_dur=p["next_total_dur_s"],
                       totals=p["totals"], annulars=p["annulars"])
R["named"] = NP

# ---------- grid summary ----------
ids = sorted(grids)
nt = np.zeros(LA.shape, int); na = np.zeros(LA.shape, int)
last = np.full(LA.shape, -1, int); nxt = np.full(LA.shape, -1, int)
for i, e_id in enumerate(ids):
    k = grids[e_id]["kind"]
    nt += (k == 1); na += (k == -1)
    if e_id < TODAY: last = np.where(k == 1, i, last)
    else: nxt = np.where((k == 1) & (nxt < 0), i, nxt)
yr = np.array([int(e[:4]) for e in ids])
ntl = nt[land]
R["land"] = dict(mean_totals=float(ntl.mean()), share_none=float((ntl == 0).mean()), share_one_plus=float((ntl >= 1).mean()),
                 max_totals=int(ntl.max()), mean_return_years=float((Y1 - Y0 + 1) / ntl.mean()),
                 share_total_since_1000_before_today=float((last[land] >= 0).mean()),
                 share_next_by_2200=float((nxt[land] >= 0).mean()),
                 dist={str(k): int(v) for k, v in sorted(Counter(ntl.tolist()).items())},
                 share_annular_one_plus=float((na[land] >= 1).mean()), mean_annulars=float(na[land].mean()),
                 share_central_none=float(((nt + na)[land] == 0).mean()))
# where the most totals fell
mx = np.argwhere((nt == ntl.max()) & land)
R["land"]["max_cells"] = [[float(LA[a, b]), float(LO[a, b])] for a, b in mx[:50]]
with open(D("grid.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["lat", "lon", "land", "n_total", "n_annular", "last_total", "next_total"])
    for a in range(LA.shape[0]):
        for b in range(LA.shape[1]):
            if land[a, b]:
                w.writerow([LA[a, b], LO[a, b], 1, nt[a, b], na[a, b], ids[last[a, b]] if last[a, b] >= 0 else "", ids[nxt[a, b]] if nxt[a, b] >= 0 else ""])

# ---------- paths (filled contours of g < 0 with the Sun up) ----------
feats = []
for e in ecl:
    g = grids[e["eclipse"]]
    z = np.where(g["kind"] != 0, np.minimum(g["gmin"], -0.01), np.maximum(g["gmin"], 0.01)).astype(float)
    gen = contourpy.contour_generator(GLON, GLAT, z, fill_type=contourpy.FillType.OuterOffset)
    polys, offs = gen.filled(-1e9, 0.0)
    out = []
    for pts, off in zip(polys, offs):
        rings = [pts[off[i]:off[i + 1]] for i in range(len(off) - 1)]
        if len(rings[0]) < 4: continue
        out.append(Polygon(rings[0], [r for r in rings[1:] if len(r) >= 4]))
    if not out: continue
    geom = unary_union(out).simplify(0.015, preserve_topology=True)
    feats.append(dict(type="Feature", properties=dict(id=e["eclipse"], y=e["year"], k=e["regional_kind"][0], land=e["on_land"]),
                      geometry=json.loads(json.dumps(mapping(geom), default=float))))
import eclib
for e in ecl:
    u = float(EX[e["eclipse"]]["peak_ut"]); E = eclib.Eclipse(u)
    t, la, lo = eclib.centreline(E, u - 0.145, u + 0.145, 20)
    m = (la > 48.6) & (la < 61.4) & (lo > -11.6) & (lo < 2.6)
    if m.sum() < 2: continue
    idx = np.where(m)[0]
    segs = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
    lines = [[[float(lo[i]), float(la[i])] for i in s] for s in segs if len(s) > 1]
    if lines:
        feats.append(dict(type="Feature", properties=dict(id=e["eclipse"], y=e["year"], k="c", land=e["on_land"]),
                          geometry=dict(type="MultiLineString", coordinates=lines)))


def rnd(c):
    if isinstance(c, (list, tuple)):
        if c and isinstance(c[0], (int, float)): return [round(c[0], 3), round(c[1], 3)]
        return [rnd(x) for x in c]
    return c
for f in feats: f["geometry"]["coordinates"] = rnd(f["geometry"]["coordinates"])
json.dump(dict(type="FeatureCollection", features=feats), open(D("paths.geojson"), "w"), separators=(",", ":"))

# ---------- validation against published statements ----------
VAL = [("1715-05-03", "London", "total, 3 min 33 s (Wikipedia, Solar eclipse of May 3, 1715)", 213),
       ("1927-06-29", "Giggleswick", "total, on the line of totality (Wikipedia, Solar eclipse of June 29, 1927)", None),
       ("1927-06-29", "Southport", "total, 'those memorable 23 seconds' (observer quoted in Wikipedia)", 23),
       ("1999-08-11", "Plymouth", "total, 1 min 42 s (Wikipedia local circumstances table)", 102),
       ("1999-08-11", "St Anne", "total, 1 min 41 s at Saint Anne, Alderney (Wikipedia table)", 101),
       ("1999-08-11", "London", "partial only, 96.58% (Wikipedia table)", 0),
       ("1999-08-11", "Dublin", "partial only, 91.23% (Wikipedia table)", 0),
       ("2090-09-23", "Plymouth", "total (Wikipedia, Solar eclipse of September 23, 2090)", None),
       ("2090-09-23", "Southampton", "total (Wikipedia)", None),
       ("2090-09-23", "London", "partial only (Wikipedia)", 0),
       ("2090-09-23", "Dublin", "partial only (Wikipedia)", 0),
       ("2090-09-23", "Cork", "West Cork total (Wikipedia); Cork city listed here as a test", None),
       ("1724-05-22", "London", "path passed to the south of London (Wikipedia)", 0),
       ("1140-03-20", "Derby", "centre line near Derby (Wikipedia list)", None),
       ("2135-10-07", "Edinburgh", "centre line passes south of Edinburgh (Wikipedia list)", None),
       ("2135-10-07", "Glasgow", "centre line passes north of Glasgow (Wikipedia list)", None),
       ("2142-05-25", "Dover", "total in Dover (Wikipedia list)", None),
       ("2142-05-25", "Hastings", "total in Hastings (Wikipedia list)", None),
       ("2151-06-14", "Lancaster", "Lancashire on the centre line (Wikipedia list)", None),
       ("2189-11-08", "Truro", "centre line through Truro (Wikipedia list)", None),
       ("2200-04-14", "Morecambe", "centre line over Morecambe Bay (Wikipedia list)", None),
       ("2093-07-23", "Ayr", "annular, centre line Ayr to Newcastle (Wikipedia list)", None),
       ("1652-04-08", "Edinburgh", "track across Scotland 'including most of the major cities' (Wikipedia list)", None),
       ("1652-04-08", "Glasgow", "as above", None),
       ("1133-08-02", "York", "Wikipedia gives no path detail for Britain; shown for interest", None)]
vrows = []
for e_id, n, claim, sec in VAL:
    p = NP.get(n)
    if not p: continue
    got = [x for x in (p["totals"] + ";" + p["annulars"]).split(";") if x.startswith(e_id)]
    kind = "total" if any(x.startswith(e_id) for x in p["totals"].split(";")) else ("annular" if got else "partial or none")
    dur = int(got[0].split(":")[1]) if got else 0
    vrows.append(dict(eclipse=e_id, place=n, published=claim, published_s=sec if sec is not None else "", computed_kind=kind, computed_dur_s=dur))
with open(D("validation.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(vrows[0])); w.writeheader(); w.writerows(vrows)
R["validation"] = vrows
# longest duration in the islands: the Wikipedia list's figures against mine (longest at a land cell or listed place)
VAL2 = [("1023-01-24", "just over 2 1/2 minutes, around the Isle of Man and the Solway Firth", 150), ("1230-05-14", "2 min 27 s on the centre line near Bridlington", 147),
        ("1241-10-06", "2 min 50 s at the north-eastern tip of Unst", 170), ("1330-07-16", "around 52 s in the western parts of the track", 52),
        ("1339-07-07", "1 to 2 s as the track crossed Orkney", 2), ("1424-06-26", "almost 2 and a half minutes", 150),
        ("1927-06-29", "24 s", 24), ("2090-09-23", "2 min 10 s in Cornwall", 130), ("2093-07-23", "annular, just over 5 minutes near the centre line", 300)]
EC = {e["eclipse"]: e for e in ecl}
R["validation_max"] = [dict(eclipse=d, published=t, published_s=s_, computed_s=EC[d]["max_dur_land_s"] if d in EC else 0,
                            computed_place=EC[d]["max_dur_place"] if d in EC else "") for d, t, s_ in VAL2]
with open(D("validation_max.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(R["validation_max"][0])); w.writeheader(); w.writerows(R["validation_max"])
R["lunar_lag_s"] = {k: round(float(eclib.lunar_lag_seconds(float(EX[k]["peak_ut"]) + float(EX[k]["delta_t_s"]) / 86400)), 1) for k in ("1023-01-24", "1140-03-20", "1715-05-03", "2142-05-25")}
# the Wikipedia list (UK, after AD 1000): which of its total and annular eclipses I reproduce
WIKI = ["1023-01-24", "1133-08-02", "1140-03-20", "1230-05-14", "1241-10-06", "1330-07-16", "1339-07-07", "1424-06-26", "1433-06-17", "1598-03-07",
        "1652-04-08", "1654-08-12", "1699-09-23", "1715-05-03", "1724-05-22", "1925-01-24", "1927-06-29", "1954-06-30", "1999-08-11", "2003-05-31",
        "2048-06-11", "2081-09-03", "2090-09-23", "2093-07-23", "2133-06-03", "2135-10-07", "2142-05-25", "2151-06-14", "2160-06-04", "2189-11-08", "2200-04-14"]
mine = {e["eclipse"]: e for e in ecl}
R["wiki_check"] = dict(listed=len(WIKI), found=[d for d in WIKI if d in mine], missing=[d for d in WIKI if d not in mine],
                       extra=[e["eclipse"] for e in EL if e["eclipse"] not in WIKI])
# Ireland: Wikipedia says no total eclipse was seen from Ireland between 1724 and 2090
irl = [p for p in prow if p["country"] in ("Ireland", "Northern Ireland")]
R["ireland_between_1724_2090"] = sorted({x.split(":")[0] for p in irl for x in p["totals"].split(";") if x and "1724-06" < x < "2090"})
# near misses: how far outside the central shadow (km, at the closest moment) are places that published lists put inside
def miss(e_id, la, lo):
    i = int(np.abs(GLAT - la).argmin()); j = int(np.abs(GLON - lo).argmin())
    return round(float(grids[e_id]["gmin"][i, j]), 1)
R["misses"] = dict(unst_1241=miss("1241-10-06", 60.75, -0.85), dover_2142=miss("2142-05-25", 51.13, 1.31), hastings_2142=miss("2142-05-25", 50.86, 0.58),
                   dt_2142=float(EX["2142-05-25"]["delta_t_s"]), dt_2090=float(EX["2090-09-23"]["delta_t_s"]), dt_1140=float(EX["1140-03-20"]["delta_t_s"]),
                   dt_1133=float(EX["1133-08-02"]["delta_t_s"]), dt_1715=float(EX["1715-05-03"]["delta_t_s"]), dt_1999=float(EX["1999-08-11"]["delta_t_s"]))
# ---------- Delta T sensitivity (step 2) ----------
if os.path.exists(D("deltat.csv")):
    R["deltat"] = list(csv.DictReader(open(D("deltat.csv"))))
R["today"] = TODAY
R["eclipse_list"] = ecl

# ---------- page data ----------
EI = {e["eclipse"]: i for i, e in enumerate(ecl)}
PE = [[e["eclipse"], e["brit_date"], e["regional_kind"][0].upper(), e["total_land_km2"], e["annular_land_km2"], e["towns_total"], e["places_total"],
       e["places_annular"], e["towns_annular"], e["max_dur_s"], e["max_dur_place"], e["peak_hour_ut"], e["on_land"]] for e in ecl]
json.dump(dict(E=PE, cent=R["by_century"]), open(D("page_data.json"), "w"), separators=(",", ":"))
areas = sorted({p["area"] for p in prow}); AI = {a: i for i, a in enumerate(areas)}
KI = {"city": 0, "town": 1, "village": 2}
rows = []
for p in prow:
    h = [[EI[x.split(":")[0]], int(x.split(":")[1])] for x in p["totals"].split(";") if x] + \
        [[EI[x.split(":")[0]], -int(x.split(":")[1])] for x in p["annulars"].split(";") if x]
    rows.append([p["name"], AI[p["area"]], KI[p["kind"]], round(p["lat"], 3), round(p["lon"], 3), sorted(h)])
json.dump(dict(areas=areas, rows=rows), open(D("places_page.json"), "w"), separators=(",", ":"), ensure_ascii=False)

# ---------- raster overlays for the page (Web Mercator rows so Leaflet places them correctly) ----------
from PIL import Image
merc = lambda la: np.log(np.tan(np.pi / 4 + np.radians(la) / 2))
H = 900; W = 2 * len(GLON)
ys = np.linspace(merc(61.02), merc(48.98), H); lat_rows = np.degrees(2 * np.arctan(np.exp(ys)) - np.pi / 2)
ri = np.clip(np.round((lat_rows - 49.0) / 0.04).astype(int), 0, len(GLAT) - 1)
ci = np.clip(np.round((np.linspace(-11.03, 2.03, W) + 11.0) / 0.06).astype(int), 0, len(GLON) - 1)
def overlay(val, colours, name):
    img = np.zeros((H, W, 4), np.uint8)
    v = val[ri][:, ci]; lm = land[ri][:, ci]
    for k, c in colours.items():
        m = (v == k) & lm
        img[m] = c
    os.makedirs(os.path.join(ROOT, "img"), exist_ok=True)
    Image.fromarray(img, "RGBA").save(os.path.join(ROOT, "img", name), optimize=True)
cent_last = np.where(last >= 0, ((yr[np.maximum(last, 0)] - 1) // 100 + 1), 0)
R["overlay_bounds"] = [[48.98, -11.03], [61.02, 2.03]]
CNT = {0: (242, 211, 191, 200), 1: (217, 226, 238, 200), 2: (175, 193, 218, 200), 3: (127, 152, 192, 200), 4: (86, 112, 159, 200), 5: (58, 76, 120, 200), 6: (39, 47, 82, 200), 7: (24, 28, 51, 200), 8: (11, 12, 22, 200)}
overlay(np.minimum(nt, 8), CNT, "count.png")
R["legend_count"] = [[f"{k} total{'s' if k != 1 else ''}" if k else "none", f"rgba({c[0]},{c[1]},{c[2]},{c[3] / 255:.2f})"] for k, c in CNT.items() if k <= max(int(nt[land].max()), 0)]
CENC = {0: (242, 211, 191, 205), 11: (235, 217, 168, 205), 12: (216, 184, 106, 205), 13: (185, 194, 122, 205), 14: (143, 179, 138, 205), 15: (111, 163, 160, 205), 16: (91, 134, 176, 205), 17: (76, 95, 163, 205), 18: (169, 155, 200, 205), 19: (90, 46, 94, 205), 20: (181, 70, 47, 205)}
overlay(cent_last, CENC, "last.png")
present = set(int(v) for v in cent_last[land].ravel())
R["legend_last"] = [["none since 1000" if k == 0 else f"{k - 1}00s", f"rgba({c[0]},{c[1]},{c[2]},{c[3] / 255:.2f})"] for k, c in CENC.items() if k in present]
R["quick"] = [["London", NP["London"]["area"]], ["Edinburgh", NP["Edinburgh"]["area"]], ["Dublin", "Ireland"], ["Plymouth", NP["Plymouth"]["area"]],
              ["Giggleswick", NP["Giggleswick"]["area"]], ["Belfast", "Northern Ireland"], ["Cardiff", NP["Cardiff"]["area"]], ["Derby", NP["Derby"]["area"]]]
json.dump(R, open(D("results.json"), "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
np.savez_compressed(os.path.join(WORK, "grid_summary.npz"), nt=nt, na=na, last=last, nxt=nxt, land=land, cent_last=cent_last)
json.dump(R, open(D("results.json"), "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print(json.dumps({k: R[k] for k in ("global", "eclipses", "towns", "land", "wiki_check")}, indent=1, default=str)[:6000])
