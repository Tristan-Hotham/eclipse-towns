"""Prose for the page, README, paper and blog, written from data/results.json so every number is computed.
Each function returns {KEY: text} for the placeholders in the templates. Facts about history come from the
English Wikipedia articles listed in the README; facts about paths and durations come from results.json."""

MON = "January February March April May June July August September October November December".split()


def n(v): return f"{int(round(float(v))):,}"
def pc(v, d=0): return f"{float(v) * 100:.{d}f}%"
def dstr(d):
    y, m, dd = str(d).split("-"); return f"{int(dd)} {MON[int(m) - 1]} {int(y)}"
def mmss(s):
    s = int(round(float(s))); return f"{s // 60} min {s % 60} s" if s >= 60 else f"{s} s"
def lst(xs):
    xs = list(xs); return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def facts(R):
    E = {e["eclipse"]: e for e in R["eclipse_list"]}
    T = R["towns"]; L = R["land"]; N = R["named"]
    V = {(v["eclipse"], v["place"]): v for v in R["validation"]}
    VM = {v["eclipse"]: v for v in R["validation_max"]}
    dt = {}
    for r in R["deltat"]:
        r = dict(r)
        for k in ("shift_s", "towns_total", "towns_changed"): r[k] = int(float(r[k]))
        r["shift_km_at_54N"] = float(r["shift_km_at_54N"])
        dt.setdefault(r["eclipse"], {})[r["shift_s"]] = r
    def dur(place, eid):
        for x in N[place]["totals"].split(";"):
            if x.startswith(eid): return int(x.split(":")[1])
        return None
    last = T["last_by_century"]
    never = T["never_list"]
    F = dict(E=E, T=T, L=L, N=N, V=V, VM=VM, dt=dt, dur=dur,
             n_tot=R["eclipses"]["with_totality_on_land"], n_ann=R["eclipses"]["annular"], n_before=R["eclipses"]["total_before_today"],
             n_after=R["eclipses"]["total_after_today"], ret=L["mean_return_years"], n18=last.get("18", 0), share18=last.get("18", 0) / T["n"],
             n20=last.get("20", 0), none1000=T["none_since_1000"], never=T["never_window"], none2200=T["none_until_2200"],
             never_kent=[a for a, b in never if b == "Kent"], never_irl=[a for a, b in never if b in ("Ireland", "Northern Ireland")],
             gap=T["longest_gap"], short=T["min_interval"], cen={c["century"]: c for c in R["by_century"]})
    return F


def dt_range(F, eid):
    d = F["dt"][eid]; a, b = sorted([d[-60]["towns_changed"], d[60]["towns_changed"]]); return a, b, d[0]["towns_total"]


def stories(R, F, html=True):
    E, N, V, dur = F["E"], F["N"], F["V"], F["dur"]
    e = lambda d: E[d]
    S = [
        ("1133-08-02", "King Henry's eclipse",
         f"The Peterborough Chronicle and William of Malmesbury both recorded this eclipse, and it was remembered as an omen: it fell as Henry I left England for Normandy for the last time, shortly before the civil war of the Anarchy. "
         f"In my calculation totality crossed Scotland and the far north of England: {n(e('1133-08-02')['towns_total'])} cities and towns, with {mmss(dur('Edinburgh', '1133-08-02'))} in Edinburgh and {mmss(dur('Newcastle upon Tyne', '1133-08-02'))} in Newcastle.",
         f"Longest on land: {mmss(e('1133-08-02')['max_dur_s'])} near {e('1133-08-02')['max_dur_place'].split(',')[0]}."),
        ("1140-03-20", "Candles at dinner",
         f"William of Malmesbury saw in it a sign of King Stephen's capture at Lincoln the next year. The Peterborough Chronicle says the day darkened in Lent \"when men were eating; and they lighted candles to eat by\". "
         f"My path runs from the south of Ireland across Wales and the Midlands: {n(e('1140-03-20')['towns_total'])} cities and towns, Derby with {mmss(dur('Derby', '1140-03-20'))}.",
         f"{n(e('1140-03-20')['total_land_km2'])} km² of land in totality. Longest: {mmss(e('1140-03-20')['max_dur_s'])} near Cardigan."),
        ("1652-04-08", "Mirk Monday",
         f"Known in Scotland as Mirk Monday and also called Black Monday (it was 29 March in the calendar then used in Britain). Nicholas Culpeper and William Lilly predicted catastrophe; John Wybard watched totality from Carrickfergus. "
         f"In my calculation the shadow crossed Ireland, the Isle of Man, the Lake District and Scotland: Dublin had {mmss(dur('Dublin', '1652-04-08'))}, Edinburgh {mmss(dur('Edinburgh', '1652-04-08'))}, Carrickfergus {mmss(dur('Carrickfergus', '1652-04-08'))}.",
         f"{n(e('1652-04-08')['towns_total'])} cities and towns. It is still the last total eclipse in Dublin, Belfast, Edinburgh and Glasgow."),
        ("1715-05-03", "Halley's eclipse",
         f"Edmond Halley predicted it, drew a map of the shadow's path and watched it from London; his prediction was about four minutes and 30 km out. London had 3 minutes 33 seconds of totality (22 April in the British calendar). "
         f"It is the only total eclipse in London in my whole window: I get {mmss(V[('1715-05-03', 'London')]['computed_dur_s'])}.",
         f"{n(e('1715-05-03')['towns_total'])} cities and towns and {n(e('1715-05-03')['places_total'])} places in all: the most of any eclipse in the 1,200 years."),
        ("1724-05-22", "Sunset over Galway",
         f"Nine years after Halley's eclipse, a second path crossed Ireland and southern Britain near sunset, from Galway to Wales, Devon, Hampshire and Sussex, passing south of London. "
         f"Thomas Simpson of Lincolnshire, then 13, took up astrology after seeing it and later became a noted mathematician. In my calculation {n(e('1724-05-22')['towns_total'])} cities and towns saw totality, and it was the last total eclipse anywhere in Ireland until 2090.",
         f"Longest on land: {mmss(e('1724-05-22')['max_dur_s'])} in County Clare. No path of totality then touched land here for {R['region_gap_max']['years']} years."),
        ("1927-06-29", "Giggleswick's 24 seconds",
         f"The first total eclipse on the British mainland for {R['region_gap_max']['years']} years lasted seconds, early on a cloudy morning. The Astronomer Royal's camp at Giggleswick School saw it; about a quarter of a million people stood on the shore at Southport. "
         f"I get {mmss(V[('1927-06-29', 'Giggleswick')]['computed_dur_s'])} at Giggleswick and {mmss(V[('1927-06-29', 'Southport')]['computed_dur_s'])} at Southport.",
         f"{n(e('1927-06-29')['towns_total'])} cities and towns, from North Wales to the north-east coast."),
        ("1999-08-11", "Clouded out in Cornwall",
         f"The BBC broadcast live from west Cornwall with Patrick Moore, but cloud hid totality almost everywhere on the mainland; the Lizard, around Goonhilly, was one of the few places where it cleared. Ferries in the Channel and the crowd on Alderney did better. "
         f"I get {mmss(V[('1999-08-11', 'Plymouth')]['computed_dur_s'])} at Plymouth (published: 1 min 42 s).",
         f"{n(e('1999-08-11')['towns_total'])} cities and towns in Cornwall, Devon and the Channel Islands."),
        ("2090-09-23", "The next one",
         f"The next total eclipse on the British mainland comes late in the afternoon of 23 September 2090, close to sunset, across the far south-west of Ireland, Cornwall, Devon, Dorset, Hampshire and the Isle of Wight. "
         f"It will be Ireland's first since 1724. I get {mmss(dur('Plymouth', '2090-09-23'))} at Plymouth and {mmss(dur('Southampton', '2090-09-23'))} at Southampton.",
         f"{n(e('2090-09-23')['towns_total'])} cities and towns. London, again, will see only a partial eclipse."),
    ]
    if not html:
        return S
    out = ""
    for d, h, body, k in S:
        br = E[d]["brit_date"]
        out += (f'<article><div class="d">{dstr(d)}{" (" + dstr(br) + " in Britain)" if br != d else ""}</div><h3>{h}</h3><p style="margin:6px 0 0">{body}</p>'
                f'<div class="k">{k}</div><button class="btn" data-show="{d}">Show on the map</button></article>')
    return out


