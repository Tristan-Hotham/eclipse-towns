"""Step 5. Static figures for the paper (release/paper/f_*.png) and the blog (release/blog/b_*.png).
Maps are drawn from coordinates (Natural Earth coastline, the computed paths and grid), no web tiles.
Run: python3 05_figures.py
"""
import csv, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly
from matplotlib.collections import PatchCollection, LineCollection
from shapely.geometry import shape

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
FD = os.environ.get("FONT_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts")
for f in ["FrauncesVar.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf"]:
    if os.path.exists(os.path.join(FD, f)): fm.fontManager.addfont(os.path.join(FD, f))
MONO = "IBM Plex Mono"; SER = "Source Serif 4"
plt.rcParams.update({"font.family": MONO, "font.size": 11, "axes.edgecolor": "#5F6577", "axes.labelcolor": "#1B1F2E",
                     "xtick.color": "#5F6577", "ytick.color": "#5F6577", "axes.spines.top": False, "axes.spines.right": False})
BG = "#FBF8F3"; FG = "#1B1F2E"; MUT = "#5F6577"; LANDC = "#E6E0D6"; COASTC = "#B9AF9F"; UMB = "#23263A"; ANN = "#D2573C"; GOLD = "#D9952B"; SKY = "#4F7CAC"
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
P = json.load(open(os.path.join(ROOT, "data", "paths.geojson")))
E = {e["eclipse"]: e for e in R["eclipse_list"]}
K = 1 / np.cos(np.radians(54.5))
PAPER = os.path.join(ROOT, "release", "paper"); BLOG = os.path.join(ROOT, "release", "blog")
os.makedirs(PAPER, exist_ok=True); os.makedirs(BLOG, exist_ok=True)

COAST = os.path.join(ROOT, "..", "did-lighthouses-work", "release", "build", "ne10m_land_british_isles.json")
LANDP = []
for g in json.load(open(COAST)):
    for p in shape(g).geoms:
        x0, y0, x1, y1 = p.bounds
        LANDP.append((p, (x0 > -2.0 and y0 <= 49.01 and p.area > 1) or x0 > 3.0))


def base(ax, ext=(-10.8, 2.0, 49.1, 60.95), foreign=True):
    for p, fr in LANDP:
        if fr and not foreign: continue
        ax.add_patch(MPoly(np.array(p.exterior.coords), closed=True, fc="#EEEAE3" if fr else LANDC, ec=COASTC, lw=.5, zorder=1))
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(K); ax.axis("off")


def polys(geom):
    cs = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    return [np.array(c[0]) for c in cs]


def save(fig, name, both=True):
    for d, pre in ((PAPER, "f_"), (BLOG, "b_")):
        if pre == "f_" or both:
            fig.savefig(os.path.join(d, pre + name + ".png"), dpi=200, facecolor=BG)
    plt.close(fig)


# 1. Every path of totality, 1000 to 2200 (the striking map): strong on land, faint over the sea
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch


def land_clip(ax):
    verts, codes = [], []
    for p, fr in LANDP:
        if fr: continue
        c = list(p.exterior.coords); verts += c; codes += [MPath.MOVETO] + [MPath.LINETO] * (len(c) - 2) + [MPath.CLOSEPOLY]
    pp = PathPatch(MPath(verts, codes), fc="none", ec="none", transform=ax.transData); ax.add_patch(pp); return pp


fig = plt.figure(figsize=(7.6, 9.6), facecolor=BG); ax = fig.add_axes([0, 0, 1, 1]); base(ax, foreign=False)
clip = land_clip(ax)
for f in P["features"]:
    pr = f["properties"]
    if pr["k"] in ("t", "h") and pr["land"]:
        for a in polys(f["geometry"]):
            ax.add_patch(MPoly(a, closed=True, fc=UMB, ec="none", alpha=.045, zorder=2))
            q = MPoly(a, closed=True, fc=UMB, ec="none", alpha=.2, zorder=2); ax.add_patch(q); q.set_clip_path(clip)
