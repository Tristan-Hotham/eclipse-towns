"""Step 7. Build the paper PDF: fill paper_template.tex with numbers and tables from data/results.json,
write release/paper/Hotham_Eclipse_Towns.tex and compile it with xelatex (figures from 05_figures.py).
Placeholders: {{path|fmt}} as in 04_build_site.py, with % escaped for LaTeX.
Run: python3 07_paper.py
"""
import json, os, re, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Eclipse_Towns"
WORDS = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split()
MON = "January February March April May June July August September October November December".split()


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "pct0": return f"{float(v) * 100:.0f}\\%"
    if f == "pct1": return f"{float(v) * 100:.1f}\\%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "words": return WORDS[int(v)] if int(v) < len(WORDS) else f"{int(v):,}"
    if f == "Words": w = fmt(v, "words"); return w[0].upper() + w[1:]
    if f == "date": y, m, d = str(v).split("-"); return f"{int(d)} {MON[int(m) - 1]} {int(y)}"
    return str(v)


def sub(m):
    path, _, f = m.group(1).partition("|")
    return fmt(get(path.strip()), f.strip() or "raw")


tex = lambda s: str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_")
mmss = lambda s: (f"{int(s) // 60} min {int(s) % 60} s" if int(s) >= 60 else f"{int(s)} s")
dstr = lambda d: fmt(d, "date")

# Table 1: every eclipse with totality on land
rows = ""
for e in R["eclipse_list"]:
    if not e["on_land"]: continue
    br = f" ({dstr(e['brit_date'])})" if e["brit_date"] != e["eclipse"] else ""
    rows += (f"{dstr(e['eclipse'])}{br} & {e['regional_kind']} & {e['total_land_km2'] + e['annular_land_km2']:,} & {e['towns_total'] + e['towns_annular']:,} & "
             f"{e['places_total'] + e['places_annular']:,} & {mmss(e['max_dur_s']) if e['max_dur_s'] else ''} & {tex(e['max_dur_place'].split(',')[0])}\\\\\n")
TE = ("{\\small\\setlength{\\tabcolsep}{4pt}\\begin{longtable}{p{4.2cm}lrrrrp{3.0cm}}\\caption{Every eclipse of AD 1000 to 2200 whose total or annular shadow touched land in the study area. "
      "Dates in the Julian calendar before 15 October 1582 and the Gregorian after; in brackets, the date in the British calendar where it differs. "
      "Land: km$^2$ inside the central path (4 km grid). Towns: OS cities and towns and GeoNames towns of 1,500 or more in the path. Longest: longest central phase at a listed place.}\\label{tab:all}\\\\"
      "\\toprule Date & Type & Land km$^2$ & Towns & Places & Longest & At\\\\\\midrule\\endfirsthead\\toprule Date & Type & Land km$^2$ & Towns & Places & Longest & At\\\\\\midrule\\endhead\n"
      + rows + "\\bottomrule\\end{longtable}}")
# Table 2: validation
rows = ""
for v in R["validation"]:
    got = "not central" if v["computed_kind"] == "partial or none" else f"{v['computed_kind']}, {mmss(v['computed_dur_s'])}"
    rows += f"{dstr(v['eclipse'])} & {tex(v['place'])} & {tex(v['published'])} & {got}\\\\\n"
TV = ("\\begin{table}[tbp]\\centering\\small\\caption{Computed results for named places against published statements (Wikipedia articles cited in the text).}\\label{tab:val}"
      "\\begin{tabular}{p{2.6cm}p{2.0cm}p{6.4cm}p{2.6cm}}\\toprule Eclipse & Place & Published & Computed\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
# Table 3: cities
rows = ""
for n, c in R["named"].items():
    if n not in ("London", "Birmingham", "Manchester", "Liverpool", "Leeds", "Sheffield", "Bristol", "Newcastle upon Tyne", "Glasgow", "Edinburgh", "Cardiff", "Belfast", "Dublin", "Cork", "Galway", "Aberdeen", "Inverness", "York", "Norwich", "Plymouth", "Exeter", "Douglas"):
        continue
    rows += (f"{tex(n)} & {dstr(c['last']) if c['last'] else 'none since 1000'} & {mmss(c['last_dur']) if c['last'] else ''} & "
             f"{dstr(c['next']) if c['next'] else 'none by 2200'} & {c['n_total']} & {c['n_annular']}\\\\\n")
TC = ("\\begin{table}[tbp]\\centering\\small\\caption{Last and next total eclipse for large cities. Totals and annulars: number in AD 1000 to 2200.}\\label{tab:cities}"
      "\\begin{tabular}{llrlrr}\\toprule City & Last total & Duration & Next total & Totals & Annulars\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
import prose
s = open(os.path.join(HERE, "paper_template.tex")).read()
s = s.replace("{{TABLE_ALL}}", TE).replace("{{TABLE_VAL}}", TV).replace("{{TABLE_CITIES}}", TC)
for k, v in prose.paper_blocks(R).items():
    s = s.replace("{{" + k + "}}", v)
s = re.sub(r"\{\{(.+?)\}\}", sub, s)
assert "{{" not in s
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w").write(s)
for _ in range(3):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
print(r.stdout[-800:])
for ext in (".aux", ".log", ".out"):
    p = os.path.join(OUT, NAME + ext)
    if os.path.exists(p): os.remove(p)
shutil.move(os.path.join(OUT, NAME + ".pdf"), os.path.join(ROOT, "release", NAME + ".pdf"))