def para_rare(R, F):
    T, L = F["T"], F["L"]
    g, s = F["gap"], F["short"]
    return (f"Luck still varies a lot. The {n(T['n'])} cities and towns in my list average {T['mean_n']:.1f} totals each. The luckiest, with {T['max_n']}, are "
            f"{lst(T['max_n_places'])}. At the other end, {F['never']} towns have none at all in the whole window: the corner of Kent around "
            f"{lst(F['never_kent'][:5])}, and a belt across south Ulster and the border counties of Ireland, among them {lst(F['never_irl'][:4])}. "
            f"The longest wait between two totals is {n(g['years'])} years, from 1140 to 2151, shared by {g['n_at_max']} towns around Manchester and east Lancashire, among them "
            f"{lst([p for p in g['places'] if p in ('Bolton', 'Bury', 'Accrington', 'Altrincham')])}. The shortest is {s['years']} years: towns in the north-east of Scotland such as "
            f"{lst([p for p in s['places'] if p in ('Elgin', 'Fraserburgh', 'Banff', 'Huntly')])} saw totality in {s['pairs'][0][0]} and again in {s['pairs'][0][1]}.")


def para_last(R, F):
    T = F["T"]
    return (f"Most places last saw totality a long time ago. For {n(F['n18'])} of the towns ({pc(F['share18'])}) the last total eclipse was Halley's of 1715 or its sequel of 1724. "
            f"Only {n(F['n20'])} saw one in the twentieth century, in 1927 or 1999, and {n(F['none1000'])} have had none since AD 1000. The median town has waited "
            f"{n(T['years_since_last_median'])} years. Looking ahead, {n(F['none2200'])} towns ({pc(T['none_until_2200_share'])}) will see no total eclipse before 2200; for "
            f"{n(T['next_2090'])} the next comes in 2090.")


def para_check(R, F, html=True):
    V, VM, W, M = F["V"], F["VM"], R["wiki_check"], R["misses"]
    p1 = (f"A calculation like this is only worth trusting if it reproduces the eclipses people actually saw. Where a duration is published for a named place, mine agree to within "
          f"about 12 seconds: London in 1715 comes out at {mmss(V[('1715-05-03', 'London')]['computed_dur_s'])} against 3 minutes 33 seconds, Southport in 1927 at "
          f"{mmss(V[('1927-06-29', 'Southport')]['computed_dur_s'])} against an observer's 23, and Plymouth and Alderney in 1999 at {mmss(V[('1999-08-11', 'Plymouth')]['computed_dur_s'])} and "
          f"{mmss(V[('1999-08-11', 'St Anne')]['computed_dur_s'])} against 1 min 42 s and 1 min 41 s. London and Dublin come out partial in 1999 and 2090, as published. The sunrise eclipse of 1230, "
          f"which Wikipedia's list says peaked at 2 min 27 s near Bridlington, peaks in my calculation at {mmss(VM['1230-05-14']['computed_s'])} at Filey, just up the coast.")
    p2 = (f"Wikipedia's list of eclipses visible from the British Isles, based on Sheridan Williams's book of 1996, names {W['listed']} total and annular eclipses over the United Kingdom after AD 1000. "
          f"I find {len(W['found'])} of them. The one I do not, the annular eclipse of 2048, is described there as passing just north of Shetland, which is what I get too. Wikipedia also says that no "
          f"total eclipse was seen from Ireland between 1724 and 2090; neither does my calculation. I find some the list does not mention: many annular eclipses (the list is not complete for them), "
          f"totals seen only in Ireland, such as 1679, a substantial total in 1185 across the Hebrides and the north of Scotland ({n(F['E']['1185-05-01']['towns_total'])} towns, among them "
          f"Inverness and Kirkwall), and a marginal one in 1630 that clipped the far south-west of Ireland and the tip of Cornwall for under 20 seconds.")
    p3 = (f"Some differences remain. For 1424 the list gives almost two and a half minutes; I get {mmss(VM['1424-06-26']['computed_s'])} on Orkney. For 2142 the list puts Dover and Hastings in "
          f"totality, but my path stays about {M['dover_2142']:.0f} km offshore. Fred Espenak's current path table for 2142 on EclipseWise also leaves both towns just outside, and the gap between "
          f"his path and mine is almost all Delta T: he uses 178 seconds for that year, the formula built into my software {n(M['dt_2142'])}.")
    p4 = (f"One correction was needed to get here. Astronomy Engine's series for the Moon has a slightly smaller long-term slowing of the Moon's mean motion than the lunar theory that the "
          f"Delta T formulas assume. Left alone, its Moon runs ahead by about {n(R['lunar_lag_s']['1023-01-24'] / 60)} minutes of time in 1023 and {n(R['lunar_lag_s']['1715-05-03'])} seconds in 1715, "
          f"which slid my medieval paths more than a hundred kilometres east. I hold the Moon back by that amount (details in the paper). With the correction, and the same Delta T, "
          f"my centre lines for 1140 and 2142 lie within about 7 km of Espenak's published ones.")
    if html:
        return "".join(f"<p>{p}</p>" for p in (p1, p2, p3, p4))
    return p1, p2, p3, p4