LAB = {"1715-05-03": (0.45, 52.45, "1715 Halley"), "1927-06-29": (-1.0, 54.62, "1927"), "1999-08-11": (-3.4, 49.55, "1999"),
       "2090-09-23": (-10.3, 49.45, "2090"), "1140-03-20": (-6.9, 51.25, "1140"), "1652-04-08": (-1.55, 56.75, "1652 Mirk Monday")}
for f in P["features"]:
    pr = f["properties"]
    if pr["k"] == "c" and pr["id"] in LAB:
        for ln in f["geometry"]["coordinates"]:
            a = np.array(ln); ax.plot(a[:, 0], a[:, 1], color=GOLD, lw=1.5, zorder=3)
for k, (x, y, s) in LAB.items():
    ax.text(x, y, s, fontsize=10.5, color=FG, zorder=4, fontweight="medium", bbox=dict(fc=BG, ec="none", alpha=.8, pad=1.2))
ax.text(-10.6, 60.75, f"{R['eclipses']['with_totality_on_land']} paths of totality, AD 1000 to 2200", fontsize=12, color=FG, fontweight="medium")
ax.text(-10.6, 60.45, "darker = crossed by more paths\ngold: centre lines of six\nwell-known eclipses", fontsize=9.5, color=MUT, va="top", linespacing=1.4)
save(fig, "paths")

# 2. How many totals each place got, 1000 to 2200 (grid)
from matplotlib.colors import ListedColormap, BoundaryNorm
G = list(csv.DictReader(open(os.path.join(ROOT, "data", "grid.csv"))))
GLAT = np.round(np.arange(49.0, 61.0 + 1e-9, 0.04), 4); GLON = np.round(np.arange(-11.0, 2.0 + 1e-9, 0.06), 4)
def gridarr(vals):
    A_ = np.full((len(GLAT), len(GLON)), np.nan)
    for g, v in zip(G, vals):
        A_[int(round((float(g["lat"]) - 49.0) / 0.04)), int(round((float(g["lon"]) + 11.0) / 0.06))] = v
    return A_
def mesh(ax, A_, cols):
    cm_ = ListedColormap(cols); nm = BoundaryNorm(np.arange(-0.5, len(cols)), len(cols))
    ax.pcolormesh(np.r_[GLON - 0.03, GLON[-1] + 0.03], np.r_[GLAT - 0.02, GLAT[-1] + 0.02], np.ma.masked_invalid(A_), cmap=cm_, norm=nm, zorder=2, rasterized=True)
nt = np.array([int(g["n_total"]) for g in G])
CN = ["#F2D3BF", "#D9E2EE", "#AFC1DA", "#7F98C0", "#56709F", "#3A4C78", "#272F52", "#181C33", "#0B0C16"]
fig = plt.figure(figsize=(7.6, 9.6), facecolor=BG); ax = fig.add_axes([0, 0, 1, 1]); base(ax)
mesh(ax, gridarr(nt), CN)
for i in range(R["land"]["max_totals"] + 1):
    ax.add_patch(plt.Rectangle((-10.6, 60.55 - i * 0.3), 0.38, 0.2, fc=CN[i], ec=COASTC, lw=.4, zorder=5))
    share = R["land"]["dist"].get(str(i), 0) / R["grid"]["cells"]
    ax.text(-10.1, 60.57 - i * 0.3, f"{i}   {share * 100:.0f}%", fontsize=9.5, color=FG, zorder=5)
ax.text(-10.6, 60.85, "total eclipses, share of land", fontsize=9.5, color=MUT, zorder=5)
save(fig, "count")

