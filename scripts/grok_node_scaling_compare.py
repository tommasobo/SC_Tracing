#!/usr/bin/env python3
"""Build a local Grok node-scaling comparison table and plot.

This script is intentionally provenance-aware: it uses already-generated
local outputs when they exist, marks missing series as unavailable, and does
not launch LGS or LP jobs.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Dict, Iterable, Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ART_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCAL_ROOT = ART_ROOT.parent


CONFIGS = [
    ("N4", 4, 16),
    ("N8", 8, 32),
    ("N16", 16, 64),
    ("N32", 32, 128),
    ("N64", 64, 256),
    ("N128", 128, 512),
]

TRAIN_STEP_RE = re.compile(
    r"iteration\s+(\d+)/\d+.*?train_step_timing in s:\s+([0-9.e+-]+)"
)

N16_LOCAL_BLOCKER = (
    "blocked locally: no full N16 GOAL/comm_dep files are present; a guarded "
    "one-rank Nsight export produced a 273 MB SQLite file, implying roughly "
    "17 GB for 64 ranks before GOAL generation, while this local filesystem "
    "had about 6.3 GB free. The paper memory-scaling data also estimates full "
    "N16 Monolithic LP at about 22 GB peak RSS."
)


def read_runtime_ms(path: Path) -> Optional[float]:
    if not path.exists():
        return None
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        row = next(reader, None)
    if not row:
        return None
    if "runtime_ms" in row:
        return float(row["runtime_ms"])
    if "runtime_ns" in row:
        return float(row["runtime_ns"]) / 1e6
    if "runtime" in row:
        return float(row["runtime"]) / 1e6
    return None


def parse_hw_ms(log_path: Path) -> Optional[float]:
    if not log_path.exists():
        return None
    timings = []
    with log_path.open(errors="ignore") as f:
        for line in f:
            match = TRAIN_STEP_RE.search(line)
            if not match:
                continue
            iteration = int(match.group(1))
            seconds = float(match.group(2))
            if 2 <= iteration <= 48:
                timings.append(seconds)
    if not timings:
        return None
    return sum(timings) * 1000.0 / len(timings)


def find_single(patterns: Iterable[Path]) -> Optional[Path]:
    for path in patterns:
        if path.exists():
            return path
    return None


def build_rows(local_root: Path) -> pd.DataFrame:
    rows = []
    for config, nodes, gpus in CONFIGS:
        row: Dict[str, object] = {
            "config": config,
            "nodes": nodes,
            "gpus": gpus,
        }

        log_path = find_single((local_root / "workspaces" / "grok" / config).glob("log-*.out"))
        row["hw_ms"] = parse_hw_ms(log_path) if log_path is not None else None
        row["hw_source"] = str(log_path) if row["hw_ms"] is not None else ""
        row["hw_status"] = "available" if row["hw_ms"] is not None else "missing local log"

        lgs_path = {
            "N4": local_root / "output/grok_n4_full/lgs/sweeps/lgs_runtime.csv",
            "N8": local_root / "output/grok_n8_full/lgs/sweeps/lgs_runtime.csv",
        }.get(config)
        row["lgs_ms"] = read_runtime_ms(lgs_path) if lgs_path is not None else None
        row["lgs_source"] = str(lgs_path) if row["lgs_ms"] is not None else ""
        if row["lgs_ms"] is not None:
            row["lgs_status"] = "available"
        elif config == "N16":
            row["lgs_status"] = N16_LOCAL_BLOCKER
        else:
            row["lgs_status"] = "not available locally"

        mono_path = {
            "N4": local_root / "output/grok_n4/monolithic_100pct/sweeps/full_runtime.csv",
            "N8": local_root / "output/grok_n8_full/monolithic/sweeps/full_runtime.csv",
        }.get(config)
        row["monolithic_lp_ms"] = read_runtime_ms(mono_path) if mono_path is not None else None
        row["monolithic_lp_source"] = (
            str(mono_path) if row["monolithic_lp_ms"] is not None else ""
        )
        if row["monolithic_lp_ms"] is not None:
            row["monolithic_lp_status"] = "available"
        elif config == "N16":
            row["monolithic_lp_status"] = N16_LOCAL_BLOCKER
        else:
            row["monolithic_lp_status"] = "not available locally"

        comp_path = local_root / "output" / "grok_composition" / config / "composed_runtime.csv"
        row["composite_lp_ms"] = read_runtime_ms(comp_path)
        row["composite_lp_source"] = str(comp_path) if row["composite_lp_ms"] is not None else ""
        row["composite_lp_status"] = (
            "available" if row["composite_lp_ms"] is not None else "missing local output"
        )

        rows.append(row)

    return pd.DataFrame(rows)


def plot(df: pd.DataFrame, out_pdf: Path, out_png: Path) -> None:
    plt.rcParams.update(
        {
            "font.size": 8,
            "axes.labelsize": 8,
            "axes.titlesize": 9,
            "legend.fontsize": 7,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "lines.linewidth": 1.6,
            "lines.markersize": 4,
            "axes.linewidth": 0.7,
            "grid.linewidth": 0.35,
            "grid.alpha": 0.35,
            "figure.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.03,
        }
    )
    fig, ax = plt.subplots(figsize=(4.8, 2.35))

    series = [
        ("hw_ms", "Hardware logs", "#1b1b1b", "o"),
        ("lgs_ms", "LogGOPSim", "#4E79A7", "s"),
        ("monolithic_lp_ms", "Monolithic LP", "#E15759", "^"),
        ("composite_lp_ms", "Composite LP", "#59A14F", "D"),
    ]
    for col, label, color, marker in series:
        have = df[df[col].notna()]
        if have.empty:
            continue
        ax.plot(
            have["nodes"],
            have[col] / 1000.0,
            marker=marker,
            color=color,
            label=label,
        )

    ax.set_xscale("log", base=2)
    ax.set_xticks(df["nodes"])
    ax.set_xticklabels([str(int(x)) for x in df["nodes"]])
    ax.set_xlabel("Nodes")
    ax.set_ylabel("Iteration Runtime [s]")
    ax.set_title("Grok 314B Node Scaling")
    ax.grid(True, which="both", axis="y", linestyle=":")
    ax.grid(True, which="major", axis="x", linestyle=":", alpha=0.15)
    ax.legend(loc="best", framealpha=0.92)

    missing = df[df["monolithic_lp_ms"].isna() & (df["nodes"] >= 16)]
    if not missing.empty:
        ax.annotate(
            "Monolithic LP not run beyond N8 locally\n"
            "(N16 blocked by missing GOAL/comm_dep, disk, and RAM)",
            xy=(16, max(df["composite_lp_ms"].dropna()) / 1000.0),
            xytext=(0.40, 0.14),
            textcoords="axes fraction",
            fontsize=6.4,
            color="#555555",
            arrowprops=dict(arrowstyle="->", lw=0.7, color="#777777"),
        )

    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf)
    fig.savefig(out_png, dpi=300)
    plt.close(fig)


def write_notes(df: pd.DataFrame, out_md: Path) -> None:
    lines = [
        "# Grok Node-Scaling Comparison",
        "",
        "This local comparison uses existing outputs only; it does not launch new LGS or LP jobs.",
        "",
        "Runtime columns are baseline `L=0` values where applicable. Hardware values are",
        "steady-state training-log averages over iterations 2..48, excluding warmup and the",
        "final profiled step.",
        "",
        "Important limitations:",
        "- Real LGS outputs were found for N4 and N8 only.",
        "- Real Monolithic-LP outputs were found for N4 and N8 only.",
        "- N16 has hardware logs and Composite-LP output, but no local GOAL/comm_dep files.",
        "- A guarded one-rank N16 Nsight export produced a 273 MB SQLite file; extrapolating",
        "  over 64 ranks gives roughly 17 GB before GOAL generation, while this local",
        "  filesystem had about 6.3 GB free during the run.",
        "- The paper memory-scaling estimate puts N16 Monolithic LP around 22 GB peak memory,",
        "  above this local machine's comfortable RAM budget.",
        "",
        "| Config | Nodes | GPUs | HW [s] | LGS [s] | Monolithic LP [s] | Composite LP [s] |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in df.iterrows():
        def fmt(col: str) -> str:
            value = row[col]
            if pd.isna(value):
                return ""
            return f"{float(value) / 1000.0:.3f}"

        lines.append(
            f"| {row['config']} | {int(row['nodes'])} | {int(row['gpus'])} | "
            f"{fmt('hw_ms')} | {fmt('lgs_ms')} | {fmt('monolithic_lp_ms')} | "
            f"{fmt('composite_lp_ms')} |"
        )
    lines.append("")
    out_md.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-root", type=Path, default=DEFAULT_LOCAL_ROOT)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ART_ROOT / "figures" / "grok_node_scaling",
    )
    args = parser.parse_args()

    df = build_rows(args.local_root.resolve())
    args.out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.out_dir / "grok_node_scaling_compare.csv"
    pdf_path = args.out_dir / "grok_node_scaling_compare.pdf"
    png_path = args.out_dir / "grok_node_scaling_compare.png"
    notes_path = args.out_dir / "grok_node_scaling_compare.md"

    df.to_csv(csv_path, index=False)
    plot(df, pdf_path, png_path)
    write_notes(df, notes_path)

    print(f"Wrote {csv_path}")
    print(f"Wrote {pdf_path}")
    print(f"Wrote {png_path}")
    print(f"Wrote {notes_path}")
    print(df[["config", "nodes", "hw_ms", "lgs_ms", "monolithic_lp_ms", "composite_lp_ms"]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
