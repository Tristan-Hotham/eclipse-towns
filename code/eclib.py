"""Shared eclipse geometry, vectorised over many places, built on Astronomy Engine (MIT licence,
https://github.com/cosinekitty/astronomy).

For one eclipse I take the geocentric Moon (GeoMoon) and the light-time and aberration corrected Sun
(GeoVector) in the J2000 equatorial frame at nodes every 15 minutes around the peak and interpolate them
with cubic splines. Each place's position is its WGS84-style ellipsoid point (Astronomy Engine's own
Earth radius and flattening) turned by Greenwich apparent sidereal time and then by the precession and
nutation matrix of the date. This reproduces Astronomy Engine's ObserverVector to a few metres.

The test at a place and moment follows Astronomy Engine's local eclipse code: the shadow axis runs from
the Sun's centre through the Moon's centre; r is the place's distance (km) from that axis and k the radius
of the umbra (k > 0) or antumbra (k < 0) in the plane through the place. The place is inside the central
shadow when g = r - |k| < 0: total if k > 0, annular if k < 0. The Sun must also be above the place's
horizon (geometric altitude above 0 degrees, no refraction).
Times are Astronomy Engine 'ut' values: days since 2000-01-01 12:00 UT. Delta T is Astronomy Engine's
default (the Espenak and Meeus polynomials) unless set with astronomy.SetDeltaTFunction.
"""
import math
import numpy as np
import astronomy as A
from scipy.interpolate import CubicSpline

KM_AU = A.KM_PER_AU
RS = 695700.0          # Sun radius km (Astronomy Engine)
RM = 1737.4            # Moon mean radius km (Astronomy Engine)
RE = 6378.1366         # Earth equatorial radius km (Astronomy Engine)
FL = 0.996647180302104 # polar / equatorial radius (Astronomy Engine)


def ecef(lat, lon):
    """Geocentric Earth-fixed position (km) and unit up vector for geodetic lat, lon (deg), height 0."""
    la = np.radians(lat); lo = np.radians(lon)
    c = 1.0 / np.sqrt(np.cos(la) ** 2 + (FL * np.sin(la)) ** 2); s = FL * FL * c
    x = RE * c * np.cos(la) * np.cos(lo); y = RE * c * np.cos(la) * np.sin(lo); z = RE * s * np.sin(la)
    up = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1)
    return np.stack([x, y, z], -1), up


# Astronomy Engine's lunar series has a smaller quadratic term in the Moon's mean longitude (-4.056"/cy^2,
# from -0.00000313 rev) than the ELP-2000/82 value in Meeus, Astronomical Algorithms (2nd ed.), eq. 47.1
# (-0.0015786 deg = -5.683"/cy^2, plus +T^3/538841 deg). The Espenak and Meeus Delta T polynomials go with the
# ELP value. Left alone, the difference puts Astronomy Engine's Moon ahead in its orbit by about
# 1.63"/cy^2: some 160" (five minutes of time) in AD 1023, 25 seconds in 1715, nothing today. I correct it by
# evaluating the Moon that much earlier (its mean motion is 0.549"/s), which shifts its longitude, argument of
# latitude and elongation together.
LUNAR_FIX = True
MOON_ARCSEC_PER_S = 481267.88123421 * 3600 / (36525 * 86400)


def lunar_lag_seconds(tt):
    T = tt / 36525.0
    return ((-0.00000313 * 1296000) * T * T - (-0.0015786 * 3600 * T * T + 3600 * T ** 3 / 538841)) / MOON_ARCSEC_PER_S


class Eclipse:
    """Sun, Moon and Earth-orientation model around one eclipse peak (ut days)."""

    def __init__(self, peak_ut, half_hours=3.5, step_min=15):
        self.peak = peak_ut
        n = int(round(half_hours * 60 / step_min))
        self.nodes = peak_ut + np.arange(-n, n + 1) * step_min / 1440.0
        S = []; M = []; G = []
        for u in self.nodes:
            t = A.Time(u)
            s = A.GeoVector(A.Body.Sun, t, True)
            m = A.GeoMoon(A.Time(u - lunar_lag_seconds(t.tt) / 86400.0) if LUNAR_FIX else t)
            S.append([s.x, s.y, s.z]); M.append([m.x, m.y, m.z]); G.append(A.SiderealTime(t))
        self.sun = CubicSpline(self.nodes, np.array(S) * KM_AU)
        self.moon = CubicSpline(self.nodes, np.array(M) * KM_AU)
        G = np.degrees(np.unwrap(np.radians(np.array(G) * 15.0)))
        self.gast = CubicSpline(self.nodes, G)
        r = A.Rotation_EQD_EQJ(A.Time(peak_ut)).rot   # rot[i][j]: Astronomy Engine row-major convention
        self.P = np.array(r).T                         # so that v_eqj = P @ v_eqd

    def frame(self, t):
        """Earth-fixed to J2000 rotation matrices for times t (array) -> (..., 3, 3)."""
        th = np.radians(self.gast(t))
        c, s = np.cos(th), np.sin(th)
        Rz = np.zeros(t.shape + (3, 3)); Rz[..., 0, 0] = c; Rz[..., 0, 1] = -s; Rz[..., 1, 0] = s; Rz[..., 1, 1] = c; Rz[..., 2, 2] = 1
        return self.P @ Rz

    def g(self, t, pos, up):
        """t: times (n_pts, n_t); pos, up: (n_pts, 3) Earth-fixed. Returns g (km), k (km), sun altitude sin."""
        F = self.frame(t)                                  # (p, t, 3, 3)
        o = np.einsum("ptij,pj->pti", F, pos)             # observer, J2000, km
        u_ = np.einsum("ptij,pj->pti", F, up)
        s = self.sun(t); m = self.moon(t)                  # (p, t, 3)
        d = m - s                                          # Sun to Moon direction
        lo = o - m                                         # lunacentric observer
        uu = np.einsum("pti,pti->pt", d, lo) / np.einsum("pti,pti->pt", d, d)
        r = np.linalg.norm(uu[..., None] * d - lo, axis=-1)
        k = RS - (1.0 + uu) * (RS - RM)
        so = s - o
        alt = np.einsum("pti,pti->pt", so, u_) / np.linalg.norm(so, axis=-1)
        return r - np.abs(k), k, alt