# 3. Century of the last total eclipse before today
lastc = np.array([int(g["last_total"][:4]) if g["last_total"] else 0 for g in G])
cc = np.where(lastc > 0, (lastc - 1) // 100 + 1, 0)
present = sorted(set(int(v) for v in cc))
PAL = {0: "#F2D3BF", 11: "#EBD9A8", 12: "#D8B86A", 13: "#B9C27A", 14: "#8FB38A", 15: "#6FA3A0", 16: "#5B86B0", 17: "#4C5FA3", 18: "#A99BC8", 19: "#5A2E5E", 20: "#B5462F"}
cols = [PAL[c] for c in present]; idx = {c: i for i, c in enumerate(present)}
fig = plt.figure(figsize=(7.6, 9.6), facecolor=BG); ax = fig.add_axes([0, 0, 1, 1]); base(ax)
mesh(ax, gridarr([idx[int(v)] for v in cc]), cols)
for j, c in enumerate(present):
    ax.add_patch(plt.Rectangle((-10.6, 60.55 - j * 0.3), 0.38, 0.2, fc=PAL[c], ec=COASTC, lw=.4, zorder=5))
    ax.text(-10.1, 60.57 - j * 0.3, "none since AD 1000" if c == 0 else f"{c - 1}00s", fontsize=9.5, color=FG, zorder=5)
save(fig, "last")

# 4. Timeline of central eclipses with land area
fig, ax = plt.subplots(figsize=(7.6, 3.8), facecolor=BG); ax.set_facecolor(BG)
for e in R["eclipse_list"]:
    if not e["on_land"]: continue
    y = int(e["eclipse"][:4]) + (int(e["eclipse"][5:7]) - .5) / 12
    if e["regional_kind"] in ("total", "hybrid") and e["total_land_km2"] > 0:
        ax.bar(y, e["total_land_km2"] / 1000, width=5, color=UMB)
    if e["annular_land_km2"] > 0:
        ax.bar(y, -e["annular_land_km2"] / 1000, width=5, color=ANN)
ax.axhline(0, color=MUT, lw=.6); ax.axvline(2026.8, color=GOLD, lw=1.2, ls="--"); ax.text(2032, ax.get_ylim()[1] * .9, "today", color=GOLD, fontsize=10)
ax.axvspan(1724.4, 1927.5, color=SKY, alpha=.12, lw=0); ax.text(1826, ax.get_ylim()[0] * .75, "1724 to 1927:\nno totality\non land", ha="center", va="center", fontsize=9, color=SKY)
ax.set_xlim(995, 2205); ax.set_ylabel("land in the path, thousand km²")
yt = ax.get_yticks(); ax.set_yticks(yt); ax.set_yticklabels([f"{abs(v):.0f}" for v in yt])
ax.text(1003, ax.get_ylim()[1] * .97, "total", color=UMB, fontsize=10, va="top"); ax.text(1003, ax.get_ylim()[0] * .97, "annular", color=ANN, fontsize=10, va="bottom")
fig.tight_layout(); save(fig, "timeline")

# 5. Distribution: number of total eclipses per town, 1000 to 2200
fig, ax = plt.subplots(figsize=(7.6, 3.6), facecolor=BG); ax.set_facecolor(BG)
d = R["towns"]["dist"]; ks = sorted(int(k) for k in d); vs = [d[str(k)] for k in ks]; n = sum(vs)
ax.bar(ks, [v / n * 100 for v in vs], color=[CN[min(k, 8)] for k in ks], ec=UMB, lw=.6)
for k, v in zip(ks, vs): ax.text(k, v / n * 100 + .8, f"{v / n * 100:.0f}%" if v / n >= .01 else f"{v} towns", ha="center", fontsize=10)
ax.set_xticks(ks); ax.set_xlabel("total eclipses seen, AD 1000 to 2200"); ax.set_ylabel("share of towns and cities, %")
fig.tight_layout(); save(fig, "towns_hist")

# 6. Delta T sensitivity
if "deltat" in R:
    fig, ax = plt.subplots(figsize=(7.6, 3.6), facecolor=BG); ax.set_facecolor(BG)
    by = {}
    for r in R["deltat"]: by.setdefault(r["eclipse"], []).append((int(r["shift_s"]), int(r["towns_changed"])))
    cols = [UMB, ANN, GOLD, SKY, "#7A4A4F", "#4F9A7F", "#8A8A8A", "#B07CC6"]
    for (k, v), c in zip(by.items(), cols):
        v = sorted(v); ax.plot([a for a, b in v], [b for a, b in v], "-o", color=c, ms=4, lw=1.4, label=k[:4])
    ax.set_xlabel("error in Delta T, seconds"); ax.set_ylabel("towns that change verdict")
    ax.legend(frameon=False, fontsize=9, ncol=2)
    fig.tight_layout(); save(fig, "deltat")
print("figures written")