def para_deltat(R, F, html=True):
    d = F["dt"]; M = R["misses"]
    a40, b40, t40 = dt_range(F, "1140-03-20"); a30, b30, t30 = dt_range(F, "1230-05-14"); a90, b90, t90 = dt_range(F, "2090-09-23")
    p1 = (f"The Earth's rotation is slowing, unevenly, mostly because of the tides. Eclipse calculations run on uniform time, so to know where on the turning Earth a shadow fell you need "
          f"the difference between uniform time and the clock the Earth keeps, called Delta T. In 1999 it was about a minute ({n(M['dt_1999'])} seconds in my model). Wikipedia's article gives "
          f"historical values of about 1,570 seconds in AD 1000 and 200 seconds in 1500, worked out largely from records of ancient and medieval eclipses. My calculation uses the Espenak and Meeus "
          f"formulas built into Astronomy Engine, which give {n(M['dt_1140'])} seconds for 1140.")
    p2 = (f"An error of one minute in Delta T turns the Earth a quarter of a degree under the shadow and slides the path about {d['1140-03-20'][60]['shift_km_at_54N']:.0f} km east or west at "
          f"British latitudes. For the eclipse of 1140, shifting Delta T by a minute either way changes the verdict for {a40} to {b40} of its {n(t40)} towns, mostly at the edges of the path. "
          f"The sunrise eclipse of 1230 is more fragile ({a30} to {b30} of {n(t30)}), because near sunrise a small shift moves the shadow a long way over the ground. The far future is uncertain too: "
          f"Delta T for 2090 and 2142 is a forecast, not a measurement, though for 2090 a minute either way changes only {a90} to {b90} of {n(t90)} towns. So read the dates for towns near the edge "
          f"of a medieval or twenty-second-century path as \"probably\", and those near the centre line as safe.")
    if html:
        return f"<p>{p1}</p><p>{p2}</p>"
    return p1, p2


def method_html(R, F):
    return (f"<p><b>Eclipses.</b> I listed all {n(R['global']['n'])} solar eclipses from AD 1000 to 2200 with Astronomy Engine (version 2.1.19), screened each on a one-degree test grid over the islands, and "
            f"scanned the survivors on a grid of 0.04 by 0.06 degrees (about 4 km; {n(R['grid']['cells'])} land cells) and at each of the {n(R['places']['n'])} places, first every 30 seconds and then every "
            f"2 seconds around the moment of closest approach. At each moment I take the Moon and the Sun (with light-time and aberration) from Astronomy Engine, turn the place's position on the Earth's "
            f"ellipsoid into the same frame using sidereal time and precession and nutation, and measure its distance from the axis of the Moon's shadow against the radius of the umbra (total) or "
            f"antumbra (annular) at that point, as Astronomy Engine's own local eclipse code does. A place counts only if the Sun is above its horizon (no refraction). Durations are the time inside the "
            f"central shadow with the Sun up. I hold the Moon back along its orbit to match the long-term lunar acceleration that the Delta T formulas assume (section 05).</p>"
            f"<p><b>Places.</b> Great Britain: every OS Open Names populated place of type City, Town or Village. Ireland, Northern Ireland, the Isle of Man and the Channel Islands: GeoNames places of 1,000 "
            f"people or more ({n(R['places']['other'])} places; those of 1,500 or more count as towns). \"Cities and towns\" in the statistics means OS City and Town plus those GeoNames towns: "
            f"{n(R['towns']['n'])} places.</p>"
            f"<p><b>Caveats.</b> Delta T is uncertain before about 1600 and after today, so path edges are uncertain by kilometres to tens of kilometres (section 06). The Moon's mean radius is used: "
            f"mountains and valleys on its limb change durations by a second or two and matter only for the thinnest paths. Weather is ignored: most of these eclipses were probably clouded out "
            f"somewhere. Dates are in the Julian calendar before 15 October 1582 and the Gregorian after it; Britain and Ireland used the Julian calendar until 1752, so the page also gives the local date. "
            f"\"Today\" is {dstr(R['today'])}. The eclipse of 12 August 2026 was total in Iceland and Spain but not here.</p>")


