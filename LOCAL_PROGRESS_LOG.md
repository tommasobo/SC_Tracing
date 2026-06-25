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

## 2026-06-25 01:05-01:25 CEST - Grok Node-Scaling Local Comparison

- Objective: compare available Grok hardware-log, LogGOPSim, Monolithic-LP, and Composite-LP iteration runtimes with Monolithic-LP attempted only up to what is safe locally and the other series plotted up to N128 where data exists.
- Machine/environment: `Linux LAPTOP-CJL91217`, artifact repository `/home/tbonato/LLAMP_Test/SC_Tracing`, branch `clean_version_local`, starting commit `652bbf0`.
- Command: `df -h /home/tbonato/LLAMP_Test && free -h`.
  Result: local filesystem had about 6.3 GB free; memory was 19 GiB total, about 16 GiB available, plus 5.0 GiB swap.
- Existing local Grok inputs found:
  - Hardware logs for N4, N8, and N16 under `/home/tbonato/LLAMP_Test/workspaces/grok/N*/log-*.out`.
  - Existing LGS result CSVs for N4 and N8 under `/home/tbonato/LLAMP_Test/output/grok_n4_full/lgs/` and `/home/tbonato/LLAMP_Test/output/grok_n8_full/lgs/`.
  - Existing Monolithic-LP result CSVs for N4 and N8 under `/home/tbonato/LLAMP_Test/output/grok_n4/monolithic_100pct/` and `/home/tbonato/LLAMP_Test/output/grok_n8_full/monolithic/`.
  - Existing Composite-LP result CSVs for N4, N8, N16, N32, N64, and N128 under `/home/tbonato/LLAMP_Test/output/grok_composition/N*/`.
- Existing local Grok raw-trace state:
  - N16 has 64 `.nsys-rep` files under `/home/tbonato/LLAMP_Test/workspaces/grok/N16/nsys_profile`, total size about 309 MB.
  - N16 has NCCL metadata sidecars under `/home/tbonato/LLAMP_Test/workspaces/grok/N16/analysis`, total size about 23 MB.
  - No full N16 `output.goal` or `comm_dep.csv` was found locally.
- Guarded N16 feasibility check:
  - Command exported one rank with bundled Nsight Systems from `/home/tbonato/LLAMP_Test/workspaces/grok/N16/nsys_profile/profile_21163_0_0.nsys-rep` to a temporary SQLite file.
  - Result: succeeded in about 7.45 s, max RSS about 44 MB; the single-rank SQLite file was 272,961,536 bytes.
  - Interpretation: expanding all 64 ranks would be roughly 17 GB of SQLite before GOAL generation, exceeding the local filesystem's 6.3 GB free space.
  - Cleanup: the temporary one-rank export directory was deleted after the size check.
- Monolithic-LP feasibility:
  - Existing paper memory-scaling data estimates Grok N16 Monolithic-LP peak memory at about 22 GB.
  - Local machine had about 16 GiB available RAM plus 5 GiB swap, so a full N16 Monolithic-LP run was not launched.
- Added `scripts/grok_node_scaling_compare.py`.
  - The script parses existing local result CSVs and hardware logs, writes provenance/status fields for missing points, and does not launch LGS or LP jobs.
- Command: `python3 scripts/grok_node_scaling_compare.py`.
  Result: succeeded and wrote ignored local outputs under `figures/grok_node_scaling/`:
  - `grok_node_scaling_compare.csv`
  - `grok_node_scaling_compare.md`
  - `grok_node_scaling_compare.pdf`
  - `grok_node_scaling_compare.png`
- Generated comparison table:

  | Config | Nodes | GPUs | HW [s] | LGS [s] | Monolithic LP [s] | Composite LP [s] |
  |---|---:|---:|---:|---:|---:|---:|
  | N4 | 4 | 16 | 5.015 | 6.125 | 6.061 | 6.101 |
  | N8 | 8 | 32 | 4.116 | 5.086 | 4.988 | 4.125 |
  | N16 | 16 | 64 | 8.352 |  |  | 8.106 |
  | N32 | 32 | 128 |  |  |  | 7.242 |
  | N64 | 64 | 256 |  |  |  | 7.278 |
  | N128 | 128 | 512 |  |  |  | 7.121 |

- Command: `python3 -m compileall -q scripts/grok_node_scaling_compare.py`.
  Result: succeeded.
- Command: `git diff --check`.
  Result: clean.

## 2026-06-25 01:35-01:45 CEST - Additional Local Reproducibility Sweep

- Objective: run the broadest local-safe artifact checks after adding the Grok comparison helper, without expanding large Grok traces or launching expensive LP jobs.
- Machine/environment: `Linux LAPTOP-CJL91217`, artifact repository `/home/tbonato/LLAMP_Test/SC_Tracing`, branch `clean_version_local`, starting commit `9258529`.
- Command: `df -h /home/tbonato/LLAMP_Test && free -h`.
  Result: local filesystem had about 6.3 GB free; memory was 19 GiB total, about 16 GiB available, plus 5.0 GiB swap.
