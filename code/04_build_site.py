"""Step 4. Build ../index.html from page_template.html and ../README.md from README_template.md.

Numbers in the text come from ../data/results.json, either as {{path|fmt}} placeholders or through
the prose blocks in prose.py (TEXT_* keys), which are written from the same results. The eclipse list
and the paths are embedded as `const D = ...`; the place list is fetched from data/places_page.json.
Formats: int, pct0, pct1, f1, words, Words, raw.
Run: python3 04_build_site.py
"""
import json, os, re
import prose

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
P = json.load(open(os.path.join(ROOT, "data", "page_data.json")))
G = json.load(open(os.path.join(ROOT, "data", "paths.geojson")))
WORDS = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split()


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "pct0": return f"{float(v) * 100:.0f}%"
    if f == "pct1": return f"{float(v) * 100:.1f}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "words": return WORDS[int(v)] if int(v) < len(WORDS) else f"{int(v):,}"
    if f == "Words": w = fmt(v, "words"); return w[0].upper() + w[1:]
    return str(v)


def sub(m_):
    path, _, f = m_.group(1).partition("|")
    return fmt(get(path.strip()), f.strip() or "raw")


def fill(t, blocks):
    for k, v in blocks.items():
        t = t.replace("{{" + k + "}}", v)
    return re.sub(r"\{\{(.+?)\}\}", sub, t)


if __name__ == "__main__":
    PR = {k: v for k, v in R.items() if k not in ("eclipse_list",)}
    D = dict(R=PR, P=P, G=G)
    t = fill(open(os.path.join(HERE, "page_template.html")).read(), prose.page_blocks(R))
    assert "{{" not in t, re.findall(r"\{\{.+?\}\}", t)[:5]
    t = t.replace("/*DATA*/", "const D = " + json.dumps(D, separators=(",", ":"), ensure_ascii=False) + ";")
    open(os.path.join(ROOT, "index.html"), "w").write(t)
    print("index.html", len(t.encode()) // 1024, "KB")
    md = fill(open(os.path.join(HERE, "README_template.md")).read(), prose.readme_blocks(R))
    assert "{{" not in md
    open(os.path.join(ROOT, "README.md"), "w").write(md)
    print("README.md written")
