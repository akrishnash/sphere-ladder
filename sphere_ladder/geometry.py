"""Exact geometry for the sphere ladder.

Conventions
-----------
* Sⁿ is the unit sphere in ℝⁿ⁺¹. Points are NumPy arrays whose last axis holds coordinates.
* A point of S³ is written (x, y, z, w) = (Re z₁, Im z₁, Re z₂, Im z₂) with |z₁|² + |z₂|² = 1.
* Stereographic projection is always taken from the pole on the LAST axis.
  ``stereographic`` projects onto the equatorial hyperplane (x ↦ x' / (1 − xₙ)),
  ``stereographic(..., tangent=True)`` onto the tangent plane at the opposite pole (twice as large),
  which is what the S¹ and S² pages of the web app draw.

Everything is vectorised and float64 throughout.
"""

from __future__ import annotations

from math import gamma, pi

import numpy as np

TAU = 2.0 * np.pi


# ─── Spheres ──────────────────────────────────────────────────────────────

def sphere_measure(n: int) -> float:
    """Total n-dimensional measure of the unit sphere Sⁿ: 2π^((n+1)/2) / Γ((n+1)/2)."""
    return 2.0 * pi ** ((n + 1) / 2) / gamma((n + 1) / 2)


def random_sphere_points(n: int, count: int, rng: np.random.Generator) -> np.ndarray:
    """Uniform random points on Sⁿ (normalised Gaussians)."""
    g = rng.standard_normal((count, n + 1))
    return g / np.linalg.norm(g, axis=1, keepdims=True)


def circle(theta) -> np.ndarray:
    """Points on S¹ ⊂ ℝ²."""
    theta = np.asarray(theta, float)
    return np.stack([np.cos(theta), np.sin(theta)], axis=-1)


def latitude(height: float, a) -> np.ndarray:
    """Latitude circle of S² ⊂ ℝ³ at the given height on the z axis (z up)."""
    a = np.asarray(a, float)
    r = np.sqrt(1.0 - height**2)
    return np.stack([r * np.cos(a), r * np.sin(a), np.full_like(a, height)], axis=-1)


