# uploaded 127ed3 CARROT2 feed0 — runtime harness fix — 2026-09-27

Status: **original runtime run INVALID AS PERFORMANCE EVIDENCE; corrected run queued**

## Candidate identity

- Candidate: `uploaded_127ed3_ca_feed0`
- SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- Formal parent/champion: `uploaded_127ed3_safety_v3`
- Formal engine: `kaggle-environments==1.32.7`

## Original run

Run `36295797394` concluded `failure`, but the failure occurred before any timing statistics were produced.

The runtime script called `C.play(timed, 'starter', seed)`. `scripts/analysis/_common.py::play` treats every string as a filesystem agent path and therefore attempted to load `<repo>/starter`.

Observed terminal error:

`FileNotFoundError: ...\\starter`

Therefore this run does **not** show a p99/worst-turn violation. It is a runtime-harness bug, not candidate runtime evidence.

## Fix

Workflow `.github/workflows/uploaded-127ed3-ca-feed0-final-runtime.yml` was updated in commit `bfce7410a8120ef52453594fc64b88116092f5cc`.

The corrected gate:

- keeps exact candidate/parent/v147/engine/source SHA assertions;
- passes builtin `starter` directly to `kaggle_environments.make(...).run(...)`;
- loads v147 as a callable;
- measures candidate action latency on seeds `71,75`;
- measures both seats against both `starter` and v147;
- requires every game `DONE` and 720 turns;
- retains thresholds p99 `< 50 ms` and worst turn `< 200 ms`.

Corrected run: `36301925723`.

Status at this record creation: **queued**.

## Decision

Do not count run `36295797394` as a runtime regression. Promotion remains blocked until corrected run `36301925723` produces valid timing statistics and passes the predefined thresholds.
