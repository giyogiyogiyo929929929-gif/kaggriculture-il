# EXP-20260923-56: archived agents round robin

Status: Implemented (2026-09-23); dynamic enrollment runner active.

## Scope and method

Snapshot locally archived, actually submitted agents listed in `docs/06_submission.md`, every `opponents/*/main.py`, and automation `state.json` records with `status=evaluated`. Never execute a notebook. Admit automation agents only when their extracted file SHA matches the recorded SHA, audit report is empty, and preflight/evaluation records exist. Run a static audit on each opponent and exclude missing/unsafe agents with a reason. Submitted code is locally authored or already submitted.

Deduplicate identical single-file agents by SHA, retaining source aliases. Run each unordered canonical pair with one deterministic seed and swapped seats (two 720-turn matches) through `scripts/eval.py`, `-j 1`. This is an exploratory tournament, not a precise ranking; top candidates need extra seeds. Record a frozen manifest, append-only results, progress monitor, exclusions, and final standings. Resume by pair key without repeating completed results. Check the hourly automation monitor before starting each pair and defer while it is processing.

A pilot pair must succeed before full schedule. Launch a hidden runner and separate health watcher; both write PID lifecycle events to `data/automation/background-processes.log`. The watcher reports completion/failure. No Kaggle submission or network access is part of this run.

## Acceptance

- All eligible, unique agents are scheduled exactly once per unordered pair.
- A result is durable after each pairing and a restart skips it.
- Missing, changed, or quarantined artifacts are never run; exclusion reason is visible.
- Monitor and watcher show terminal status and log both process stops.

## Dynamic enrollment extension (user request, 2026-09-23)

While the tournament is running, re-read the automation ledger at least every 30 minutes and after the current schedule drains. New records with `status=evaluated` must pass the same SHA, audit, and successful-evaluation evidence checks. Append eligible new agents to the existing manifest, preserve canonical IDs and completed pair results, then schedule only newly created unordered pairs. Identical-code arrivals add aliases but no redundant matches. Keep exclusion reasons. A controlled restart of the already running process must preserve its result ledger and watcher lifecycle log.

Implemented in `refresh_manifest()`. Unit tests: 3 passed. At the controlled restart, 18 completed pairings were preserved. New runner PID 11536 and watcher PID 31480 started at 16:50:57 JST. The manifest expands as evaluated automation entries arrive; the `total` field increases by the number of new pairings. The old runner and watcher were stopped with lifecycle entries; an in-flight pairing at the handoff may be repeated, but completed ledger entries are skipped.

## Implementation and pilot

`scripts/analysis/round_robin.py` and `scripts/start_round_robin.py` implement the snapshot, audit, deduplication, paired matches, resume, standings, hidden launch, and watcher. Initial discovery found 77 eligible source entries / 65 unique agents / 2,080 pairings; 23 source entries were excluded with recorded reasons (mostly static audit warnings). The v22-v27 pilot completed both seats without exceptions in 24.0 seconds; at this rough rate the full run could take ~14 hours plus automation deferrals. `tests/test_round_robin.py`: 2 passed. This initial round robin uses one seed per pairing and should not be treated as a statistically decisive ranking.
