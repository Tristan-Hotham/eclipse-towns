"""Step 6. Render ../header.png (1200x630 social card) with Playwright Chromium.

Fonts: FONT_DIR holding FrauncesVar.ttf, SourceSerif4-Regular.ttf, IBMPlexMono-Regular.ttf and
IBMPlexMono-Medium.ttf (from github.com/google/fonts); otherwise system serif is used.
Coastline: Natural Earth 1:10m land for the British Isles, as extracted for the lighthouse project.
Run: FONT_DIR=/path/to/fonts python3 06_header.py
"""
import json, math, os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
P = json.load(open(os.path.join(ROOT, "data", "paths.geojson")))
FD = os.environ.get("FONT_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts")
K = math.cos(math.radians(54.5))
X0, X1, Y0, Y1 = -10.7 * K, 2.0 * K, -60.95, -49.8
Hh = 610; Ww = Hh * (X1 - X0) / (Y1 - Y0)


def pr(lat, lon):
    return (lon * K - X0) / (Y1 - Y0) * Hh, (-lat - Y0) / (Y1 - Y0) * Hh


def path(rings):
    return "".join("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in (pr(q[1], q[0]) for q in ring)) + "Z" for ring in rings)


COAST = os.path.join(ROOT, "..", "did-lighthouses-work", "release", "build", "ne10m_land_british_isles.json")
land = ""
for g in json.load(open(COAST)):
    for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
        xs = [q[0] for q in poly[0]]; ys = [q[1] for q in poly[0]]
        if (min(xs) > -2.0 and min(ys) <= 49.01) or min(xs) > 3.0: continue
        land += path([poly[0]])
bands = ""
for f in P["features"]:
    k = f["properties"]["k"]
    if k not in ("t", "h") or not f["properties"]["land"]: continue
    g = f["geometry"]; cs = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    d_ = path([c[0] for c in cs])
    bands += f'<path d="{d_}" fill="#23263A" fill-opacity=".05"/><path d="{d_}" fill="#23263A" fill-opacity=".2" clip-path="url(#land)"/>'
ff = ""
if FD:
    ff = "".join(f"@font-face{{font-family:'{n}';src:url('file://{FD}/{f}');font-weight:{w};}}" for n, f, w in [
        ("Fraunces", "FrauncesVar.ttf", "100 900"), ("Source Serif 4", "SourceSerif4-Regular.ttf", "400"),
        ("IBM Plex Mono", "IBMPlexMono-Regular.ttf", "400"), ("IBM Plex Mono", "IBMPlexMono-Medium.ttf", "500")])
T = R["towns"]
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{ff}
body{{margin:0;width:1200px;height:630px;background:linear-gradient(180deg,#DCE7F2 0%,#EEF0F0 45%,#F8E3D2 100%);color:#1B1F2E;overflow:hidden;position:relative;font-family:'Source Serif 4',Georgia,serif}}
.k{{position:absolute;left:66px;top:62px;font:500 15px/1 'IBM Plex Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:#5F6577;display:flex;gap:12px;align-items:center}}
.k b{{background:#23263A;color:#F8E3D2;padding:7px 9px;font-weight:500}}
h1{{position:absolute;left:60px;top:100px;margin:0;font:900 78px/.95 Fraunces,Georgia,serif;letter-spacing:-.02em;color:#1B1F2E;width:690px}}
h1 em{{font-style:normal;color:#B5462F}}
p{{position:absolute;left:66px;top:368px;width:620px;margin:0;font-size:25px;line-height:1.36}}
p b{{color:#B5462F}}
.f{{position:absolute;left:66px;bottom:40px;font:400 14px/1 'IBM Plex Mono',monospace;letter-spacing:.12em;text-transform:uppercase;color:#5F6577}}
svg{{position:absolute;right:40px;top:10px}}
</style></head><body>
<div class="k"><b>Data study</b><span>Every path of totality · AD 1000 to 2200</span></div>
<h1>When did your town last see a <em>total eclipse?</em></h1>
<p><b>{R['eclipses']['with_totality_on_land']}</b> total eclipses touched Britain and Ireland in 1,200 years. The average spot waits about <b>{R['land']['mean_return_years']:.0f} years</b> between them.</p>
<div class="f">Dr Tristan Hotham · Independent researcher</div>
<svg width="{Ww:.0f}" height="{Hh}" viewBox="0 0 {Ww:.0f} {Hh}"><defs><clipPath id="land"><path d="{land}"/></clipPath></defs><path d="{land}" fill="#FBF8F3" stroke="#B9AF9F" stroke-width="1"/>{bands}</svg>
</body></html>"""
os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)
tmp = os.path.join(ROOT, "work", "header.html"); open(tmp, "w").write(html)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.goto("file://" + os.path.abspath(tmp)); pg.wait_for_timeout(600)
    pg.screenshot(path=os.path.join(ROOT, "header.png")); b.close()
os.remove(tmp)
print("header.png written")
