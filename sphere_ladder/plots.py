"""Matplotlib figures for the sphere ladder, drawn from the exact geometry in ``geometry``.

Run:  python -m sphere_ladder plot s3            (interactive window; drag to rotate)
      python -m sphere_ladder plot all --save out
      python -m sphere_ladder plot s3 --animate
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import hsv_to_rgb

from . import geometry as g

THEMES = {
    "dark": {"BG": "#0c0e16", "INK": "#e7e9f2", "MUTED": "#8b91a8", "GRID": "#2a2e3d",
             "PAL": ["#6fb7ff", "#c89bff", "#ffb86b"]},
    "light": {"BG": "#ffffff", "INK": "#151826", "MUTED": "#5d6479", "GRID": "#d5d8e2",
              "PAL": ["#1868cc", "#8042c4", "#c8680c"]},
}
BG, INK, MUTED, GRID = "#0c0e16", "#e7e9f2", "#8b91a8", "#2a2e3d"
PAL = ["#6fb7ff", "#c89bff", "#ffb86b"]
LIGHT = False
LATS = (0.35, -0.10, -0.55)


def use_style(light: bool = False) -> None:
    global BG, INK, MUTED, GRID, PAL, LIGHT
    t = THEMES["light" if light else "dark"]
    BG, INK, MUTED, GRID, PAL, LIGHT = t["BG"], t["INK"], t["MUTED"], t["GRID"], t["PAL"], light
    plt.rcParams.update({
        "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
        "text.color": INK, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.edgecolor": GRID, "font.family": "monospace", "font.size": 9,
    })


def hopf_color(eta: float, phi: float):
    """Same idea as the web app: hue = longitude on S², brightness = latitude."""
    if LIGHT:
        return hsv_to_rgb([(phi % g.TAU) / g.TAU, 0.85, 0.82 - 0.35 * eta / (np.pi / 2)])
    return hsv_to_rgb([(phi % g.TAU) / g.TAU, 0.62, 1.0 - 0.45 * eta / (np.pi / 2)])


def eta_spread(n: int) -> np.ndarray:
    return np.array([0.22 * np.pi]) if n == 1 else np.pi * (0.10 + 0.22 * np.arange(n) / (n - 1))


def axes3d(fig, pos, lim: float, title: str | None = None):
    ax = fig.add_subplot(pos, projection="3d")
    ax.set_facecolor(BG)
    ax.set_axis_off()
    ax.set_box_aspect((1, 1, 1))
    for setter in (ax.set_xlim, ax.set_ylim, ax.set_zlim):
        setter(-lim, lim)
    if title:
        ax.set_title(title, color=INK, pad=0)
    return ax


# ─── Individual scenes ────────────────────────────────────────────────────

def draw_s1(ax, n: int = 7, phase: float = 0.3) -> None:
    t = np.linspace(0, g.TAU, 400)
    ax.plot(*g.circle(t).T, color=INK, lw=0.8, alpha=0.5)
    ax.axhline(-1, color=MUTED, lw=0.8)
    N = np.array([0.0, 1.0])
    for k in range(n):
        th = phase + k * g.TAU / n
        p = g.circle(th)
        if 1 - p[1] < 1e-3:
            continue
        xs = g.stereographic(p, tangent=True)[0]
        c = PAL[k % 3]
        ax.plot([N[0], xs], [N[1], -1], color=c, lw=0.7, alpha=0.45)
        ax.plot(*p, "o", color=c, ms=5)
        ax.plot(xs, -1, "o", color=c, ms=5)
    ax.plot(*N, "o", color=INK, ms=4)
    ax.annotate("N", N, xytext=(6, 6), textcoords="offset points", color=INK)
    ax.set_xlim(-6, 6); ax.set_ylim(-1.8, 1.6); ax.set_aspect("equal")
    ax.set_title("S¹ → ℝ¹  ·  x′ = 2x / (1 − y)", color=INK)
    ax.tick_params(left=False, labelleft=False)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)


def draw_s2(ax, per: int = 6, phase: float = 0.0) -> None:
    u, v = np.meshgrid(np.linspace(0, g.TAU, 25), np.linspace(0, np.pi, 13))
    ax.plot_wireframe(np.sin(v) * np.cos(u), np.sin(v) * np.sin(u), np.cos(v), color=INK, lw=0.3, alpha=0.2)
    ext = 3.2
    for x in np.arange(-ext, ext + 1e-9, 0.8):
        ax.plot([x, x], [-ext, ext], [-1, -1], color=MUTED, lw=0.3, alpha=0.4)
        ax.plot([-ext, ext], [x, x], [-1, -1], color=MUTED, lw=0.3, alpha=0.4)
    t = np.linspace(0, g.TAU, 300)
    N = np.array([0, 0, 1.0])
    for li, h in enumerate(LATS):
        c = PAL[li]
        lat = g.latitude(h, t)
        sh = g.stereographic(lat, tangent=True)
        ax.plot(*lat.T, color=c, lw=1.2)
        ax.plot(sh[:, 0], sh[:, 1], -1, color=c, lw=1, alpha=0.7)
        for k in range(per):
            p = g.latitude(h, phase + k * g.TAU / per + li * 0.5)
            s = g.stereographic(p, tangent=True)
            ax.scatter(*p, color=c, s=14, depthshade=False)
            ax.scatter(s[0], s[1], -1, color=c, s=14, depthshade=False)
            if k == 0:
                ax.plot(*np.array([N, [s[0], s[1], -1]]).T, color=c, lw=0.7, alpha=0.6)
    ax.scatter(*N, color=INK, s=12)
    ax.text(*N + [0.1, 0.1, 0.15], "N", color=INK)
    ax.set_zlim(-1.4, 2.4)
    ax.view_init(elev=24, azim=-60)


def draw_torus(ax, eta: float = np.pi / 4, p: int = 2, q: int = 3) -> None:
    a, b = np.meshgrid(np.linspace(0, g.TAU, 60), np.linspace(0, g.TAU, 40))
    S = g.stereographic(g.torus_point(eta, a, b))
    ax.plot_surface(S[..., 0], S[..., 1], S[..., 2], color=PAL[0], alpha=0.12, linewidth=0.2, edgecolor=(0, 0, 0, 0.1) if LIGHT else (1, 1, 1, 0.12))
    t = np.linspace(0, g.TAU, 1500)
    K = g.stereographic(g.torus_knot(eta, p, q, t))
    ax.plot(*K.T, color=PAL[2], lw=1.8)
    ext = max(np.cos(eta) / (1 - np.sin(eta)), np.tan(eta)) * 1.05
    for setter in (ax.set_xlim, ax.set_ylim, ax.set_zlim):
        setter(-ext, ext)
    ax.view_init(elev=35, azim=-50)


def draw_s3(ax, tori: int = 3, per: int = 10, scale: float = 1.0, lw: float = 1.0):
    t = np.linspace(0, g.TAU, 400)
    fibers = []
    for ti, eta in enumerate(eta_spread(tori)):
        for k in range(per):
            phi = k * g.TAU / per + ti * 0.37
            F = g.stereographic(g.hopf_fiber(eta, phi, t)) * scale
            ax.plot(*F.T, color=hopf_color(eta, phi), lw=lw, alpha=0.9)
            fibers.append((eta, phi))
    ax.view_init(elev=30, azim=-55)
    return fibers


def draw_base(ax, fibers) -> None:
    u, v = np.meshgrid(np.linspace(0, g.TAU, 25), np.linspace(0, np.pi, 13))
    ax.plot_wireframe(np.sin(v) * np.cos(u), np.sin(v) * np.sin(u), np.cos(v), color=INK, lw=0.3, alpha=0.2)
    for eta, phi in fibers:
        b = g.hopf_map(g.hopf_fiber(eta, phi, 0.0))
        ax.scatter(*b, color=hopf_color(eta, phi), s=30, depthshade=False)
    ax.view_init(elev=25, azim=-55)


# ─── Figures ──────────────────────────────────────────────────────────────

def fig_s1():
    fig, ax = plt.subplots(figsize=(9, 4.5))
    draw_s1(ax)
    return fig


def fig_s2():
    fig = plt.figure(figsize=(7, 7))
    ax = axes3d(fig, 111, 2.6, "S² → ℝ²  ·  latitudes cast circles")
    draw_s2(ax)
    return fig


def fig_torus(eta: float = np.pi / 4, p: int = 2, q: int = 3):
    fig = plt.figure(figsize=(12, 6))
    ax = axes3d(fig, 121, 1, f"η = {np.degrees(eta):.0f}° torus with the ({p}, {q}) curve")
    draw_torus(ax, eta, p, q)
    sq = fig.add_subplot(122)
    t = np.linspace(0, g.TAU, 4000)
    A, B = (p * t) % g.TAU, (q * t) % g.TAU
    jumps = np.where((np.abs(np.diff(A)) > np.pi) | (np.abs(np.diff(B)) > np.pi))[0] + 1
    for a_seg, b_seg in zip(np.split(A, jumps), np.split(B, jumps)):
        sq.plot(a_seg, b_seg, color=PAL[2], lw=1.6)
    sq.set_xlim(0, g.TAU); sq.set_ylim(0, g.TAU); sq.set_aspect("equal")
    sq.set_xlabel("a · around the hole"); sq.set_ylabel("b · around the tube")
    sq.set_title("The same curve on the flat square (opposite edges glued)", color=INK)
    return fig


def fig_s3(tori: int = 3, per: int = 10):
    fig = plt.figure(figsize=(13, 6.5))
    ax = axes3d(fig, 121, 2.2, "S³ → ℝ³  ·  Hopf fibers are linked circles")
    fibers = draw_s3(ax, tori, per)
    base = axes3d(fig, 122, 1.05, "S²  ·  each whole fiber is one dot")
    draw_base(base, fibers)
    return fig


def fig_s4(per: int = 8):
    vs = (-0.97, -0.7, 0.0, 0.7, 0.97)
    fig = plt.figure(figsize=(16, 4.2))
    fig.suptitle("S⁴ sliced at x₅ = v: each slice is a 3-sphere of radius √(1 − v²), drawn by its Hopf rings", color=INK)
    for i, v in enumerate(vs):
        r = np.sqrt(1 - v * v)
        ax = axes3d(fig, 151 + i, 2.2, f"v = {v:+.2f}   r = {r:.2f}")
        draw_s3(ax, 3, per, scale=r, lw=0.8)
    return fig


def animate_s3(tori: int = 3, per: int = 10, frames: int = 360):
    fig = plt.figure(figsize=(8, 8))
    ax = axes3d(fig, 111, 2.2, "Hopf flow on S³ (shadow in ℝ³)")
    fibers = draw_s3(ax, tori, per, lw=0.6)
    colors = [hopf_color(e, p) for e, p in fibers]
    phases = np.arange(len(fibers)) * 2.399963

    def heads(t):
        P = np.array([g.stereographic(g.hopf_fiber(e, p, t + ph)) for (e, p), ph in zip(fibers, phases)])
        return P[:, 0], P[:, 1], P[:, 2]

    sc = ax.scatter(*heads(0.0), color=colors, s=26, depthshade=False)

    def update(i):
        sc._offsets3d = heads(i * g.TAU / frames * 2)
        ax.view_init(elev=30, azim=-55 + i * 0.5)
        return (sc,)

    anim = FuncAnimation(fig, update, frames=frames, interval=33, blit=False)
    return fig, anim


FIGURES = {"s1": fig_s1, "s2": fig_s2, "torus": fig_torus, "s3": fig_s3, "s4": fig_s4}