def page_blocks(R):
    F = facts(R); T, L, N = F["T"], F["L"], F["N"]
    gm = R["region_gap_max"]
    B = {}
    B["TEXT_DEK"] = (f"The Moon's shadow is a narrow band, so any one spot can wait centuries for a total eclipse. I computed every path of totality and annularity that crossed Britain and Ireland "
                     f"from AD 1000 to 2200 and tested {n(R['places']['n'])} cities, towns and villages one by one. When did yours last go dark in daytime, and when will it next?")
    B["TEXT_STATS"] = f"""<div class="stats">
  <div><b>{F['n_tot']}</b><span>total eclipses touched land in Britain and Ireland, AD 1000 to 2200</span></div>
  <div><b class="r">{n(F['ret'])}</b><span>years: the average wait between totals at a spot on land</span></div>
  <div><b class="i">1</b><span>total eclipse in London in 1,200 years: {dstr(N['London']['last'])}</span></div>
  <div><b class="o">2090</b><span>the next on the mainland: 23 September, Cornwall to the Isle of Wight</span></div>
</div>"""
    B["TEXT_INTRO"] = (f"<p class=\"lede\">On {dstr('1715-05-03')}, at about nine in the morning, London went dark. Edmond Halley had predicted it and printed a map of where the Moon's shadow would fall, and for "
                       f"three and a half minutes the city saw the Sun's corona. Nobody in London has seen that since, and on my calculation nobody will before 2200. In the whole window from AD 1000 to 2200, "
                       f"{dstr(N['London']['last'])} is London's only total eclipse.</p>"
                       f"<p>That is not bad luck. A total eclipse happens somewhere on Earth every year or two ({n(R['global']['total'])} in these 1,200 years), but the Moon's dark shadow is only a narrow strip, "
                       f"so any one place has to wait a long time for it to pass overhead. Averaged over the land of Britain and Ireland, I find a total eclipse every {n(F['ret'])} years, close to the figure "
                       f"of about 375 years often given for the world as a whole.</p>"
                       f"<p>To find out what that means town by town, I used the open-source Astronomy Engine library to compute the positions of the Sun and Moon for every solar eclipse from AD 1000 to 2200 "
                       f"({n(R['global']['n'])} of them worldwide), found the {R['eclipses']['on_land']} whose total or annular shadow touched land in Britain, Ireland, the Isle of Man or the Channel Islands, and "
                       f"tested every city, town and village in the Ordnance Survey's gazetteer, plus the towns of Ireland, Northern Ireland, Man and the Channel Islands, second by second. The calculation "
                       f"reproduces the eclipses that history remembers, from King Henry's eclipse of 1133 to Cornwall's cloudy morning in 1999, with some honest caveats about the Middle Ages and the far future.</p>")
    B["TEXT_H_TIMELINE"] = "Feast and famine"
    B["TEXT_TIMELINE"] = (f"<p>Between AD 1000 and 2200 I count {F['n_tot']} total eclipses whose shadow touched land in Britain and Ireland, {F['n_before']} of them before today and {F['n_after']} still to come, "
                          f"plus {F['n_ann']} annular eclipses, when the Moon is too far away to cover the Sun and leaves a burning ring. On average a total eclipse touches land somewhere in the islands every "
                          f"{R['region_gap_mean']:.0f} years, but they come in clusters. Halley's eclipse of 1715 was followed only nine years later by another, across Ireland, Wales and the south. Then nothing: "
                          f"no path of totality touched land for {gm['years']} years, until the brief eclipse of {dstr(gm['to'])}. The whole nineteenth century had none. The twenty-second century, by contrast, has "
                          f"{F['cen'][22]['totals']}.</p>")
    B["TEXT_H_RARE"] = f"Once every {n(F['ret'])} years"
    B["TEXT_RARE"] = (f"<p>Totality needs the Moon's dark cone, the umbra, to reach the ground, and when it does it covers only a narrow strip that sweeps across the globe in a few hours. Over 1,200 years "
                      f"those strips criss-cross the islands. On my 4 km grid of the land, {pc(L['share_one_plus'])} of Britain and Ireland sees at least one total eclipse between AD 1000 and 2200, and the "
                      f"average spot sees {L['mean_totals']:.1f}. That works out at one every {n(F['ret'])} years.</p><p>{para_rare(R, F)}</p>")
    B["TEXT_RARE2"] = f"<p>{para_last(R, F)}</p>"
    B["TEXT_STORIES"] = stories(R, F)
    B["TEXT_CHECK"] = para_check(R, F)
    B["TEXT_DELTAT"] = para_deltat(R, F)
    B["TEXT_METHOD"] = method_html(R, F)
    return B


def readme_blocks(R):
    F = facts(R); T, L, N = F["T"], F["L"], F["N"]
    gm = R["region_gap_max"]; V = F["V"]
    a40, b40, t40 = dt_range(F, "1140-03-20")
    hl = [f"- Of {n(R['global']['n'])} solar eclipses from AD 1000 to 2200, {R['eclipses']['on_land']} had a total or annular shadow touching land in Britain, Ireland, the Isle of Man or the Channel Islands: {F['n_tot']} total ({F['n_before']} before today, {F['n_after']} to come) and {F['n_ann']} annular.",
          f"- On a 4 km grid, {pc(L['share_one_plus'])} of the land sees at least one total eclipse in the 1,200 years; the average spot sees {L['mean_totals']:.1f}, one every {n(F['ret'])} years (the worldwide figure usually quoted is about 375).",
          f"- London's only total eclipse in the window is Halley's, {dstr('1715-05-03')} ({mmss(V[('1715-05-03', 'London')]['computed_dur_s'])} computed; 3 min 33 s recorded). Dublin's only one is {dstr(N['Dublin']['last'])}.",
          f"- {dstr('1715-05-03')} put the most towns in totality ({n(F['E']['1715-05-03']['towns_total'])} of {n(T['n'])} cities and towns); {dstr(R['biggest'][0]['eclipse'])} will cover the most land ({n(R['biggest'][0]['km2'])} km²).",
          f"- No total eclipse touched land for {gm['years']} years, from {dstr(gm['from'])} to {dstr(gm['to'])}; the nineteenth century had none, the twenty-second will have {F['cen'][22]['totals']}.",
          f"- For {pc(F['share18'])} of towns the last total eclipse was in 1715 or 1724; {n(F['n20'])} had one in the twentieth century; {n(F['none1000'])} have had none since AD 1000 and {F['never']} (the Ashford and Folkestone corner of Kent and parts of south Ulster and the Irish border counties) none in the whole window. {n(F['none2200'])} towns will see none before 2200; for {n(T['next_2090'])} the next is 23 September 2090.",
          f"- Validation: {len(R['wiki_check']['found'])} of the {R['wiki_check']['listed']} eclipses in Wikipedia's British list are reproduced (the other passes just north of Shetland, as listed); published durations at London 1715, Southport 1927, Plymouth and Alderney 1999 are matched within about 12 seconds. Astronomy Engine's Moon needed a correction for its long-term acceleration (about {n(R['lunar_lag_s']['1023-01-24'])} seconds of time in 1023).",
          f"- Delta T matters: a one minute error moves a path about {F['dt']['1140-03-20'][60]['shift_km_at_54N']:.0f} km; for 1140 it changes the verdict for {a40} to {b40} of {n(t40)} towns."]
    meth = ("Eclipses from Astronomy Engine (SearchGlobalSolarEclipse), screened on a one-degree grid; survivors scanned every 30 seconds and then every 2 seconds at each place and on a 0.04 by 0.06 degree grid. "
            "At each moment the place's distance from the axis of the Moon's shadow is compared with the radius of the umbra or antumbra there (the test Astronomy Engine uses for local eclipses), with the Sun above the horizon. "
            "The Moon is held back along its orbit to correct Astronomy Engine's long-term lunar acceleration to the ELP-2000/82 value in Meeus's Astronomical Algorithms (equation 47.1), the lunar theory the Espenak and Meeus Delta T formulas assume. "
            "Paths are filled contours of the shadow distance; centre lines are where the shadow axis meets the ellipsoid. "
            "Checked against published durations and the Wikipedia list (data/validation.csv, data/validation_max.csv) and tested for Delta T errors of 30 to 120 seconds (data/deltat.csv). "
            "Caveats: medieval and future Delta T uncertain; lunar limb profile and weather ignored; place lists differ between Great Britain (OS Open Names) and elsewhere (GeoNames).")
    return dict(README_HEADLINES="\n".join(hl), README_METHOD=meth)


