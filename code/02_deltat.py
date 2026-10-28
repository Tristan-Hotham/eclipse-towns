"""Step 2. How much do the medieval paths depend on Delta T (the slowly growing gap between Earth-rotation
time and uniform time)? Re-run selected eclipses with Delta T shifted by a fixed number of seconds and
count the towns and cities whose verdict (total or not) changes, and how far the path moves.

A Delta T error of s seconds turns the Earth by s x 360 / 86164 degrees, so the path slides east or west by
that much longitude: at 54 degrees north, about 0.27 km per second.
Output: data/deltat.csv. Run after step 1: python3 02_deltat.py
"""
import csv, os
import numpy as np
import astronomy as A
import astronomy.astronomy as AA   # the module-level Delta T hook (_DeltaT) lives here
import eclib

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
places = list(csv.DictReader(open(os.path.join(ROOT, "data", "places_in.csv"), encoding="utf-8")))
T = [p for p in places if p["kind"] in ("town", "city")]
lat = np.array([float(p["lat"]) for p in T]); lon = np.array([float(p["lon"]) for p in T])
EX = {e["date"]: e for e in csv.DictReader(open(os.path.join(ROOT, "data", "eclipses_all.csv")))}
SEL = ["1133-08-02", "1140-03-20", "1230-05-14", "1433-06-17", "1652-04-08", "1715-05-03", "2090-09-23", "2142-05-25"]
SHIFTS = [-120, -60, -30, 0, 30, 60, 120]
rows = []
for e_id in SEL:
    u = float(EX[e_id]["peak_ut"]); base = None
    for s in SHIFTS:
        AA._DeltaT = (lambda ut, s=s: A.DeltaT_EspenakMeeus(ut) + s)
        E = eclib.Eclipse(u)
        o = eclib.scan(E, lat, lon, u - 0.15, u + 0.15, coarse_s=30, thresh_km=500)
        tot = o["kind"] == 1
        lon_c = float(np.mean(lon[tot])) if tot.any() else float("nan")
        lat_c = float(np.mean(lat[tot])) if tot.any() else float("nan")
        if s == 0: base = (tot, lon_c)
        rows.append(dict(eclipse=e_id, delta_t_base_s=EX[e_id]["delta_t_s"], shift_s=s, towns_total=int(tot.sum()), lon_mean=round(lon_c, 3), lat_mean=round(lat_c, 3), _tot=tot))
        print(e_id, s, int(tot.sum()), flush=True)
    AA._DeltaT = A.DeltaT_EspenakMeeus
    for r in rows:
        if r["eclipse"] == e_id:
            t0, l0 = base
            r["towns_changed"] = int((r["_tot"] ^ t0).sum()); r["towns_kept"] = int((r["_tot"] & t0).sum())
            r["lon_shift_deg"] = round(r["lon_mean"] - l0, 3) if r["towns_total"] and t0.any() else ""
            r["shift_km_at_54N"] = round(abs(r["shift_s"]) * 360 / 86164.1 * 111.32 * np.cos(np.radians(54)), 1)
for r in rows: r.pop("_tot")
with open(os.path.join(ROOT, "data", "deltat.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print("written", len(rows))
