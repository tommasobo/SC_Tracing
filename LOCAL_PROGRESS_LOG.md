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

## 2026-06-24 Second Pass - Tests, Tier C Safety, And Merge Readiness

- Command: `git show --stat --oneline --summary HEAD`.
  Result: audited first-pass commit `61ab912`; additions were source/docs plus NPKIT JSON inputs. No generated figures, logs, nsys/sqlite files, Gurobi license, built binaries, or Python bytecode were tracked.
- Command: `git diff origin/main...HEAD -- . ':!data/npkit/*.json' ':!tools/nccl_generator/*' | rg ...`.
  Result: absolute paths found only in local progress/reconciliation docs, intentionally documenting local machine state.
- Added `pytest.ini` and `tests/test_artifact_smoke.py`.
  Result: default `python3 -m pytest -q` now tests the artifact smoke path rather than collecting stale historical `solver/test` tests.
- Added `solver/test/README.md`.
  Result: explains why historical solver tests are not the default artifact test path.
- Added `scripts/check_artifact.py`.
  Result: local-safe check script covering packaged inputs, default imports, help surfaces, Tier C dry-run, compile checks, one optional figure, and optional pipeline demo.
- Hardened Tier C scripts:
  - `pipeline/reproduce_fig5_from_nsys.sh --dry-run` prints plan/dependency status and exits without downloads or generation.
  - `pipeline/reproduce_fig5_from_nsys.sh` stops before Monolithic-LP unless `--run-lp` is passed.
  - `pipeline/run_monolithic_lp.py --dry-run` prints the solver command without launching Gurobi.
  - `pipeline/run_nccl_generator.py --dry-run` validates sqlite/NPKIT inputs and prints the generator command.
- Command: `python3 scripts/check_artifact.py --skip-figure`.
  Result: succeeded. It reported `nsys` as missing in Tier C dry-run, without failing.
- Command: `python3 -m pytest -q`.
  Result: succeeded, `5 passed`.
- Command: `git diff --check`.
  Result: clean.
- Command: `python3 reproduce_all.py --list`.
  Result: succeeded.
- Command: `/usr/bin/time -f 'elapsed=%E maxrss_kb=%M' python3 reproduce_all.py --pipeline --only 3`.
  Result: succeeded; runtime 4.40 s; max RSS 134868 KiB.
- Command: `/usr/bin/time -f 'elapsed=%E maxrss_kb=%M' python3 -m compileall -q pipeline tools/nccl_generator solver/llamp_nccl`.
  Result: succeeded; runtime 0.02 s; max RSS 11064 KiB.
- Command: `/usr/bin/time -f 'elapsed=%E maxrss_kb=%M' python3 -m pytest -q`.
  Result: succeeded; `5 passed`; runtime 2.43 s; max RSS 82728 KiB.
- Command: `/usr/bin/time -f 'elapsed=%E maxrss_kb=%M' python3 scripts/check_artifact.py`.
  Result: succeeded; included Tier C dry-run and one packaged Fig. 7 regeneration; runtime 2.10 s; max RSS 82476 KiB.

## 2026-06-25 00:15 CEST - Local Raw-Trace End-to-End Smoke

- Input: local nsys-exported SQLite directory `/home/tbonato/LLAMP_Test/data/raw/mixed20_annotated/mixed20_atlahs_rerun_results_20260403_annotated_rerun/mixed20_rand16to64_2n_ch1_job1791879/trace/nsys_reports`.
  Result: found 8 nonempty SQLite files, 1.7-4.2 MiB each.
- Command: `/usr/bin/time -f 'elapsed=%E maxrss_kb=%M' python3 pipeline/run_nccl_generator.py --sqlite-dir .../nsys_reports --out-dir tier_c_local_smoke/mixed20_2n_ch1/analysis`.
  Result: succeeded; generated `output.goal` plus NCCL metadata sidecars in 3.85 s, max RSS 209464 KiB. The GOAL has 266707 lines; `collective_instances.csv` and `goal_label_ranges.csv` have 161 lines each.
- Sidecar finding: `tools/nccl_generator` writes identity/metadata sidecars (`collective_instances.csv`, `goal_label_ranges.csv`, `comm_info.csv`, etc.) but does not write LP `comm_dep.csv`. The send/recv dependency sidecar is generated by patched LogGOPSim with `--comm-dep-file`.
- Command: `tools/LogGOPSim/txt2bin -i tier_c_local_smoke/mixed20_2n_ch1/analysis/output.goal -o tier_c_local_smoke/mixed20_2n_ch1/lgs/trace.bin`.
  Result: succeeded in 0.09 s, max RSS 6468 KiB.
- Command: `tools/LogGOPSim/LogGOPSim -f tier_c_local_smoke/mixed20_2n_ch1/lgs/trace.bin -L 1000 -G 0.04 -o 200 -g 5 --comm-dep-file tier_c_local_smoke/mixed20_2n_ch1/lgs/comm_dep.csv`.
  Result: succeeded in 0.14 s, max RSS 29984 KiB; replay runtime 179739038 ns and wrote a 28028-line `comm_dep.csv`.
- Command: `python3 pipeline/run_lgs.py --goal tier_c_local_smoke/mixed20_2n_ch1/analysis/output.goal --L 1000 --G 0.04 --o 200 --g 5`.
  Result: succeeded; reported 179739038 ns in 0.32 s.
- Command: `/usr/bin/time -f 'nsys_lp elapsed=%E maxrss_kb=%M' timeout 120s python3 pipeline/run_monolithic_lp.py --goal tier_c_local_smoke/mixed20_2n_ch1/analysis/output.goal --comm-dep tier_c_local_smoke/mixed20_2n_ch1/lgs/comm_dep.csv --out tier_c_local_smoke/mixed20_2n_ch1/lp/full_runtime.csv --l-min 0 --l-max 0 --step 1000`.
  Result: succeeded in 6.19 s, max RSS 363756 KiB. The generated graph had 117586 vertices and 177132 edges. Output `full_runtime.csv` contains one latency point: `L=0.0`, `runtime=34557887.280000106`.
- Comparison against older local generated output `/home/tbonato/LLAMP_Test/output/mixed20_2n_ch1/generated`:
  `collective_instances.csv` and `comm_info.csv` are byte-identical. `output.goal` is not byte-identical; it has the same line count but some generated `calc` durations differ slightly. LogGOPSim runtime drift at `L=1000,G=0.04,o=200,g=5` was 179.739 ms regenerated vs 179.911 ms old (~0.096%).
- Patched code locations confirmed locally:
  `SC_Tracing/tools/nccl_generator/identity_sidecar.py`,
  `SC_Tracing/tools/nccl_generator/main.py`,
  `SC_Tracing/tools/LogGOPSim/LogGOPSim.cpp`,
  plus corresponding copies in `artifact_sc26`, `tools/nccl_generator_v2_hwfix`, and the publish/temp worktrees.
