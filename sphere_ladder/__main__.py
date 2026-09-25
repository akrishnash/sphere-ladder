"""Command line for the sphere ladder.

  python -m sphere_ladder verify
  python -m sphere_ladder plot s1|s2|torus|s3|s4|all [--save DIR] [--animate] [--light]
  python -m sphere_ladder plot torus --eta 45 --p 2 --q 3
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(prog="sphere_ladder", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("verify", help="numerically check every claim on the pages")
    pp = sub.add_parser("plot", help="draw a figure with matplotlib")
    pp.add_argument("which", choices=["s1", "s2", "torus", "s3", "s4", "all"])
    pp.add_argument("--save", metavar="DIR", help="save PNGs here instead of opening windows")
    pp.add_argument("--animate", action="store_true", help="animate the Hopf flow (s3 only)")
    pp.add_argument("--light", action="store_true", help="light background instead of dark")
    pp.add_argument("--eta", type=float, default=45.0, help="torus η in degrees (torus only)")
    pp.add_argument("--p", type=int, default=2, help="turns around the hole (torus only)")
    pp.add_argument("--q", type=int, default=3, help="turns around the tube (torus only)")
    args = ap.parse_args()

    if args.cmd == "verify":
        from .verify import run
        return 0 if run() else 1

    import matplotlib
    if args.save:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from . import plots

    plots.use_style(light=args.light)
    if args.animate:
        fig, anim = plots.animate_s3()
        if args.save:
            out = Path(args.save); out.mkdir(parents=True, exist_ok=True)
            anim.save(out / "s3_flow.gif", writer="pillow", fps=30)
            print(f"saved {out / 's3_flow.gif'}")
        else:
            plt.show()
        return 0

    names = list(plots.FIGURES) if args.which == "all" else [args.which]
    figs = {}
    for name in names:
        if name == "torus":
            figs[name] = plots.fig_torus(math.radians(args.eta), args.p, args.q)
        else:
            figs[name] = plots.FIGURES[name]()
    if args.save:
        out = Path(args.save); out.mkdir(parents=True, exist_ok=True)
        for name, fig in figs.items():
            fig.savefig(out / f"{name}.png", dpi=150, bbox_inches="tight")
            print(f"saved {out / (name + '.png')}")
    else:
        plt.show()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
