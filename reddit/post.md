## Title

[OC] When did your town last see a total eclipse? I computed every path of totality over Britain and Ireland from AD 1000 to 2200 for 17,103 places: 30 total eclipses touched land, the average spot waits 359 years, and London's only one was Halley's eclipse of 1715

## Body

I used an open-source astronomy library to compute every solar eclipse from AD 1000 to 2200 and tested each city, town and village in Britain and Ireland second by second.

For 54% of the 1,819 cities and towns, the last total eclipse was in 1715 or 1724; after that no path of totality touched land for 203 years, until a 24-second eclipse in 1927. Fifteen towns, including Ashford and Folkestone in Kent, get none at all in the 1,200 years. The next one on the mainland is 23 September 2090, Cornwall to the Isle of Wight.

Caveat: medieval and far-future path edges are uncertain by kilometres to tens of kilometres, because of how the Earth's rotation has slowed (Delta T). Weather is ignored.

Search your town: https://tristan-hotham.github.io/eclipse-towns/

## Source comment

Source: own calculation with Astronomy Engine by Don Cross (MIT licence, https://github.com/cosinekitty/astronomy), Delta T from the Espenak and Meeus formulas (NASA Five Millennium Canon of Solar Eclipses), lunar acceleration corrected to ELP-2000/82 (Meeus, Astronomical Algorithms); places from Ordnance Survey OS Open Names (Contains OS data © Crown copyright and database right 2026, Open Government Licence v3.0) and GeoNames cities1000 (CC BY 4.0); coastline Natural Earth (public domain); historical checks against English Wikipedia (List of solar eclipses visible from the British Isles and articles on individual eclipses, CC BY-SA 4.0).

Tools: Python (numpy, scipy, shapely, contourpy, astronomy-engine, matplotlib).

Interactive version: https://tristan-hotham.github.io/eclipse-towns/
Blog post: https://blog.tristanhotham.com/2026/10/28/eclipse-towns/
Paper and data: https://doi.org/10.5281/zenodo.23729635