def circle_on_s2(normal, offset: float, a) -> np.ndarray:
    """The circle {x ∈ S² : n·x = offset} for a unit normal n, parametrised by angle a."""
    n = np.asarray(normal, float)
    n = n / np.linalg.norm(n)
    helper = np.array([0.0, 0.0, 1.0]) if abs(n[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = np.cross(n, helper)
    u /= np.linalg.norm(u)
    v = np.cross(n, u)
    rho = np.sqrt(1.0 - offset**2)
    a = np.asarray(a, float)[..., None]
    return offset * n + rho * (u * np.cos(a) + v * np.sin(a))


# ─── Stereographic projection ─────────────────────────────────────────────

def stereographic(p, tangent: bool = False) -> np.ndarray:
    """Project points of Sⁿ ⊂ ℝⁿ⁺¹ from the north pole (0, …, 0, 1) into ℝⁿ."""
    p = np.asarray(p, float)
    k = (2.0 if tangent else 1.0) / (1.0 - p[..., -1])
    return p[..., :-1] * k[..., None]


def inverse_stereographic(y) -> np.ndarray:
    """Inverse of ``stereographic`` (equatorial version): ℝⁿ → Sⁿ minus the north pole."""
    y = np.asarray(y, float)
    s = np.sum(y * y, axis=-1, keepdims=True)
    return np.concatenate([2.0 * y / (s + 1.0), (s - 1.0) / (s + 1.0)], axis=-1)


# ─── Tori inside S³ and the Hopf fibration ────────────────────────────────

def torus_point(eta, a, b) -> np.ndarray:
    """Point of the torus |z₁| = cos η, |z₂| = sin η in S³, with z₁ = cos η·e^{ia}, z₂ = sin η·e^{ib}."""
    eta, a, b = np.broadcast_arrays(*(np.asarray(v, float) for v in (eta, a, b)))
    c, s = np.cos(eta), np.sin(eta)
    return np.stack([c * np.cos(a), c * np.sin(a), s * np.cos(b), s * np.sin(b)], axis=-1)


def torus_knot(eta: float, p: int, q: int, t) -> np.ndarray:
    """(p, q) torus curve on the η-torus: p turns around the hole, q around the tube."""
    t = np.asarray(t, float)
    return torus_point(eta, p * t, q * t)


def hopf_fiber(eta: float, phi: float, t) -> np.ndarray:
    """Orbit of the Hopf flow (z₁, z₂) ↦ (e^{it}z₁, e^{it}z₂) through the point with angles (0, φ)."""
    t = np.asarray(t, float)
    return torus_point(eta, t, t + phi)


def hopf_flow_field(q) -> np.ndarray:
    """Velocity of the Hopf flow at q: d/dt (e^{it}z₁, e^{it}z₂) = i·(z₁, z₂)."""
    q = np.asarray(q, float)
    return np.stack([-q[..., 1], q[..., 0], -q[..., 3], q[..., 2]], axis=-1)


def hopf_map(q) -> np.ndarray:
    """Hopf map S³ → S²: (z₁, z₂) ↦ (2 Re z₁z̄₂, 2 Im z₁z̄₂, |z₁|² − |z₂|²)."""
    q = np.asarray(q, float)
    x, y, z, w = (q[..., i] for i in range(4))
    re = x * z + y * w
    im = y * z - x * w
    return np.stack([2 * re, 2 * im, x * x + y * y - z * z - w * w], axis=-1)


def fiber_over(base, t) -> np.ndarray:
    """The Hopf fiber lying over a point of S² (inverse of ``hopf_map``, as a whole circle)."""
    bx, by, bz = np.asarray(base, float)
    eta = 0.5 * np.arccos(np.clip(bz, -1.0, 1.0))
    phi = -np.arctan2(by, bx)
    return hopf_fiber(eta, phi, t)


def rotate4(p, angle: float, ratio: float = 0.63) -> np.ndarray:
    """Double rotation of ℝ⁴: by `angle` in the x–w plane and `ratio·angle` in the y–z plane."""
    p = np.asarray(p, float)
    ca, sa = np.cos(angle), np.sin(angle)
    cb, sb = np.cos(ratio * angle), np.sin(ratio * angle)
    x, y, z, w = (p[..., i] for i in range(4))
    return np.stack([x * ca - w * sa, y * cb - z * sb, y * sb + z * cb, x * sa + w * ca], axis=-1)


# ─── S⁴ ───────────────────────────────────────────────────────────────────

def s4_slice(v: float, q3) -> np.ndarray:
    """Lift unit-S³ points into the slice x₅ = v of S⁴ ⊂ ℝ⁵ (a 3-sphere of radius √(1 − v²))."""
    q3 = np.asarray(q3, float)
    r = np.sqrt(max(0.0, 1.0 - v * v))
    return np.concatenate([r * q3, np.full(q3.shape[:-1] + (1,), v)], axis=-1)


def s4_flow_field(p) -> np.ndarray:
    """Hopf flow on every slice of S⁴ at once: rotates (x₁, x₂) and (x₃, x₄), leaves x₅ alone."""
    p = np.asarray(p, float)
    return np.stack([-p[..., 1], p[..., 0], -p[..., 3], p[..., 2], np.zeros_like(p[..., 0])], axis=-1)


# ─── Curve measurements ───────────────────────────────────────────────────

def fit_circle_3d(points) -> dict:
    """Fit a circle to 3-D points: best plane by SVD, then a least-squares circle in that plane.

    Returns the centre, radius, the largest distance from the plane and the largest radial error.
    """
    P = np.asarray(points, float)
    c0 = P.mean(axis=0)
    _, sv, vt = np.linalg.svd(P - c0)
    u, v, n = vt
    planar = np.abs((P - c0) @ n).max()
    X, Y = (P - c0) @ u, (P - c0) @ v
    A = np.column_stack([X, Y, np.ones_like(X)])
    sol, *_ = np.linalg.lstsq(A, X * X + Y * Y, rcond=None)
    cx, cy = sol[0] / 2, sol[1] / 2
    R = np.sqrt(sol[2] + cx * cx + cy * cy)
    radial = np.abs(np.hypot(X - cx, Y - cy) - R).max()
    return {"centre": c0 + cx * u + cy * v, "radius": R, "planar_err": planar, "radial_err": radial}


def linking_number(A, B) -> float:
    """Gauss linking integral of two closed polygonal curves in ℝ³ (midpoint rule)."""
    A, B = np.asarray(A, float), np.asarray(B, float)
    dA, dB = np.roll(A, -1, axis=0) - A, np.roll(B, -1, axis=0) - B
    mA, mB = A + dA / 2, B + dB / 2
    r = mA[:, None, :] - mB[None, :, :]
    num = np.einsum("ijk,ijk->ij", r, np.cross(dA[:, None, :], dB[None, :, :]))
    return float(np.sum(num / np.linalg.norm(r, axis=-1) ** 3) / (4 * np.pi))
