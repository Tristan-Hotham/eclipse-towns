"""Step 8. Blog post (release/blog/post.html from blog_template.html), blog and Zenodo meta files,
and the Zenodo folder (paper, key CSVs, results.json and a code-and-data zip).
Image placeholders {{IMG|file|alt|caption}} are left for the uploader.
Run: python3 08_release.py
"""
import json, os, re, shutil, zipfile
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "04_build_site.py")); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
import prose
R = b.R
t = open(os.path.join(HERE, "blog_template.html")).read()
for k, v in prose.blog_blocks(R).items():
    t = t.replace("{{" + k + "}}", v)
t = re.sub(r"\{\{(?!IMG\|)([^{}]+?)\}\}", b.sub, t)
os.makedirs(os.path.join(ROOT, "release", "blog"), exist_ok=True)
open(os.path.join(ROOT, "release", "blog", "post.html"), "w").write(t)
for m in re.findall(r"\{\{IMG\|([^|]+)\|", t):
    assert os.path.exists(os.path.join(ROOT, "release", "blog", m)), m

TITLE = "When Did Your Town Last See a Total Eclipse? Every Path of Totality over Britain and Ireland, AD 1000 to 2200"
meta = prose.blog_meta(R)
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
json.dump(meta, open(os.path.join(ROOT, "release", "blog", "meta.json"), "w"), indent=2, ensure_ascii=False)

pt = open(os.path.join(ROOT, "release", "paper", "Hotham_Eclipse_Towns.tex")).read()
ab = pt.split("\\begin{center}\\textbf{Abstract}\\end{center}")[1].split("\\textbf{Keywords:}")[0].strip()
ab = ab.replace("\\%", "%").replace("$<$", "<").replace("~", " ")
Z = os.path.join(ROOT, "release", "zenodo"); os.makedirs(Z, exist_ok=True)
zmeta = dict(
    title=TITLE,
    description_html="".join(f"<p>{p.strip()}</p>" for p in ab.split("\n\n") if p.strip()) +
                     "<p>Interactive version: https://tristan-hotham.github.io/eclipse-towns/. Data and code: https://github.com/Tristan-Hotham/eclipse-towns. Blog post: to follow.</p>",
    keywords=["solar eclipses", "total solar eclipse", "eclipse paths", "Delta T", "historical astronomy", "Britain", "Ireland", "towns", "Halley", "open data"],
    licence="cc-by-4.0",
    related=[
        dict(identifier="https://github.com/Tristan-Hotham/eclipse-towns", relation="issupplementedby", resource_type="software"),
        dict(identifier="https://tristan-hotham.github.io/eclipse-towns/", relation="issupplementedby", resource_type="other"),
        dict(identifier="https://github.com/cosinekitty/astronomy", relation="isderivedfrom", resource_type="software"),
        dict(identifier="https://www.ordnancesurvey.co.uk/products/os-open-names", relation="isderivedfrom", resource_type="dataset"),
        dict(identifier="https://www.geonames.org/", relation="isderivedfrom", resource_type="dataset"),
        dict(identifier="https://www.naturalearthdata.com/", relation="isderivedfrom", resource_type="dataset"),
        dict(identifier="https://en.wikipedia.org/wiki/List_of_solar_eclipses_visible_from_the_British_Isles", relation="isderivedfrom", resource_type="other"),
    ])
json.dump(zmeta, open(os.path.join(Z, "meta.json"), "w"), indent=2, ensure_ascii=False)
shutil.copy(os.path.join(ROOT, "release", "Hotham_Eclipse_Towns.pdf"), Z)
for f in ["eclipses.csv", "places.csv", "eclipses_all.csv", "grid.csv", "validation.csv", "validation_max.csv", "deltat.csv", "paths.geojson", "results.json"]:
    shutil.copy(os.path.join(ROOT, "data", f), Z)
with zipfile.ZipFile(os.path.join(Z, "eclipse-towns_code_and_data.zip"), "w", zipfile.ZIP_DEFLATED) as zf:
    for sub in ("code", "data", "img"):
        for f in sorted(os.listdir(os.path.join(ROOT, sub))):
            p = os.path.join(ROOT, sub, f)
            if os.path.isfile(p) and not f.endswith(".pyc"): zf.write(p, f"eclipse-towns/{sub}/{f}")
    for f in ("README.md", "LICENSE"): zf.write(os.path.join(ROOT, f), f"eclipse-towns/{f}")
print("release files written; post words:", len(re.sub(r"<[^>]+>", " ", re.sub(r"\{\{IMG\|.*?\}\}", "", t, flags=re.S)).split()))
