"""Step 1. Find every total, annular or hybrid solar eclipse whose central shadow touched Britain,
Ireland, the Isle of Man or the Channel Islands from AD 1000 to 2200, and test every place and grid cell.

1. List all solar eclipses (Astronomy Engine SearchGlobalSolarEclipse / NextGlobalSolarEclipse).
2. Screen each one on a 1 degree test grid over the region (2 minute steps, generous threshold).
3. For survivors, scan a 0.04 x 0.06 degree grid (lat 49 to 61 N, lon 11 W to 2 E; about 4 km cells) and
   every place in data/places_in.csv (step 0) at 30 second steps, then 2 second steps around each
   place's closest approach (eclib.scan). Record kind (total or annular) and duration with the Sun up.
Outputs: data/eclipses_all.csv (every eclipse in the window, for the global rates),
work/grid_<id>.npz (temporary grid fields for step 3), work/place_hits.csv.
Run: python3 01_eclipses.py   (about 20 to 40 minutes on two cores)
"""
import csv, json, math, os, sys, time
import numpy as np
import astronomy as A
import eclib

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
WORK = os.path.join(ROOT, "work"); os.makedirs(WORK, exist_ok=True)
Y0, Y1 = 1000, 2200
GLAT = np.round(np.arange(49.0, 61.0 + 1e-9, 0.04), 4); GLON = np.round(np.arange(-11.0, 2.0 + 1e-9, 0.06), 4)


def jd_to_cal(jd):
    """Calendar date for a Julian Day: Julian calendar before 1582-10-15, Gregorian after (NASA convention).
    Also returns the date in the calendar used in Britain and Ireland (Julian until 2 September 1752)."""
    def conv(jd, greg):
        z = int(math.floor(jd + 0.5)); f = jd + 0.5 - z
        if greg:
            al = int((z - 1867216.25) / 36524.25); a = z + 1 + al - al // 4
        else:
            a = z
        b = a + 1524; c = int((b - 122.1) / 365.25); d = int(365.25 * c); e = int((b - d) / 30.6001)
        day = b - d - int(30.6001 * e) + f; m = e - 1 if e < 14 else e - 13; y = c - 4716 if m > 2 else c - 4715
        return y, m, int(day), (day - int(day)) * 24
    nasa = conv(jd, jd >= 2299160.5)
    brit = conv(jd, jd >= 2361221.5)   # Gregorian in Britain from 14 September 1752
    return nasa, brit


def main():
    places = list(csv.DictReader(open(os.path.join(ROOT, "data", "places_in.csv"), encoding="utf-8")))
    plat = np.array([float(p["lat"]) for p in places]); plon = np.array([float(p["lon"]) for p in places])
    LA, LO = np.meshgrid(GLAT, GLON, indexing="ij")
    glat, glon = LA.ravel(), LO.ravel()
    tlat, tlon = np.meshgrid(np.arange(49.0, 61.01, 1.0), np.arange(-11.0, 2.01, 1.0), indexing="ij")
    tlat, tlon = tlat.ravel(), tlon.ravel()

    t = A.Time.Make(Y0 - 1, 12, 1, 0, 0, 0)
    e = A.SearchGlobalSolarEclipse(t)
    allrows = []; hits = []; cand = 0; t_start = time.time()
    while True:
        jd = e.peak.ut + 2451545.0
        (y, mo, d, h), (by, bmo, bd, bh) = jd_to_cal(jd)
        if y > Y1: break
        row = dict(peak_ut=round(e.peak.ut, 6), date=f"{y:04d}-{mo:02d}-{d:02d}", brit_date=f"{by:04d}-{bmo:02d}-{bd:02d}",
                   peak_hour_ut=round(h, 3), global_kind=e.kind.name.lower(), peak_lat=round(e.latitude, 2) if e.latitude == e.latitude else "",
                   peak_lon=round(e.longitude, 2) if e.longitude == e.longitude else "", delta_t_s=round((e.peak.tt - e.peak.ut) * 86400, 1), touches=0)
        if y >= Y0:
            E = eclib.Eclipse(e.peak.ut)
            tt = e.peak.ut + np.arange(-210, 211, 2) / 1440.0
            T = np.broadcast_to(tt, (len(tlat), len(tt)))
            pos, up = eclib.ecef(tlat, tlon)
            g, k, alt = E.g(T, pos, up)
            g = np.where(alt > -0.05, g, np.inf)
            if g.min() < 700:
                close = np.where((g < 1200).any(0))[0]
                ta, tb = tt[close[0]] - 12 / 1440.0, tt[close[-1]] + 12 / 1440.0
                gr = eclib.scan(E, glat, glon, ta, tb, coarse_s=30, thresh_km=500)
                pr = eclib.scan(E, plat, plon, ta, tb, coarse_s=30, thresh_km=500)
                if (gr["kind"] != 0).any() or (pr["kind"] != 0).any():
                    cand += 1
                    eid = row["date"]
                    row["touches"] = 1
                    np.savez_compressed(os.path.join(WORK, f"grid_{eid}.npz"), gmin=np.where(np.isfinite(gr["gmin"]), gr["gmin"], 9999).astype(np.float32).reshape(LA.shape),
                                        dur=gr["dur"].astype(np.float32).reshape(LA.shape), kind=gr["kind"].astype(np.int8).reshape(LA.shape),
                                        tmax=gr["tmax"].reshape(LA.shape))
                    for i in np.where(pr["kind"] != 0)[0]:
                        hits.append((places[i]["pid"], eid, int(pr["kind"][i]), round(float(pr["dur"][i]), 1), round(float(pr["tmax"][i]), 6)))
                    print(eid, e.kind.name, "grid cells", int((gr["kind"] != 0).sum()), "places", int((pr["kind"] != 0).sum()),
                          f"{time.time() - t_start:.0f}s", flush=True)
            allrows.append(row)
        e = A.NextGlobalSolarEclipse(e.peak)
    with open(os.path.join(ROOT, "data", "eclipses_all.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(allrows[0])); w.writeheader(); w.writerows(allrows)
    with open(os.path.join(WORK, "place_hits.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["pid", "eclipse", "kind", "dur_s", "tmax_ut"]); w.writerows(hits)
    print("eclipses", len(allrows), "touching", cand, f"{time.time() - t_start:.0f}s")


if __name__ == "__main__":
    main()