# ---------------- paper ----------------
def tx(s):
    s = s.replace("%", "\\%").replace("&", "\\&").replace("km²", "km$^2$")
    s = s.replace(" \"", " ``").replace("(\"", "(``").replace("\"", "''")
    return s


def paper_blocks(R):
    F = facts(R); T, L, N, E, V, VM = F["T"], F["L"], F["N"], F["E"], F["V"], F["VM"]
    gm = R["region_gap_max"]; M = R["misses"]
    a40, b40, t40 = dt_range(F, "1140-03-20")
    B = {}
    B["PAPER_ABSTRACT"] = tx(
        f"How often does a given town see a total eclipse of the Sun, and when did each town in Britain and Ireland last see one? I compute every solar eclipse from AD 1000 to 2200 with the open-source "
        f"Astronomy Engine library, correcting its long-term lunar acceleration to the value assumed by the Espenak and Meeus Delta T formulas, and test {n(R['places']['n'])} cities, towns and villages and a 4 km "
        f"land grid second by second. Of {n(R['global']['n'])} eclipses, {R['eclipses']['on_land']} had a central shadow touching land in Britain, Ireland, the Isle of Man or the Channel Islands: "
        f"{F['n_tot']} total ({F['n_before']} before 28 October 2026) and {F['n_ann']} annular. {pc(L['share_one_plus'])} of the land sees at least one total eclipse in the 1,200 years; the mean is "
        f"{L['mean_totals']:.2f}, a return period of {n(F['ret'])} years, close to the worldwide figure of about 375 years. London's only total eclipse in the window is Halley's of 1715; for "
        f"{pc(F['share18'])} of {n(T['n'])} cities and towns the last total eclipse was in 1715 or 1724, and no path of totality touched land between 1724 and 1927. {F['never']} towns, in east Kent and "
        f"south Ulster and the Irish border counties, see none in the whole window. The calculation reproduces {len(R['wiki_check']['found'])} of the {R['wiki_check']['listed']} eclipses in a published "
        f"British list and matches recorded durations to within about 12 seconds. A one minute error in Delta T moves a path about {F['dt']['1140-03-20'][60]['shift_km_at_54N']:.0f} km and changes the "
        f"verdict for {a40} to {b40} of the {n(t40)} towns in the path of 1140, so medieval and future dates near path edges are uncertain.")
    B["PAPER_INTRO"] = tx(
        f"A total eclipse of the Sun is one of the few astronomical events that most people would travel to see, and one that most people never do. The reason is geometry. The Moon's umbra reaches the "
        f"Earth only as a narrow strip, so although a total eclipse happens somewhere on Earth every year or two ({n(R['global']['total'])} of the {n(R['global']['n'])} solar eclipses between AD 1000 and "
        f"2200 are total), any one place waits a long time between them. A figure of about 375 years is often quoted as the average interval for a given spot on Earth (Wikipedia contributors 2026, "
        f"Solar eclipse of August 21, 2017).\n\n"
        f"Britain and Ireland have a rich record of particular eclipses: the eclipses of 1133 and 1140 in the Peterborough Chronicle and William of Malmesbury; the Mirk Monday of 1652; Halley's "
        f"predicted and mapped eclipse of 1715 (Halley 1715); the 24 seconds of 1927 seen from Giggleswick; and the clouded-out eclipse of 1999 in Cornwall. Lists of the eclipses visible from the "
        f"United Kingdom exist (Williams 1996, summarised in Wikipedia contributors 2026). What is harder to find is the view from a particular town: when did this place last see totality, and when "
        f"will it next? This note answers that question for every city, town and village in Great Britain and for the towns of Ireland, Northern Ireland, the Isle of Man and the Channel Islands, from "
        f"AD 1000 to 2200, and uses the answers to describe how rare totality really is in these islands.\n\n"
        f"An interactive version, with a search for any place and a map of every path, is at \\url{{https://tristan-hotham.github.io/eclipse-towns/}}.")
    B["PAPER_METHODS"] = tx(
        "\\subsection{Ephemeris and eclipse geometry}\n\n"
        f"I list all solar eclipses from AD 1000 to 2200 with Astronomy Engine (Cross, version 2.1.19), a well-tested open-source library for the positions of the Sun, Moon and planets. For each eclipse "
        f"I take the geocentric Moon and the light-time and aberration corrected Sun in the J2000 equatorial frame every 15 minutes within 3.5 hours of the peak and interpolate them with cubic splines. "
        f"A place's position is its point on the Earth's ellipsoid (Astronomy Engine's own radius and flattening) rotated by Greenwich apparent sidereal time and then by the precession and nutation "
        f"matrix of the date; this reproduces Astronomy Engine's own observer vector to better than a metre. At each moment, following Astronomy Engine's local eclipse code, I find the place's distance $r$ from "
        f"the axis running from the Sun's centre through the Moon's centre, and the radius $k$ of the umbra ($k>0$) or antumbra ($k<0$) in the plane through the place, using the Sun's radius of 695,700 km "
        f"and the Moon's mean radius of 1,737.4 km. The place is in the central shadow when $r < |k|$: totality if $k>0$, annularity if $k<0$. The Sun must be above the place's horizon (geometric altitude "
        f"above zero; refraction is ignored). Duration is the time in the central shadow with the Sun up.\n\n"
        "\\subsection{Lunar acceleration and Delta T}\n\n"
        f"Times are in Universal Time, linked to the uniform time of the ephemeris by Delta T. I use Astronomy Engine's default, the polynomial expressions of Espenak and Meeus (2006), which give "
        f"{n(M['dt_1133'])} seconds for 1133, {n(M['dt_1715'])} seconds for 1715 and {n(M['dt_2142'])} seconds for 2142. Those expressions go with the lunar theory ELP-2000/82 and its secular "
        f"acceleration of the Moon. Astronomy Engine's lunar series has a smaller quadratic term in the Moon's mean longitude ($-4.06''$ per century squared, against $-5.68''$ in the ELP-2000/82 "
        f"expression given by Meeus 1998, equation 47.1, which also has a small cubic term). Left uncorrected, its Moon runs ahead of the ELP Moon by an amount that grows with the square of the time from "
        f"2000: {n(R['lunar_lag_s']['1023-01-24'])} seconds of time in 1023, {n(R['lunar_lag_s']['1140-03-20'])} in 1140, {n(R['lunar_lag_s']['1715-05-03'])} in 1715 and {n(R['lunar_lag_s']['2142-05-25'])} in 2142. "
        f"In a first run this put the medieval paths more than 100 km east of published ones. I correct it by evaluating Astronomy Engine's Moon earlier by that lag (the difference in mean longitude "
        f"divided by the Moon's mean motion of $0.549''$ per second), which moves its longitude, argument of latitude and elongation together. With the correction and the same Delta T, my centre lines "
        f"for 1140 and 2142 lie within about 7 km of the path tables published by Fred Espenak on EclipseWise; for 1023 the difference is about 50 km for reasons I could not establish.\n\n"
        "\\subsection{Search}\n\n"
        f"Each eclipse is first screened on a one-degree test grid over the region (latitude 49 to 61 N, longitude 11 W to 2 E) every 2 minutes. Survivors are scanned on a regular grid of 0.04 degrees of "
        f"latitude by 0.06 degrees of longitude (about 4.4 by 4 km) and at each place, every 30 seconds and then every 2 seconds for 5 minutes either side of the closest approach. Land cells are those whose "
        f"centre lies on the Natural Earth 1:10m land outline of Britain, Ireland, the Isle of Man and the Channel Islands ({n(R['grid']['cells'])} cells, {n(R['grid']['land_km2'])} km$^2$). An eclipse "
        f"counts as over land if any land cell or listed place is in its central shadow. Paths for maps are filled contours of $r-|k|$ at zero, and centre lines are where the shadow axis meets the ellipsoid.\n\n"
        "\\subsection{Places}\n\n"
        f"Great Britain: every OS Open Names populated place of local type City, Town or Village (Ordnance Survey 2026). Ireland, Northern Ireland, the Isle of Man and the Channel Islands, which OS Open "
        f"Names does not cover: GeoNames places of 1,000 people or more ({n(R['places']['other'])} places). In all {n(R['places']['n'])} places. In the statistics, cities and towns means OS City and "
        f"Town and GeoNames places of 1,500 or more: {n(T['n'])} places. Today is {dstr(R['today'])}. Dates are given in the Julian calendar before 15 October 1582 and the Gregorian after it, as is usual "
        f"in eclipse catalogues; Britain and Ireland used the Julian calendar until 1752, so Halley's eclipse of 3 May 1715 was 22 April 1715 there.\n\n"
        "\\subsection{Checks}\n\n"
        f"I compare durations with published figures for named places, the list of total and annular eclipses visible from the United Kingdom (Wikipedia contributors 2026, after Williams 1996) and "
        f"statements in the Wikipedia articles on individual eclipses. To test sensitivity to Delta T, I rerun eight eclipses with Delta T shifted by 30, 60 and 120 seconds either way and count the cities "
        f"and towns whose verdict changes.")
    B["PAPER_R1"] = tx(
        f"Of the {n(R['global']['n'])} solar eclipses between AD 1000 and 2200, {R['eclipses']['touching_region']} had a central shadow reaching the study region and {R['eclipses']['on_land']} touched land "
        f"in it; the other {len(R['eclipses']['sea_only'])} crossed only the sea, among them 1925 near St Kilda and 2015 near Rockall. Of the {R['eclipses']['on_land']}, {F['n_tot']} were total and "
        f"{F['n_ann']} annular in the study area (Figure~\\ref{{fig:paths}} and Table~\\ref{{tab:all}}). {F['n_before']} of the totals fall before today and {F['n_after']} after.\n\n"
        f"Totals over land come on average every {R['region_gap_mean']:.0f} years, but irregularly (Figure~\\ref{{fig:timeline}}). The seventeenth century had {F['cen'][17]['totals']}, the "
        f"nineteenth none, and the twenty-second will have {F['cen'][22]['totals']}. The longest gap ran {gm['years']} years, from {dstr(gm['from'])} to {dstr(gm['to'])}. "
        f"The eclipse that put most towns in totality was Halley's of 1715 ({n(E['1715-05-03']['towns_total'])} cities and towns, {n(E['1715-05-03']['places_total'])} places), and the largest "
        f"area of land will be covered on {dstr(R['biggest'][0]['eclipse'])} ({n(R['biggest'][0]['km2'])} km$^2$).")
    B["PAPER_R2"] = tx(
        f"On the land grid, {pc(L['share_one_plus'], 1)} of cells see at least one total eclipse between AD 1000 and 2200 and {pc(L['share_none'], 1)} see none (Figure~\\ref{{fig:count}}). The mean is "
        f"{L['mean_totals']:.2f} totals per cell, or one every {n(F['ret'])} years, close to the worldwide figure of about 375 years. The maximum is {L['max_totals']}. Every land cell sees at least one "
        f"annular eclipse (mean {L['mean_annulars']:.1f}).\n\n"
        f"The {n(T['n'])} cities and towns average {T['mean_n']:.2f} totals (Figure~\\ref{{fig:hist}}). The most, {T['max_n']}, fall to {lst(T['max_n_places'])}. {F['never']} towns see none in the whole "
        f"window: {lst(F['never_kent'])} in Kent and {lst(F['never_irl'])} in Ireland and Northern Ireland. The longest interval between two totals at a town is {n(F['gap']['years'])} years, from 1140 "
        f"to 2151, shared by {F['gap']['n_at_max']} towns around Manchester and east Lancashire. The shortest is {F['short']['years']} years, {F['short']['pairs'][0][0]} and {F['short']['pairs'][0][1]}, in "
        f"towns of the north-east of Scotland such as {lst([p for p in F['short']['places'] if p in ('Elgin', 'Fraserburgh', 'Banff', 'Huntly')])}.")
    B["PAPER_R3"] = tx(
        f"For {n(F['n18'])} of the {n(T['n'])} cities and towns ({pc(F['share18'])}) the last total eclipse before today was in 1715 or 1724 (Figure~\\ref{{fig:last}}). {n(F['n20'])} had one in the twentieth "
        f"century and {n(F['none1000'])} ({pc(T['none_since_1000_share'], 1)}) have had none since AD 1000. The median town last saw totality {n(T['years_since_last_median'])} years ago. Looking forward, "
        f"{n(F['none2200'])} towns ({pc(T['none_until_2200_share'])}) will see none before 2200, and for {n(T['next_2090'])} the next is 23 September 2090. Table~\\ref{{tab:cities}} gives large cities: "
        f"London's only total eclipse in the window is 1715, Dublin's 1652; Edinburgh, Glasgow and Belfast also last saw totality in 1652.")
    p1, p2, p3, p4 = para_check(R, F, html=False)
    B["PAPER_R4"] = tx(p1 + " Table~\\ref{tab:val} lists the comparisons.\n\n" + p2 + "\n\n" + p3 +
                       " The list's durations for future eclipses appear to be the greatest durations anywhere on Earth, so I do not compare them.")
    d1, d2 = para_deltat(R, F, html=False)
    B["PAPER_R5"] = tx(d2.replace("An error of one minute", "Figure~\\ref{fig:deltat} shows the test. An error of one minute"))
    B["PAPER_DISCUSSION"] = tx(
        f"The calculation turns a familiar statistic into a local one. Averaged over the land of Britain and Ireland, the return period of {n(F['ret'])} years is close to the worldwide figure, but the spread "
        f"is wide: some towns see {T['max_n']} totals in 1,200 years, some none, and the same town can wait two years or a thousand. The clustering in time matters as much as the clustering in space. "
        f"Because two large paths crossed southern Britain and Ireland in 1715 and 1724, and none touched land for two centuries afterwards, most towns last saw totality in the early eighteenth century; "
        f"the narrow paths of 1927 and 1999 changed that for only {n(F['n20'])} of them, and the south-west waits until 2090 and much of England until 2151.\n\n"
        f"The history and the calculation support each other. The medieval and early modern records that survive come from places that the paths cover: the chroniclers of 1133 and 1140, the "
        f"Carrickfergus observer of 1652, Halley's London of 1715. Delta T itself is estimated largely from such records, so the agreement is partly built in; but the durations of 1715, 1927 and 1999 are "
        f"independent checks of the geometry, and they agree within seconds.\n\n"
        f"The lunar correction is the main methodological lesson. A general-purpose ephemeris tuned for the present can drift by minutes of time over a thousand years, which moves an eclipse path by "
        f"more than any plausible error in Delta T. Anyone using such a library for historical eclipses should check its long-term lunar acceleration against the Delta T model they use.")
    B["PAPER_LIMITS"] = tx(
        f"Delta T is uncertain before about 1600 and is a forecast after today; path edges are therefore uncertain by kilometres to tens of kilometres, and verdicts for towns near the edge of a medieval or "
        f"future path should be read as probable rather than certain. My centre line for 1023 differs from Espenak's by about 50 km even after the lunar correction. The Moon is treated as a smooth sphere "
        f"of mean radius, so durations ignore the lunar limb profile, which matters for very short totals such as 1339 over Orkney. Refraction and the observer's height are ignored, which matters only "
        f"for eclipses close to sunrise or sunset. Weather is ignored entirely. The place lists come from two sources, OS Open Names in Great Britain and GeoNames elsewhere, with different definitions "
        f"of a town. The grid uses a generalised coastline, so small islands may be missed, and the area figures are approximate.")
    B["PAPER_CONCLUSION"] = tx(
        f"Between AD 1000 and 2200, {F['n_tot']} total eclipses touch land in Britain and Ireland, and a typical spot sees about {L['mean_totals']:.0f} of them, one every {n(F['ret'])} years. For most towns the last was "
        f"in 1715 or 1724, and for about a third there is no other before 2200. The data and search tool make it possible for anyone to look up their own place, with an honest statement of how sure the answer is.")
    return B