def scan(ecl, lat, lon, t0, t1, coarse_s=60, fine_s=2, fine_half_s=300, thresh_km=400, chunk=2000):
    """For places (lat, lon arrays) find min g over [t0, t1] (ut days) and the central duration.
    Returns dict of arrays: gmin (km, at the best sunlit moment), kind (+1 total, -1 annular, 0 none),
    dur (seconds of central eclipse with the Sun up), tmax (ut of minimum g)."""
    pos, up = ecef(np.asarray(lat, float), np.asarray(lon, float))
    n = len(pos); out = dict(gmin=np.full(n, np.inf), kind=np.zeros(n, int), dur=np.zeros(n), tmax=np.full(n, np.nan))
    tc = np.arange(t0, t1 + 1e-9, coarse_s / 86400.0)
    for a in range(0, n, chunk):
        b = min(n, a + chunk); P, U = pos[a:b], up[a:b]
        T = np.broadcast_to(tc, (b - a, len(tc)))
        g, k, alt = ecl.g(T, P, U)
        gg = np.where(alt > -0.02, g, np.inf)
        j = np.argmin(gg, axis=1); gm = gg[np.arange(b - a), j]
        out["gmin"][a:b] = gm
        sel = np.where(gm < thresh_km)[0]
        if len(sel) == 0:
            continue
        off = np.arange(-fine_half_s, fine_half_s + 1e-9, fine_s) / 86400.0
        Tf = tc[j[sel]][:, None] + off[None, :]
        g2, k2, alt2 = ecl.g(Tf, P[sel], U[sel])
        g2s = np.where(alt2 > 0, g2, np.inf)
        jj = np.argmin(g2s, axis=1); idx = np.arange(len(sel))
        gm2 = g2s[idx, jj]
        out["gmin"][a + sel] = gm2
        out["tmax"][a + sel] = Tf[idx, jj]
        cen = gm2 < 0
        kind = np.where(k2[idx, jj] > 0, 1, -1) * cen
        out["kind"][a + sel] = kind
        # duration: linear interpolation of the sunlit g < 0 segments
        h = np.where(alt2 > 0, g2, np.abs(g2) + 1.0)
        neg = h < 0
        both = neg[:, 1:] & neg[:, :-1]
        one = neg[:, 1:] ^ neg[:, :-1]
        a1, a2 = h[:, :-1], h[:, 1:]
        frac = np.where(one, np.abs(np.minimum(a1, a2)) / (np.abs(a1) + np.abs(a2) + 1e-12), 0)
        out["dur"][a + sel] = (both.sum(1) + frac.sum(1)) * fine_s * cen
    return out


def centreline(ecl, t0, t1, step_s=10):
    """Where the shadow axis meets the ellipsoid, for times t0..t1 (ut days). Returns arrays t, lat, lon
    (geodetic degrees); points where the axis misses the Earth are dropped."""
    t = np.arange(t0, t1 + 1e-9, step_s / 86400.0)
    s = ecl.sun(t); m = ecl.moon(t); d = m - s; d = d / np.linalg.norm(d, axis=-1)[:, None]
    F = ecl.frame(t)                                   # Earth-fixed -> J2000
    Ft = np.transpose(F, (0, 2, 1))
    m_e = np.einsum("tij,tj->ti", Ft, m); d_e = np.einsum("tij,tj->ti", Ft, d)
    sc = np.array([1.0, 1.0, 1.0 / FL])                # squash the ellipsoid to a sphere of radius RE
    M = m_e * sc; Dv = d_e * sc
    a = (Dv * Dv).sum(1); b = 2 * (M * Dv).sum(1); c = (M * M).sum(1) - RE * RE
    disc = b * b - 4 * a * c
    ok = disc >= 0
    lam = (-b - np.sqrt(np.where(ok, disc, 0))) / (2 * a)
    p = (m_e + lam[:, None] * d_e)
    lon = np.degrees(np.arctan2(p[:, 1], p[:, 0]))
    rxy = np.hypot(p[:, 0], p[:, 1])
    lat = np.degrees(np.arctan2(p[:, 2], rxy * FL * FL))  # geodetic latitude on the ellipsoid
    return t[ok], lat[ok], lon[ok]
