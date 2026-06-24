# Local Progress Log

This log records the lightweight local cleanup/reproduction pass for the SC
tracing/provisioning artifact. It is intentionally focused on actions that are
safe on this local WSL machine and avoids expensive trace regeneration,
4096-GPU jobs, monolithic LP solves, and large downloads.

## 2026-06-24 22:04 CEST - Initial Checkout And Branch

- Machine/environment: `Linux LAPTOP-CJL91217 6.18.33.1-microsoft-standard-WSL2`, Python `3.8.10`.
- Artifact repository: `/home/tbonato/LLAMP_Test/SC_Tracing`.
- Command: `git ls-remote --heads https://github.com/tommasobo/SC_Tracing.git`.
- Result: remote advertised only `refs/heads/main` at `90231b14a03b526b406fb4811229b5544cc2a5c4`; no remote `clean_version` branch was visible locally.
- Command: `git clone https://github.com/tommasobo/SC_Tracing.git SC_Tracing`.
- Command: `git fetch --all --prune`.
- Command: `git switch -c clean_version_local origin/main`.
- Current branch: `clean_version_local`, tracking `origin/main`.
- Base commit: `90231b14a03b526b406fb4811229b5544cc2a5c4` (`Initial SC26 artifact: figure reproduction + full LP/LGS pipeline`).
- Status after branch creation: clean.
- Local-only context observed outside this checkout:
  - `/home/tbonato/LLAMP_Test` is a dirty `Traces_Compression` development checkout on branch `codex-analytical-formula-comparison`.
  - `/home/tbonato/LLAMP_Test/artifact_sc26` is an untracked local artifact-style directory in the development checkout, about 24 MiB.
  - `/home/tbonato/LLAMP_Test/workspaces/publish_traces_compression_20260331` is a separate dirty local checkout, about 3.8 GiB.
  - `/home/tbonato/LLAMP_Test/tmp_publish_traces_main_wt` is another local worktree/check-out with modified generator files, about 183 MiB.
- Initial artifact checkout size: about 9.1 MiB.
- Initial packaged data files in this checkout:
  - `data/output/grok_final/grok_N1024_bw_sweep.csv`
  - `data/output/grok_final/grok_N1024_latency_sweep.csv`
  - `data/output/grok_final/grok_N1024_summary.csv`
  - `data/output/grok_final/grok_N512_bw_sweep.csv`
  - `data/output/grok_final/grok_N512_latency_sweep.csv`
  - `data/output/grok_final/grok_N512_summary.csv`
  - `data/output/vllm_llama8b_128tok/bandwidth_runtime.csv`
  - `data/output/vllm_llama8b_128tok/latency_runtime.csv`
  - `data/traces/demo_allreduce_16r_1MiB.goal`
- Interpretation: `origin/main` is the safest base for `clean_version_local` because the artifact remote currently exposes only `main`. The richer local `artifact_sc26` material may contain important newer scripts/data, but it is not authoritative and needs comparison before porting.

## 2026-06-24 22:05-22:10 CEST - Inventory, Fetch, And Lightweight Reproduction

- Command: `git fetch --all --prune` in `/home/tbonato/LLAMP_Test`.
  Result: development `origin/main` advanced from `279f441e` to `22bafa59`.
- Command: `git -C workspaces/publish_traces_compression_20260331 fetch --all --prune`.
  Result: fetched successfully; local branch has modified generated plot PDFs and `scientific_policies.py`.
- Command: `git -C tmp_publish_traces_main_wt fetch --all --prune`.
  Result: failed with a remote-ref lock error for `origin/feature/closed-goal-prefix-cutoff`; freshness of that temp worktree remains unclear.
- Command: `diff -qr SC_Tracing artifact_sc26`.
  Result: local `artifact_sc26` contains extra source/wrapper material (`tools/nccl_generator`, Tier C pipeline wrappers, NPKIT JSONs) plus generated outputs/binaries. Only source-like/lightweight pieces were considered for porting.
- Command: `python3 -c "import matplotlib, numpy, pandas; ..."` in artifact checkout.
  Result: `matplotlib 3.7.5`, `numpy 1.22.2`, `pandas 2.0.3`.
- Command: `python3 reproduce_all.py --list`.
  Result: succeeded; listed paper figure mapping.
- Command: `/usr/bin/time -f 'elapsed=%E maxrss_kb=%M' python3 reproduce_all.py`.
  Result: succeeded; all packaged figure PDFs reported `OK`; runtime 38.9 s; max RSS 191296 KiB. Output directory: `figures/` (ignored by git).
- Command: `/usr/bin/time -f 'elapsed=%E maxrss_kb=%M' python3 reproduce_all.py --pipeline --only 3`.
  Result: succeeded; built LogGOPSim and replayed the shipped demo GOAL at `L=0,1000,10000,100000`; runtime 20.9 s; max RSS 374548 KiB. Built binaries are ignored by git.
- Command: `python3 -m pytest solver/test`.
  Result: failed during collection because tests expect `solver/` on `PYTHONPATH`.
- Command: `PYTHONPATH=solver python3 -m pytest solver/test`.
  Result: collected 7 tests; 1 passed, 6 failed. Failures appear to reflect stale unit tests and missing historical test-data paths, not the packaged figure path.

## 2026-06-24 22:10 CEST - Local Artifact Improvements

- Ported source-like Tier C pieces from `/home/tbonato/LLAMP_Test/artifact_sc26`:
  - `tools/nccl_generator/`
  - `pipeline/run_monolithic_lp.py`
  - `pipeline/run_nccl_generator.py`
  - `pipeline/reproduce_fig5_from_nsys.sh`
  - `data/npkit/npkit_alps_simple.json`
  - `data/npkit/npkit_alps_ll.json`
- Did not port generated figures, built binaries, cached demo outputs, regenerated Llama cache outputs, or large workspaces.
- Added `requirements-tierc.txt` for optional raw-nsys-to-GOAL dependencies, keeping `requirements.txt` lightweight for Tier A.
- Updated `README.md` with explicit Tier A/B/C reproduction guidance and local hardware boundaries.
- Updated `.gitignore` for `tier_c_fig5/` and `*.regenerated`.
- Updated `pipeline/demo.py` so the default LGS-only demo no longer says it produced persistent outputs.
- Added `LOCAL_RECONCILIATION_REPORT.md` as a concise merge aid for later `clean_version` reconciliation.

## 2026-06-24 22:12 CEST - Post-Edit Verification

- Command: `python3 pipeline/run_monolithic_lp.py --help`.
  Result: succeeded; wrapper arguments parsed.
- Command: `python3 pipeline/run_nccl_generator.py --help`.
  Result: succeeded; wrapper arguments parsed.
- Command: `bash -n pipeline/reproduce_fig5_from_nsys.sh`.
  Result: succeeded; shell syntax OK.
- Command: `python3 -m compileall -q pipeline tools/nccl_generator solver/llamp_nccl`.
  Result: succeeded.
- Command: `git diff --check`.
  Result: clean.
- Command: `/usr/bin/time -f 'elapsed=%E maxrss_kb=%M' python3 reproduce_all.py --pipeline --only 3` after output-flush and demo-message changes.
  Result: succeeded; runtime 3.98 s after LogGOPSim was already built; max RSS 134764 KiB. Console output is now ordered correctly.
