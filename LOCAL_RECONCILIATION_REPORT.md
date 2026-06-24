# Local Reconciliation Report

This file summarizes what was found during the local lightweight pass on
2026-06-24. It is a merge aid for later reconciliation with any high-RAM
`clean_version` work.

## Repository State

- Artifact checkout: `/home/tbonato/LLAMP_Test/SC_Tracing`
- Working branch: `clean_version_local`
- Base: `origin/main` at `90231b14a03b526b406fb4811229b5544cc2a5c4`
- Remote artifact branches visible locally: only `main`
- Development checkout: `/home/tbonato/LLAMP_Test`, remote
  `https://github.com/tommasobo/Traces_Compression.git`, branch
  `codex-analytical-formula-comparison` at `87a1ab6c444c68ce4c6525ec545f4fd731c8f644`
- Development `origin/main` after fetch: `22bafa59da27f9374ea301c28c1429a12e593d2a`
- Important caution: the development checkout is very dirty and contains many
  untracked outputs, raw/generated trace artifacts, local tool installs, and
  paper PDFs. It should not be treated as a clean source of truth.

## Local-Only Material Found

- `/home/tbonato/LLAMP_Test/artifact_sc26`: an untracked artifact-style tree
  with generated figures, extra pipeline wrappers, `tools/nccl_generator/`,
  small NPKIT reference JSONs, and built LogGOPSim artifacts.
- `/home/tbonato/LLAMP_Test/workspaces/publish_traces_compression_20260331`:
  a 3.8 GiB dirty local checkout with refreshed plots and one modified
  `scientific_policies.py`.
- `/home/tbonato/LLAMP_Test/tmp_publish_traces_main_wt`: a 183 MiB local
  worktree with modified closed-prefix generator files; `git fetch` reported
  a remote-ref lock error, so its freshness is unclear.
- Claude memory files in `/home/tbonato/.claude/projects/-home-tbonato-LLAMP-Test/memory/`
  record useful LLAMP/NCCL status, including Llama 202-collective stats and a
  note that Gurobi `Method=1` was faster for parametric sweeps.
- Codex session index contains relevant older sessions such as artifact
  preparation, figure updates, and LLAMP/NCCL debugging. Raw session logs were
  not imported into the artifact repository.

## Local Changes Made In This Branch

- Added this reconciliation report and `LOCAL_PROGRESS_LOG.md`.
- Added optional Tier C source pieces from local `artifact_sc26`:
  - `tools/nccl_generator/`
  - `pipeline/run_monolithic_lp.py`
  - `pipeline/run_nccl_generator.py`
  - `pipeline/reproduce_fig5_from_nsys.sh`
  - `data/npkit/npkit_alps_simple.json`
  - `data/npkit/npkit_alps_ll.json`
- Added `requirements-tierc.txt` so default figure reproduction stays light.
- Clarified README reproduction tiers and hardware/software boundaries.
- Fixed `pipeline/demo.py` so the default LGS-only demo no longer claims to
  write persistent output files.
- Added small output flushing in `reproduce_all.py` and `pipeline/demo.py` so
  parent progress messages appear before child process output.
- Added root-level artifact smoke tests under `tests/` and `pytest.ini`, so
  `python3 -m pytest -q` now validates the artifact path instead of collecting
  stale historical solver tests by default.
- Added `scripts/check_artifact.py` for local-safe syntax/help/import/data
  checks, with optional single-figure and pipeline-demo checks.
- Hardened Tier C:
  - `pipeline/reproduce_fig5_from_nsys.sh --dry-run` reports the plan and
    dependency status without downloading or generating files.
  - The script stops before the expensive Monolithic-LP step unless `--run-lp`
    is passed.
  - `pipeline/run_monolithic_lp.py` and `pipeline/run_nccl_generator.py` now
    support `--dry-run`.
- Documented `solver/test/` as legacy historical tests, not the default
  artifact test path.

## First-Pass Audit Result

- No newly tracked generated figures, logs, SQLite files, nsys captures,
  Gurobi license files, built LogGOPSim binaries, or Python bytecode were
  found.
