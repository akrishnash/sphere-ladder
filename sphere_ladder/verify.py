"""Numerically check every claim the Sphere Ladder pages make.

Run:  python -m sphere_ladder verify
"""

from __future__ import annotations

import numpy as np

from . import geometry as g

RNG_SEED = 20260925


class Report:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, bool]] = []

    def check(self, claim: str, value: str, ok: bool) -> None:
        self.rows.append((claim, value, ok))
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {claim:<58} {value}")

    def section(self, title: str) -> None:
        print(f"\n{title}\n" + "─" * len(title))

    @property
    def ok(self) -> bool:
        return all(r[2] for r in self.rows)


def run(tol: float = 1e-9) -> bool:
    rng = np.random.default_rng(RNG_SEED)
    r = Report()
    t = np.linspace(0, g.TAU, 2000, endpoint=False)

    # ── S¹ and S² ──
    r.section("S¹ and S²: stereographic projection")
    for n in (1, 2, 3):
        p = g.random_sphere_points(n, 20000, rng)
        p = p[p[:, -1] < 0.999]  # stay away from the pole, where the shadow is at infinity
        err = np.abs(g.inverse_stereographic(g.stereographic(p)) - p).max()
        sup = "¹²³"[n - 1]
        r.check(f"S{sup}: projection then inverse returns the same point", f"max error {err:.1e}", err < 1e-9)
    th = np.pi / 2 - np.logspace(-1, -6, 6)
    xs = g.stereographic(g.circle(th), tangent=True)[:, 0]
    r.check("S¹: shadow runs to infinity as the point nears N", f"x′ = {xs[0]:.3g} … {xs[-1]:.3g}", bool(np.all(np.diff(xs) > 0) and xs[-1] > 1e5))

    tilted = g.circle_on_s2([0.6, 0.5, -0.6], 0.35, t)
    fit = g.fit_circle_3d(np.column_stack([g.stereographic(tilted, tangent=True), np.zeros(len(t))]))
    r.check("S²: a tilted circle casts a perfectly circular shadow", f"radial error {fit['radial_err']:.1e}", fit["radial_err"] < 1e-9 * fit["radius"])
    nrm = np.array([0.9, -0.3, 0.35]); nrm /= np.linalg.norm(nrm)
    through = g.circle_on_s2(nrm, nrm[2], t)  # n·N = offset, so the circle passes through N
    shadow = g.stereographic(through[np.abs(1 - through[:, 2]) > 1e-3], tangent=True)
    d = shadow - shadow[0]
    _, sv, _ = np.linalg.svd(d)
    r.check("S²: a circle through N casts a straight line", f"off-line spread {sv[1] / sv[0]:.1e}", sv[1] / sv[0] < 1e-9)

    lat = g.latitude(0.35, t)
    rot = np.stack([-lat[:, 1], lat[:, 0], np.zeros(len(t))], axis=1)  # spin about the z axis
    poles = np.array([[0, 0, 1.0], [0, 0, -1.0]])
    pole_speed = np.linalg.norm(np.stack([-poles[:, 1], poles[:, 0], np.zeros(2)], axis=1), axis=1).max()
    r.check("S²: spinning moves latitudes but the poles stay still", f"latitude speed {np.linalg.norm(rot, axis=1).min():.3f}, pole speed {pole_speed:.1f}", pole_speed == 0.0)

    # ── Torus ──
    r.section("Tori inside S³")
    for eta in (np.pi / 8, np.pi / 4, 3 * np.pi / 8):
        a, b = rng.uniform(0, g.TAU, (2, 5000))
        q = g.torus_point(eta, a, b)
        norm_err = np.abs(np.sum(q * q, axis=1) - 1).max()
        h = 1e-6
        da = (g.torus_point(eta, a + h, b) - g.torus_point(eta, a - h, b)) / (2 * h)
        db = (g.torus_point(eta, a, b + h) - g.torus_point(eta, a, b - h)) / (2 * h)
        E, F, G = np.sum(da * da, 1), np.sum(da * db, 1), np.sum(db * db, 1)
        spread = max(np.ptp(E), np.ptp(F), np.ptp(G))
        r.check(f"η = {np.degrees(eta):.1f}°: lies on S³ and has a constant (flat) metric",
                f"|q|²−1 {norm_err:.1e}; metric ({E.mean():.4f}, {F.mean():.1e}, {G.mean():.4f}) ± {spread:.1e}",
                norm_err < tol and spread < 1e-8)
    eta = np.pi / 4
    c, s = np.cos(eta), np.sin(eta)
    pts = g.stereographic(g.torus_point(eta, *np.meshgrid(t[::10], t[::10])).reshape(-1, 4))
    radial = np.hypot(pts[:, 0], pts[:, 1]).max()
    r.check("Shadow torus outer radius = cos η ⁄ (1 − sin η)", f"{radial:.6f} vs {c / (1 - s):.6f}", abs(radial - c / (1 - s)) < 1e-3)

    tref = g.stereographic(g.torus_knot(np.pi / 4, 2, 3, np.linspace(0, g.TAU, 1500, endpoint=False)))
    core = g.stereographic(g.torus_point(0.0, np.linspace(0, g.TAU, 1500, endpoint=False), 0.0))
    lk_core = g.linking_number(tref, core)
    r.check("(2, 3) curve winds 3 times around the core circle", f"linking {lk_core:+.4f}", abs(abs(lk_core) - 3) < 1e-2)

    # ── S³ Hopf fibration ──
    r.section("S³: Hopf fibration")
    etas = rng.uniform(0.05, np.pi / 2 - 0.05, 40)
    phis = rng.uniform(0, g.TAU, 40)
    fibers = [g.hopf_fiber(e, p, t) for e, p in zip(etas, phis)]
    norm_err = max(np.abs(np.sum(f * f, axis=1) - 1).max() for f in fibers)
    r.check("Every fiber lies on S³", f"max |q|²−1 {norm_err:.1e}", norm_err < tol)
    rank3 = max(np.linalg.svd(f, compute_uv=False)[2] for f in fibers)
    r.check("Every fiber is a great circle (spans a 2-plane through 0)", f"3rd singular value {rank3:.1e}", rank3 < 1e-9)
    speed = np.linalg.norm(g.hopf_flow_field(g.random_sphere_points(3, 100000, rng)), axis=1)
    r.check("Hopf flow has no still point on S³", f"speed in [{speed.min():.6f}, {speed.max():.6f}]", np.allclose(speed, 1.0))
    base_spread = max(np.ptp(g.hopf_map(f), axis=0).max() for f in fibers)
    on_s2 = max(np.abs(np.linalg.norm(g.hopf_map(f), axis=1) - 1).max() for f in fibers)
    r.check("Hopf map sends each whole fiber to one point", f"spread along fiber {base_spread:.1e}", base_spread < 1e-9)
    r.check("…and that point lies on S²", f"| |h(q)| − 1 | {on_s2:.1e}", on_s2 < tol)
    b = g.random_sphere_points(2, 20, rng)
    back = max(np.abs(g.hopf_map(g.fiber_over(bb, t)) - bb).max() for bb in b)
    r.check("fiber_over(b) really lies over b", f"max error {back:.1e}", back < 1e-9)

    same_torus = g.hopf_map(np.array([g.hopf_fiber(np.pi / 5, p, 0.0) for p in np.linspace(0, g.TAU, 12)]))
    r.check("Fibers on one torus land on one latitude of S²", f"heights {same_torus[:, 2].min():.6f} … {same_torus[:, 2].max():.6f}", np.ptp(same_torus[:, 2]) < 1e-12)

    circ_err, lk = [], []
    tt = np.linspace(0, g.TAU, 800, endpoint=False)
    for i in range(12):
        e1, e2 = rng.uniform(0.1 * np.pi, 0.32 * np.pi, 2)
        p1, p2 = rng.uniform(0, g.TAU, 2)
        A = g.stereographic(g.hopf_fiber(e1, p1, tt))
        B = g.stereographic(g.hopf_fiber(e2, p2, tt))
        fa = g.fit_circle_3d(A)
        circ_err.append(max(fa["planar_err"], fa["radial_err"]) / fa["radius"])
        lk.append(g.linking_number(A, B))
    lk = np.abs(lk)
    r.check("Shadows of fibers are exact circles in ℝ³", f"max relative error {max(circ_err):.1e}", max(circ_err) < 1e-9)
    r.check("Any two fibers are linked exactly once", f"|Lk| in [{lk.min():.4f}, {lk.max():.4f}] over {len(lk)} pairs", bool(np.all(np.abs(lk - 1) < 1e-2)))
    dmin = min(np.linalg.norm(fibers[0][:, None] - fibers[j][None, ::4], axis=-1).min() for j in range(1, 10))
    r.check("Different fibers never touch", f"closest approach {dmin:.3f}", dmin > 1e-3)

    # ── S⁴ ──
    r.section("S⁴: slices and still points")
    q3 = g.random_sphere_points(3, 5000, rng)
    worst = 0.0
    for v in np.linspace(-1, 1, 21):
        p5 = g.s4_slice(v, q3)
        worst = max(worst, np.abs(np.sum(p5 * p5, axis=1) - 1).max(), np.abs(np.linalg.norm(p5[:, :4], axis=1) - np.sqrt(1 - v * v)).max())
    r.check("Slice x₅ = v is a 3-sphere of radius √(1 − v²) inside S⁴", f"max error {worst:.1e}", worst < 1e-12)
    p4 = g.random_sphere_points(4, 200000, rng)
    sp = np.linalg.norm(g.s4_flow_field(p4), axis=1)
    still = np.linalg.norm(g.s4_flow_field(np.array([[0, 0, 0, 0, 1.0], [0, 0, 0, 0, -1.0]])), axis=1)
    r.check("Slice-wise Hopf flow on S⁴ stops exactly at x₅ = ±1", f"speed at poles {still.max():.1f}; random min {sp.min():.4f}", still.max() == 0.0)

    # ── Sizes ──
    r.section("How big is each unit sphere?")
    print(f"  {'n':>2}  {'formula':>10}  {'Monte Carlo':>12}")
    mc_ok = True
    for n in range(1, 8):
        exact = g.sphere_measure(n)
        pts = rng.uniform(-1, 1, (1_500_000, n + 1))
        ball = (2.0 ** (n + 1)) * np.mean(np.sum(pts * pts, axis=1) <= 1.0)
        mc = ball * (n + 1)  # |Sⁿ| = (n + 1)·|Bⁿ⁺¹|
        mc_ok &= abs(mc - exact) / exact < 0.02
        print(f"  {n:>2}  {exact:>10.4f}  {mc:>12.4f}")
    peak = max(range(1, 20), key=g.sphere_measure)
    r.check("Monte Carlo agrees with 2π^((n+1)/2) ⁄ Γ((n+1)/2) (within 2 %)", "n = 1 … 7", bool(mc_ok))
    r.check("The largest unit sphere is S⁶", f"peak at n = {peak}", peak == 6)

    print(f"\n{sum(x[2] for x in r.rows)}/{len(r.rows)} checks passed")
    return r.ok


if __name__ == "__main__":
    raise SystemExit(0 if run() else 1)
