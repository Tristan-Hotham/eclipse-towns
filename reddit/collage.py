"""r/dataisbeautiful collage: every path of totality over Britain and Ireland, AD 1000 to 2200.
Every number comes from ../data/results.json; paths from ../data/paths.geojson. Fonts: FONT_DIR (Fraunces,
Source Serif 4, IBM Plex Mono). Run from this folder: FONT_DIR=/path/to/fonts python3 collage.py
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly
from shapely.geometry import shape

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
FD = os.environ.get("FONT_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts")
for f in ["FrauncesVar.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "SourceSerif4-It.ttf"]:
    fm.fontManager.addfont(os.path.join(FD, f))
DISP = fm.FontProperties(fname=os.path.join(FD, "FrauncesVar.ttf"), weight=900)
SER = "Source Serif 4"; MONO = "IBM Plex Mono"
FG = "#1B1F2E"; MUT = "#5A6072"; UMB = "#23263A"; ANN = "#C8513A"; GOLD = "#C98A22"; LANDC = "#FBF8F2"; COASTC = "#A79E90"; RED = "#B5462F"
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
P = json.load(open(os.path.join(ROOT, "data", "paths.geojson")))
E = {e["eclipse"]: e for e in R["eclipse_list"]}
K = 1 / np.cos(np.radians(54.5))
MON = "January February March April May June July August September October November December".split()
def dstr(d): y, m, dd = d.split("-"); return f"{int(dd)} {MON[int(m) - 1]} {int(y)}"

COAST = os.path.join(ROOT, "..", "did-lighthouses-work", "release", "build", "ne10m_land_british_isles.json")
LANDP = []
for g in json.load(open(COAST)):
    for p in shape(g).geoms:
        x0, y0, x1, y1 = p.bounds
        LANDP.append((p, (x0 > -2.0 and y0 <= 49.01 and p.area > 1) or x0 > 3.0))


def base(ax, ext=(-10.7, 2.0, 49.1, 60.95), lw=.6):
    for p, fr in LANDP:
        ax.add_patch(MPoly(np.array(p.exterior.coords), closed=True, fc="#F1ECE4" if fr else LANDC, ec=COASTC, lw=lw, zorder=1, alpha=.55 if fr else 1))
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(K); ax.axis("off"); ax.patch.set_alpha(0)


def polys(geom):
    cs = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    return [np.array(c[0]) for c in cs]


def draw_path(ax, eid, fc=UMB, alpha=.85, line=True):
    for f in P["features"]:
        pr = f["properties"]
        if pr["id"] != eid: continue
        if pr["k"] == "c":
            if line:
                for ln in f["geometry"]["coordinates"]:
                    a = np.array(ln); ax.plot(a[:, 0], a[:, 1], color=GOLD, lw=1.6, zorder=4)
        else:
            for a in polys(f["geometry"]):
                ax.add_patch(MPoly(a, closed=True, fc=fc, ec="none", alpha=alpha, zorder=3))


fig = plt.figure(figsize=(12, 15), dpi=200)
bg = fig.add_axes([0, 0, 1, 1], zorder=-10); bg.axis("off")
grad = np.linspace(0, 1, 512)[:, None]
from matplotlib.colors import LinearSegmentedColormap
cm = LinearSegmentedColormap.from_list("dawn", ["#D7E4F1", "#E9EEF2", "#F6ECE2", "#F7DCC8"])
bg.imshow(grad, aspect="auto", cmap=cm, extent=[0, 1, 0, 1], origin="upper")

T = R["towns"]; L = R["land"]; N = R["named"]
fig.text(0.045, 0.968, "When did your town last see", fontproperties=DISP, fontsize=46, color=FG, va="top")
fig.text(0.045, 0.922, "a total eclipse?", fontproperties=DISP, fontsize=46, color=RED, va="top")
fig.text(0.047, 0.872, f"Every path of totality across Britain and Ireland from AD 1000 to 2200, computed from the motions\n"
                       f"of the Sun and Moon and tested at {R['places']['n']:,} cities, towns and villages.", family=SER, fontsize=15, color=FG, va="top", linespacing=1.35)

# hero map: every path of totality stacked
ax = fig.add_axes([0.0, 0.30, 0.58, 0.52]); base(ax)
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
_v, _c = [], []
for p, fr in LANDP:
    if fr: continue
    c = list(p.exterior.coords); _v += c; _c += [MPath.MOVETO] + [MPath.LINETO] * (len(c) - 2) + [MPath.CLOSEPOLY]
CLIP = PathPatch(MPath(_v, _c), fc="none", ec="none", transform=ax.transData); ax.add_patch(CLIP)
for f in P["features"]:
    pr = f["properties"]
    if pr["k"] in ("t", "h") and pr["land"]:
        for a in polys(f["geometry"]):
            ax.add_patch(MPoly(a, closed=True, fc=UMB, ec="none", alpha=.05, zorder=2))
            q = MPoly(a, closed=True, fc=UMB, ec="none", alpha=.21, zorder=2); ax.add_patch(q); q.set_clip_path(CLIP)
for eid in ("1715-05-03", "1927-06-29", "1999-08-11", "2090-09-23"):
    for f in P["features"]:
        if f["properties"]["id"] == eid and f["properties"]["k"] == "c":
            for ln in f["geometry"]["coordinates"]:
                a = np.array(ln); ax.plot(a[:, 0], a[:, 1], color=GOLD, lw=2.2, zorder=4, solid_capstyle="round")
LAB = {"1715-05-03": (0.4, 52.45, "1715 Halley", "left"), "1927-06-29": (-0.9, 54.62, "1927", "left"), "1999-08-11": (-3.4, 49.55, "1999", "left"), "2090-09-23": (-10.4, 49.45, "2090", "left")}
for eid, (x, y, s, ha) in LAB.items():
    ax.text(x, y, s, fontsize=12, color=FG, family=MONO, fontweight="medium", zorder=6, ha=ha, va="center",
            bbox=dict(fc="#FBF8F2", ec="none", alpha=.8, pad=1.5))
ax.text(-10.55, 60.85, f"{R['eclipses']['with_totality_on_land']} paths of totality, AD 1000 to 2200", family=MONO, fontsize=12.5, color=FG, va="top", fontweight="medium")
ax.text(-10.55, 60.55, "darker = more eclipses\ngold = four centre lines", family=MONO, fontsize=11, color=MUT, va="top", linespacing=1.45)

# right column: big numbers
tx = fig.add_axes([0.62, 0.30, 0.36, 0.54]); tx.axis("off")
notes = [(f"{R['land']['mean_return_years']:.0f} years", f"average wait between total eclipses\nat a spot on land (the worldwide figure\nusually quoted is about 375)"),
         ("1", f"total eclipse in London in 1,200\nyears: Halley's, {dstr(N['London']['last'])}.\nNone before 2200."),
         (f"{R['region_gap_max']['years']} years", f"with no totality on land, from\n{dstr(R['region_gap_max']['from'])} to {dstr(R['region_gap_max']['to'])}"),
         (f"{T['never_window']}", f"towns with no total eclipse at all\nin the 1,200 years: "
                                  "Ashford, Folkestone and\nHythe in Kent; Omagh and Donegal\nin Ireland")]
for (big, small), y in zip(notes, [1.0, 0.74, 0.50, 0.27]):
    tx.text(0, y, big, fontproperties=DISP, fontsize=34, color=RED if big != "1" else UMB, va="top", transform=tx.transAxes)
    tx.text(0, y - 0.085, small, family=SER, fontsize=13, color=FG, va="top", transform=tx.transAxes, linespacing=1.3)

# small multiples: famous eclipses
SM = ["1140-03-20", "1652-04-08", "1715-05-03", "1724-05-22", "1927-06-29", "2090-09-23"]
fig.text(0.045, 0.283, "SIX FAMOUS SHADOWS  ·  computed path of totality and cities and towns inside it", family=MONO, fontsize=11.5, color=MUT)
for i, eid in enumerate(SM):
    a = fig.add_axes([0.01 + i * 0.163, 0.1, 0.16, 0.148]); base(a, lw=.35)
    draw_path(a, eid, alpha=.8, line=True)
    e = E[eid]
    a.set_title(f"{eid[:4]}: {e['towns_total']:,} towns", family=MONO, fontsize=12, color=FG, pad=2, linespacing=1.25)

fig.text(0.045, 0.018, "Data: own calculation with Astronomy Engine (MIT; Delta T after Espenak and Meeus; lunar acceleration matched to ELP-2000/82).\n"
                       "Places: OS Open Names (Contains OS data © Crown copyright and database right 2026, OGL v3) and GeoNames (CC BY 4.0); coastline Natural Earth.\n"
                       "Medieval and 22nd-century path edges uncertain by km to tens of km. Weather ignored. Interactive: tristan-hotham.github.io/eclipse-towns\n"
                       "Analysis and chart: Tristan Hotham, with Python and matplotlib.",
         family=MONO, fontsize=9, color=MUT, linespacing=1.4, va="bottom")
out = os.path.join(HERE, "when_did_your_town_last_see_a_total_eclipse.png")
fig.savefig(out, dpi=200)
print("ok", out)