- Command: `/usr/bin/time -f 'list elapsed=%E maxrss_kb=%M' python3 reproduce_all.py --list`.
  Result: succeeded; listed packaged figure mappings for paper figures 1, 3, 4, 5, 6, 7, 8/9, and 10. Runtime 0.06 s; max RSS 11,784 KiB.
- Command: `/usr/bin/time -f 'all_figures elapsed=%E maxrss_kb=%M' python3 reproduce_all.py`.
  Result: succeeded; regenerated all packaged figure PDFs under ignored `figures/`. Runtime 32.96 s; max RSS 190,708 KiB.
- Command: `/usr/bin/time -f 'pipeline_fig3 elapsed=%E maxrss_kb=%M' python3 reproduce_all.py --pipeline --only 3`.
  Result: succeeded; replayed the shipped demo GOAL with LogGOPSim at `L=0,1000,10000,100000` and regenerated Fig. 3. Runtime 5.18 s; max RSS 134,868 KiB. Reported demo runtimes were 1.272 ms, 1.302 ms, 1.572 ms, and 4.272 ms.
- Command: `/usr/bin/time -f 'artifact_check elapsed=%E maxrss_kb=%M' python3 scripts/check_artifact.py`.
  Result: succeeded; checked help surfaces, Tier C dry-run, compile checks, and one packaged figure regeneration. Runtime 3.52 s; max RSS 82,468 KiB.
- Command: `/usr/bin/time -f 'pytest elapsed=%E maxrss_kb=%M' python3 -m pytest -q`.
  Result: succeeded; `5 passed`. Runtime 3.98 s; max RSS 82,700 KiB.
- Command: `/usr/bin/time -f 'compileall elapsed=%E maxrss_kb=%M' python3 -m compileall -q pipeline scripts tools/nccl_generator solver/llamp_nccl tests reproduce_all.py`.
  Result: succeeded. Runtime 0.14 s; max RSS 13,964 KiB.
- Command: `bash -n pipeline/build_tools.sh pipeline/reproduce_fig5_from_nsys.sh solver/graph_gen.sh solver/lp_analysis.sh`.
  Result: succeeded; shell syntax OK.
- Command: `/usr/bin/time -f 'tierc_dryrun elapsed=%E maxrss_kb=%M' bash pipeline/reproduce_fig5_from_nsys.sh --dry-run`.
  Result: succeeded without downloads or generated files. It reported `nsys` missing from `PATH` and all Python dependencies present. Runtime 0.35 s; max RSS 9,244 KiB.
- Command: `/usr/bin/time -f 'grok_compare elapsed=%E maxrss_kb=%M' python3 scripts/grok_node_scaling_compare.py`.
  Result: succeeded; regenerated ignored Grok comparison CSV/Markdown/PDF/PNG under `figures/grok_node_scaling/`. Runtime 2.08 s; max RSS 110,956 KiB.
- Command: `rm -f /tmp/sc_tracing_demo_comm_dep.csv; /usr/bin/time -f 'lgs_comm_dep elapsed=%E maxrss_kb=%M' python3 pipeline/run_lgs.py --goal data/traces/demo_allreduce_16r_1MiB.goal --L 1000 --G 0.04 --o 200 --g 5 --comm-dep-out /tmp/sc_tracing_demo_comm_dep.csv; wc -l /tmp/sc_tracing_demo_comm_dep.csv`.
  Result: succeeded; patched LogGOPSim reported runtime 1.302 ms and emitted a 480-line demo `comm_dep` CSV. Runtime 0.05 s; max RSS 12,456 KiB.
- Command: `/usr/bin/time -f 'monolithic_dryrun elapsed=%E maxrss_kb=%M' python3 pipeline/run_monolithic_lp.py --goal data/traces/demo_allreduce_16r_1MiB.goal --out /tmp/sc_tracing_demo_full_runtime.csv --l-min 0 --l-max 0 --step 1000 --dry-run`.
  Result: succeeded; printed the expected `solver/main.py -a sensitivity` command and did not launch Gurobi. Runtime 0.03 s; max RSS 11,744 KiB.
- Command: `/usr/bin/time -f 'nccl_generator_dryrun elapsed=%E maxrss_kb=%M' python3 pipeline/run_nccl_generator.py --sqlite-dir /home/tbonato/LLAMP_Test/data/raw/mixed20_annotated/mixed20_atlahs_rerun_results_20260403_annotated_rerun/mixed20_rand16to64_2n_ch1_job1791879/trace/nsys_reports --out-dir /tmp/sc_tracing_nccl_generator_dryrun --dry-run`.
  Result: succeeded; wrapper resolved the generator command, NPKit JSON inputs, and found 8 local SQLite rank files. Runtime 0.03 s; max RSS 11,740 KiB.
