#!/usr/bin/env python3
"""
Pipeline stage: SQLite (from nsys export) -> GOAL + comm_dep CSV.

Thin wrapper around ``tools/nccl_generator/main.py`` that points the
generator at the shipped Alps NPKit reference data. Typical invocation:

    python3 pipeline/run_nccl_generator.py \\
        --sqlite-dir workspaces/llama_n4/sqlite \\
        --out-dir    workspaces/llama_n4/analysis

The input directory must contain one ``*.sqlite`` file per node (four
for the Fig 5 workload). The output directory will end up with
``output.goal``, ``collective_instances.csv``, ``comm_info.csv``,
``comm_ring_info.csv``, and the ``comm_dep`` file that the LP solver
needs.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
GENERATOR = ROOT / "tools" / "nccl_generator"
NPKIT_DIR = ROOT / "data" / "npkit"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sqlite-dir", required=True, type=Path,
                    help="Directory containing *.sqlite files "
                         "(one per GPU node).")
    ap.add_argument("--out-dir", required=True, type=Path,
                    help="Destination for output.goal and the metadata CSVs.")
    ap.add_argument("--npkit-simple", type=Path,
                    default=NPKIT_DIR / "npkit_alps_simple.json")
    ap.add_argument("--npkit-ll", type=Path,
                    default=NPKIT_DIR / "npkit_alps_ll.json")
    ap.add_argument("--parallel", action="store_true", default=False,
                    help="Use the Dask-backed parallel event extractor "
                         "(experimental; may not apply tolerant_gpu_match).")
    ap.add_argument("--dry-run", action="store_true",
                    help="Validate inputs and print the generator command "
                         "without running it.")
    args = ap.parse_args()

    for p in (args.sqlite_dir, args.npkit_simple, args.npkit_ll):
        if not p.exists():
            print(f"error: {p} not found", file=sys.stderr)
            return 2
    sqlite_files = sorted(args.sqlite_dir.glob("*.sqlite"))
    if not sqlite_files:
        print(f"error: no *.sqlite files found in {args.sqlite_dir}", file=sys.stderr)
        return 2
    args.out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, str(GENERATOR / "main.py"),
        "-i", str(args.sqlite_dir),
        "-o", str(args.out_dir),
        "-s", str(args.npkit_simple),
        "-l", str(args.npkit_ll),
        "--intermediate_results",
    ]
    if args.parallel:
        cmd += ["-p"]
    print(">>>", " ".join(cmd))
    if args.dry_run:
        print(f"[nccl_generator] dry run complete; found {len(sqlite_files)} sqlite file(s).")
        return 0
    t0 = time.perf_counter()
    r = subprocess.run(cmd, cwd=GENERATOR)
    dt = time.perf_counter() - t0
    if r.returncode != 0:
        print(f"[nccl_generator] FAILED after {dt:.1f}s", file=sys.stderr)
        return r.returncode
    print(f"[nccl_generator] wrote {args.out_dir} ({dt:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