- The large NPKIT JSON files are intentional Tier C inputs ported from local
  `artifact_sc26`.
- Absolute local paths appear only in the local progress/reconciliation docs
  and are intentional merge context.
- Extended `.gitignore` for Tier C outputs and regenerated CSV sidecars.

## Lightweight Reproduction Results

- `python3 reproduce_all.py --list`: succeeded.
- `python3 reproduce_all.py`: succeeded in 38.9 s, max RSS 191296 KiB.
  All packaged figure PDFs reported `OK`.
- `python3 reproduce_all.py --pipeline --only 3`: succeeded in 20.9 s, max
  RSS 374548 KiB. This built LogGOPSim and replayed the shipped demo GOAL at
  four latency points.
- After LogGOPSim was built, the same `--pipeline --only 3` check succeeded
  in 3.98 s, max RSS 134764 KiB, with ordered console output.
- Wrapper checks succeeded:
  - `python3 pipeline/run_monolithic_lp.py --help`
  - `python3 pipeline/run_nccl_generator.py --help`
  - `bash -n pipeline/reproduce_fig5_from_nsys.sh`
  - `python3 -m compileall -q pipeline tools/nccl_generator solver/llamp_nccl`
- Second-pass checks:
  - `python3 scripts/check_artifact.py --skip-figure`: succeeded.
  - `python3 -m pytest -q`: succeeded, 5 passed.
  - `git diff --check`: succeeded.
  - `python3 reproduce_all.py --list`: succeeded.
  - `python3 reproduce_all.py --pipeline --only 3`: succeeded in 4.40 s,
    max RSS 134868 KiB.
  - `python3 -m compileall -q pipeline tools/nccl_generator solver/llamp_nccl`:
    succeeded in 0.02 s, max RSS 11064 KiB.
  - `python3 scripts/check_artifact.py`: succeeded in 2.10 s, max RSS
    82476 KiB, including one packaged Fig. 7 regeneration.

## Tests And Known Gaps

- `solver/test/` remains as legacy historical tests and is not collected by
  default. Earlier direct runs failed due to missing historical test data and
  stale graph assumptions.
- Tier C was not run locally. It requires Nsight/Gurobi and can become
  expensive; the local branch validates dry-run/help/syntax/import surfaces.
- No 4,096-GPU, monolithic-LP-at-scale, LGS-at-scale, retracing, or full trace
  downloads were attempted.

## Likely Merge Points

- Safe to merge immediately if not already present:
  - README tier clarification.
  - `pytest.ini`, `tests/test_artifact_smoke.py`, and `scripts/check_artifact.py`.
  - Tier C safety flags and clearer dry-run behavior.
- Needs manual review against high-RAM `clean_version`:
  - `tools/nccl_generator/`
  - `data/npkit/*.json`
  - Tier C wrapper defaults, especially whether high-RAM has newer trace paths.
- Reconcile `pipeline/run_lgs.py` with the local `artifact_sc26` variant if
  intra-node LGS parameters are still needed in the final artifact.
- Do not merge local-only/generated material from the development tree:
  - built LogGOPSim binaries,
  - generated figures,
  - `tier_c_fig5/`,
  - raw nsys/sqlite outputs,
  - dirty workspaces under `/home/tbonato/LLAMP_Test/workspaces/`.

## Reconciliation Commands

Useful commands before merging with the high-RAM branch:

```bash
git fetch origin
git log --oneline --graph --decorate --all --max-count=30
git diff --stat origin/main...clean_version_local
git diff --name-status origin/main...clean_version_local
```

If a remote `clean_version` branch becomes visible:

```bash
git fetch origin clean_version
git diff --stat origin/clean_version...clean_version_local
git diff --name-status origin/clean_version...clean_version_local
git log --oneline --graph --decorate origin/clean_version clean_version_local --max-count=40
```

After any merge, rerun:

```bash
python3 -m pytest -q
python3 scripts/check_artifact.py --skip-figure
python3 reproduce_all.py --list
python3 reproduce_all.py --pipeline --only 3
```
