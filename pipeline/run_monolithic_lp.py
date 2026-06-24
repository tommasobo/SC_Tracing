#!/usr/bin/env python3
"""
Pipeline stage: GOAL trace -> Monolithic-LP latency sensitivity CSV.

Thin wrapper around ``solver/main.py -a sensitivity``. Builds a single
full-trace LP and sweeps the latency parameter via dual-simplex
warm-starts, producing the ``full_runtime.csv`` that serves as the
paper's Monolithic-LP baseline in Figures 3, 4, and 5. Writes
(L [ns], runtime [ns]).

NOTE: The paper's headline ``Composite LP`` methodology (per-signature
parametric solve + program-level composition via ``solver/llamp_nccl/``)
is a *separate* code path in this repository. It is cheaper to solve
but requires workspace-aware orchestration beyond the scope of a
single wrapper; its precomputed outputs ship under ``data/output/``.
Reviewers who want to re-run the Composite LP at scale should use
the workspace drivers cited in the AD.

Usage:
    python3 pipeline/run_monolithic_lp.py \\
        --goal data/traces/demo_allreduce_16r_1MiB.goal \\
        --out data/demo/full_runtime.csv \\
        --l-min 0 --l-max 1000000 --step 50000
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOLVER = ROOT / "solver"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--goal", required=True, type=Path,
                    help="Input GOAL trace (NCCL-generated, carries unique tags)")
    ap.add_argument("--comm-dep", type=Path, default=None,
                    help="Companion comm_dep CSV that disambiguates sends/recvs. "
                         "Shipped with each A2 trace; required for workloads "
                         "where NCCL emits repeated tags.")
    ap.add_argument("--out", required=True, type=Path,
                    help="Output CSV (L_ns,runtime_ms)")
    ap.add_argument("--l-min", type=int, default=0,
                    help="Minimum latency sweep point, ns (default: 0)")
    ap.add_argument("--l-max", type=int, default=1_000_000,
                    help="Maximum latency sweep point, ns (default: 1e6)")
    ap.add_argument("--step", type=int, default=50_000,
                    help="Sweep step, ns (default: 50000)")
    ap.add_argument("--l-intra", type=int, default=350,
                    help="Intra-node latency, ns (default: 350)")
    ap.add_argument("--o", type=int, default=200,
                    help="LogGP overhead parameter, ns (default: 200)")
    ap.add_argument("--G", type=float, default=0.018,
                    help="LogGP bandwidth parameter, ns/byte (default: 0.018)")
    args = ap.parse_args()

    args.goal = args.goal.resolve()
    args.out = args.out.resolve()
    if args.comm_dep is not None:
        args.comm_dep = args.comm_dep.resolve()

    if not args.goal.exists():
        print(f"error: GOAL file not found: {args.goal}", file=sys.stderr)
        return 2

    args.out.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, str(SOLVER / "main.py"),
        "-g", str(args.goal),
        "-a", "sensitivity",
        "--l-min", str(args.l_min),
        "--l-max", str(args.l_max),
        "--step", str(args.step),
        "--l-intra", str(args.l_intra),
        "-o", str(args.o),
        "-G", str(args.G),
        "--output-dir", str(args.out.parent),
    ]
    if args.comm_dep is not None:
        cmd += ["-c", str(args.comm_dep)]
    print("[composite-lp]", " ".join(cmd))
    t0 = time.perf_counter()
    r = subprocess.run(cmd, cwd=SOLVER)
    dt = time.perf_counter() - t0
    if r.returncode != 0:
        print(f"[composite-lp] FAILED after {dt:.1f}s", file=sys.stderr)
        return r.returncode

    # The sensitivity action writes a fixed runtime filename.
    for produced in (args.out.parent / "tmp_runtime.csv",
                     args.out.parent / "runtime.csv",
                     args.out.parent / "net_lat_sen.csv"):
        if produced.exists() and produced.resolve() != args.out.resolve():
            produced.replace(args.out)
            break
    print(f"[composite-lp] wrote {args.out} ({dt:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
