# Sphere Ladder

**Live:** https://akrishnash.github.io/sphere-ladder/

An interactive climb up the dimensions: **S¹ → S² → torus → S³ → S⁴**. At each step the same trick
makes the next sphere visible: shine a light from the north pole and look at the shadow it casts on
flat space one dimension down (stereographic projection). S⁴ is too big even for that, so it is shown
by slicing it into a stack of 3-spheres.

| Page | What it shows |
|---|---|
| **S¹** circle | Points flowing round a circle; their shadows run along a line and escape to ∞ at the pole. |
| **S²** sphere | Latitudes cast circular shadows on a plane; tilted circles stay circles, circles through N become lines. |
| **T²** torus | Tori as slices of S³, (p, q) torus curves and knots, and the flat square with glued edges. |
| **S³** hypersphere | The Hopf fibration: great circles become linked rings on nested tori, each ring one point of S². |
| **S⁴** 4-sphere | Slices x₅ = v are 3-spheres of radius √(1 − v²), shrinking to two still points. |

The web app is a single static `index.html` (no build step). Light and dark themes.

## Python companion

`sphere_ladder/` holds the same geometry in NumPy, a checker for every claim the pages make, and
matplotlib figures. Needs Python 3.10+, `numpy` and `matplotlib`.

```bash
python -m sphere_ladder verify                       # 26 numerical checks
python -m sphere_ladder plot s3                      # interactive 3D window
python -m sphere_ladder plot torus --eta 45 --p 2 --q 3
python -m sphere_ladder plot all --save out --light  # PNGs, light background
python -m sphere_ladder plot s3 --animate            # animated Hopf flow
```

What `verify` measures, among other things: every pair of Hopf fibers has linking number 1 (Gauss
integral), fiber shadows are exact circles to ~10⁻¹⁵, the tori in S³ are flat, the Hopf map sends
each fiber to a single point of S², and the S⁴ flow stops exactly at x₅ = ±1.

## License

MIT
