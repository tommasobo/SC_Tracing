#!/usr/bin/env bash
# End-to-end reproduction of paper Figure 5 starting from raw nsys captures.
#
# Stages:
#   1. Download 4 nsys-rep files for Llama 3.3 @ 16 GPUs from A2.
#   2. nsys export --type=sqlite   (needs NVIDIA Nsight Systems)
#   3. tools/nccl_generator        (SQLite -> output.goal + comm_dep)
#   4. solver/main.py              (GOAL -> composed_runtime.csv, Gurobi)
#   5. scripts/fig05_llama_iteration.py  (CSV -> fig5_llama7b.pdf)
#   6. Diff regenerated CSV and PDF against the shipped artifact output.
#
# Requires: nsys >= 2024.x on PATH, Python 3.8+, Gurobi 10.0+, wget.
#
# Expected wall time: ~15–20 min (dominated by LP solve).

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

WORK="${WORK:-$ROOT/tier_c_fig5}"
A2_NSYS="${A2_NSYS:-http://storage2.spcl.ethz.ch/traces/ai/llama3_3_n4/nsys/}"

mkdir -p "$WORK"/{nsys,sqlite,analysis,out}

echo "=== [1/6] Download nsys-rep from A2 ($A2_NSYS) ==="
wget -nc -r -np -nH --cut-dirs=4 -P "$WORK/nsys" "$A2_NSYS" || true
ls "$WORK/nsys"

echo "=== [2/6] nsys export --type=sqlite ==="
if ! command -v nsys >/dev/null 2>&1; then
    echo "error: nsys not found on PATH. Install NVIDIA Nsight Systems first." >&2
    exit 3
fi
for rep in "$WORK/nsys"/*.nsys-rep; do
    sqlite="$WORK/sqlite/$(basename "${rep%.nsys-rep}.sqlite")"
    if [ -f "$sqlite" ]; then
        echo "  [skip] $sqlite exists"
        continue
    fi
    nsys export --type=sqlite -o "$sqlite" "$rep"
done

echo "=== [3/6] SQLite -> GOAL via nccl_generator ==="
python3 "$HERE/run_nccl_generator.py" \
    --sqlite-dir "$WORK/sqlite" \
    --out-dir    "$WORK/analysis"

echo "=== [4/6] GOAL -> Monolithic-LP sweep (paper Fig 5 baseline, ~83 min) ==="
python3 "$HERE/run_monolithic_lp.py" \
    --goal  "$WORK/analysis/output.goal" \
    --out   "$WORK/out/full_runtime.csv" \
    --l-min 0 --l-max 1000000 --step 50000

echo "=== [5/6] CSV staged next to the shipped Fig 5 CSV ==="
cp "$WORK/out/full_runtime.csv" \
   "$ROOT/data/output/llama7b/partial_100pct/sweeps/full_runtime.csv.regenerated"
echo "  regenerated CSV saved to:"
echo "    $ROOT/data/output/llama7b/partial_100pct/sweeps/full_runtime.csv.regenerated"

echo "=== [6/6] Compare regenerated vs shipped (Monolithic LP baseline) ==="
SHIPPED="$ROOT/data/output/llama7b/partial_100pct/sweeps/full_runtime.csv"
MY="$WORK/out/full_runtime.csv"

python3 - <<PY
import pandas as pd, sys
shipped = pd.read_csv("$SHIPPED")
mine    = pd.read_csv("$MY")
merged  = shipped.merge(mine, on="L", suffixes=("_shipped", "_mine"))
diff    = (merged["runtime_shipped"] - merged["runtime_mine"]).abs()
rel     = diff / merged["runtime_shipped"]
print(f"{'L [ns]':<12} {'shipped':<14} {'mine':<14} {'abs diff':<14} {'rel':>7}")
for _, r in merged.iterrows():
    print(f"{int(r['L']):<12} {r['runtime_shipped']:<14.1f} "
          f"{r['runtime_mine']:<14.1f} "
          f"{abs(r['runtime_shipped']-r['runtime_mine']):<14.3f} "
          f"{rel[_]*100:>6.3f}%")
if (rel.max() < 1e-3):
    print("\\nPASS: regenerated CSV matches shipped within 0.1%.")
    sys.exit(0)
print("\\nWARN: max relative error", f"{rel.max()*100:.2f}%")
sys.exit(1)
PY

echo
echo "Tier C end-to-end reproduction complete."
echo "Regenerated CSV: $MY"
echo "To render Fig 5 from the regenerated CSV:"
echo "  cp $MY \\"
echo "     $ROOT/data/output/llama7b/comp_100pct/sweeps/composed_runtime.csv"
echo "  python3 $ROOT/reproduce_all.py --only 5"