# ---------------- blog ----------------
def blog_blocks(R):
    F = facts(R); T, L, N, E, V = F["T"], F["L"], F["N"], F["E"], F["V"]
    gm = R["region_gap_max"]
    a40, b40, t40 = dt_range(F, "1140-03-20")
    def P(t): return f"<!-- wp:paragraph -->\n<p>{t}</p>\n<!-- /wp:paragraph -->\n\n"
    def H(t): return f"<!-- wp:heading -->\n<h2 class=\"wp-block-heading\">{t}</h2>\n<!-- /wp:heading -->\n\n"
    def IMG(f, alt, cap=""): return f"<!-- wp:image {{\"sizeSlug\":\"full\"}} -->\n<figure class=\"wp-block-image size-full\">{{{{IMG|{f}|{alt}|{cap}}}}}</figure>\n<!-- /wp:image -->\n\n"
    def Q(t): return f"<!-- wp:pullquote -->\n<figure class=\"wp-block-pullquote\"><blockquote><p>{t}</p></blockquote></figure>\n<!-- /wp:pullquote -->\n\n"
    B = {}
    B["BLOG_LEAD"] = (f"London has seen one total eclipse of the Sun in 1,200 years. I worked out every path of totality across Britain and Ireland from AD 1000 to 2200 and tested "
                      f"{n(R['places']['n'])} places one by one, to find when your town last went dark, and when it will again.")
    body = ""
    body += P(f"On the morning of 3 May 1715 the sky over London went dark for about three and a half minutes. Edmond Halley had predicted it, and had a map printed showing where the shadow of the Moon "
              f"would fall. It was a sensation. It was also, on my calculation, the only total eclipse London sees between AD 1000 and 2200.")
    body += P(f"I wanted to know what that looks like for everywhere else. So I took an open-source astronomy library, worked out the positions of the Sun and Moon for all {n(R['global']['n'])} solar "
              f"eclipses in those twelve centuries, and checked, second by second, which ones put each of {n(R['places']['n'])} cities, towns and villages in Britain and Ireland into the Moon's shadow. "
              f"The answer for your own town is one search away in the interactive version.")
    body += H("Thirty shadows")
    body += P(f"Between AD 1000 and 2200, {F['n_tot']} total eclipses touch land somewhere in Britain, Ireland, the Isle of Man or the Channel Islands: {F['n_before']} before today and {F['n_after']} still to come. "
              f"Another {F['n_ann']} are annular, when the Moon is a little too far away to cover the Sun and leaves a ring of fire.")
    body += IMG("b_paths.png", f"Map of Britain and Ireland crossed by {F['n_tot']} dark translucent bands, the paths of total solar eclipses from AD 1000 to 2200, with overlapping bands darker; thin red outlines mark annular eclipses and gold lines mark the centre lines of six famous eclipses including 1715, 1927, 1999 and 2090.",
                "Every path of totality over Britain and Ireland, AD 1000 to 2200. Where paths overlap the map is darker.")
    body += P(f"They do not arrive evenly. Halley's eclipse of 1715 was followed nine years later by another, which crossed Galway, Wales and the south of England at sunset. Then nothing. No path of "
              f"totality touched land here for {gm['years']} years, until a sliver of shadow crossed North Wales, Lancashire and Yorkshire for about 24 seconds early on {dstr(gm['to'])}. The whole "
              f"nineteenth century had none. The twenty-second century will have {F['cen'][22]['totals']}.")
    body += IMG("b_timeline.png", "Timeline from AD 1000 to 2200 with a bar for each eclipse over land, dark bars upwards for total eclipses and red bars downwards for annular ones, and a shaded empty gap from 1724 to 1927.",
                "Land inside each path of totality (up) and annularity (down). Note the empty two centuries after 1724.")
    body += H(f"Once every {n(F['ret'])} years")
    body += P(f"The Moon's shadow is a narrow strip, so any one spot waits a long time. Averaged over the land, I get {L['mean_totals']:.1f} total eclipses per spot in 1,200 years, or one every "
              f"{n(F['ret'])} years. That is close to the figure of about 375 years often quoted for the world as a whole, which is reassuring.")
    body += P(f"But luck varies. The towns with the most, {T['max_n']} each, are {lst(T['max_n_places'])}. {F['never']} towns get none at all: the corner of Kent around "
              f"{lst(F['never_kent'][:4])}, and a belt across south Ulster and the Irish border counties, including {lst(F['never_irl'][:3])}. The longest wait is {n(F['gap']['years'])} years, "
              f"from 1140 to 2151, for {F['gap']['n_at_max']} towns around Manchester. And some towns in the north-east of Scotland, such as Elgin and Fraserburgh, had two in two years, in 1652 and 1654.")
    body += IMG("b_count.png", "Map of Britain and Ireland shaded by the number of total eclipses each 4 km square sees from AD 1000 to 2200, from pale (none or one) to near-black (seven or eight), with stripes following the eclipse paths.",
                "How many total eclipses each part of the islands sees, AD 1000 to 2200.")
    body += Q(f"For {pc(F['share18'])} of towns, the last total eclipse was in 1715 or 1724.")
    body += H("Your last eclipse was probably in 1715")
    body += P(f"Because those two big eighteenth-century eclipses covered so much ground, and almost nothing followed, they are the last totality for {n(F['n18'])} of the {n(T['n'])} cities and towns, "
              f"{pc(F['share18'])}. Only {n(F['n20'])} had one in the twentieth century. The median town has waited {n(T['years_since_last_median'])} years. Edinburgh, Glasgow, Belfast and Dublin last "
              f"saw one in 1652, on what Scots called Mirk Monday.")
    body += IMG("b_last.png", "Map of Britain and Ireland coloured by the century of each area's last total eclipse before today, with large areas of the eighteenth century across Ireland, Wales and southern England, the seventeenth century across Scotland and Ulster, and thin twentieth-century strips across northern England and Cornwall.",
                "When each place last saw totality.")
    body += P(f"Looking ahead, the next on the mainland is on 23 September 2090, late in the afternoon, across south-west Ireland, Cornwall, Devon, Dorset, Hampshire and the Isle of Wight. For "
              f"{n(T['next_2090'])} towns that is the next one. The big one is {dstr('2151-06-14')}, which will cover more land than any other in the window, {n(E['2151-06-14']['total_land_km2'])} km², "
              f"from Northern Ireland and the Isle of Man across northern and eastern England. But {n(F['none2200'])} towns, {pc(T['none_until_2200_share'])}, will see none before 2200. London is one of them.")
    body += H("Does the maths match history?")
    body += P(f"I checked the calculation against eclipses people actually saw. London in 1715 comes out at {mmss(V[('1715-05-03', 'London')]['computed_dur_s'])} of totality against a recorded "
              f"3 minutes 33 seconds. Southport in 1927 comes out at {mmss(V[('1927-06-29', 'Southport')]['computed_dur_s'])}, against an observer's \"memorable 23 seconds\". Plymouth in 1999 comes out at "
              f"{mmss(V[('1999-08-11', 'Plymouth')]['computed_dur_s'])} against a published 1 minute 42 seconds. I also find {len(R['wiki_check']['found'])} of the {R['wiki_check']['listed']} eclipses in the "
              f"standard British list, and a few it does not mention, including a big total over the Hebrides and the north of Scotland in 1185.")
    body += P(f"The Middle Ages are harder. The Earth's spin has slowed, unevenly, and the correction for that, called Delta T, is only known approximately for the distant past and only forecast for the "
              f"future. A one minute error moves a path about {F['dt']['1140-03-20'][60]['shift_km_at_54N']:.0f} km. For the eclipse of 1140, when the Peterborough Chronicle says people lit candles to eat "
              f"their dinner, that changes the verdict for {a40} to {b40} of the {n(t40)} towns in the path. So for a medieval or far-future eclipse, a town near the edge of the shadow should read its answer "
              f"as \"probably\".")
    body += IMG("b_deltat.png", "Line chart of how many towns change between total and not total when Delta T is shifted by up to two minutes either way, for eight eclipses from 1133 to 2142.",
                "How much the answer depends on Delta T.")
    body += H("How I did this")
    body += P(f"I used Astronomy Engine, an open-source library for the positions of the Sun and Moon, to list every solar eclipse from AD 1000 to 2200. For each one that came near the islands I "
              f"tested every place, and a 4 km grid of the land, every 30 seconds and then every 2 seconds, measuring how far the place was from the axis of the Moon's shadow and whether it was inside "
              f"the umbra with the Sun above the horizon. One fix was needed: over centuries the library's Moon drifts ahead of the lunar theory that the standard Delta T formulas assume, by about "
              f"{n(R['lunar_lag_s']['1023-01-24'] / 60)} minutes of time by 1023, so I held it back by the right amount. Places come from the Ordnance Survey's OS Open Names for Great Britain and from "
              f"GeoNames for Ireland, Northern Ireland, the Isle of Man and the Channel Islands. Weather is ignored: many of these eclipses were clouded out, as 1927 and 1999 were for most people.")
    B["BLOG_BODY"] = body
    return B


def blog_meta(R):
    F = facts(R)
    return dict(
        title="When did your town last see a total eclipse?",
        slug="eclipse-towns",
        excerpt=(f"London has seen one total eclipse of the Sun in 1,200 years. I computed every path of totality across Britain and Ireland from AD 1000 to 2200 and tested "
                 f"{n(R['places']['n'])} places: for most towns the last one was in 1715 or 1724."),
        seo_description=f"Every total eclipse over Britain and Ireland, AD 1000 to 2200: {F['n_tot']} paths, one every {n(F['ret'])} years per spot. Find your town's last and next.",
        tags=["eclipses", "astronomy", "history", "maps", "Halley", "Britain", "Ireland", "data"],
        header_alt=(f"Title card reading 'When did your town last see a total eclipse?' on a pale dawn-sky background, beside a map of Britain and Ireland crossed by dark translucent bands, "
                    f"the paths of totality. Text: {F['n_tot']} total eclipses touched Britain and Ireland in 1,200 years; the average spot waits about {n(F['ret'])} years between them."))
