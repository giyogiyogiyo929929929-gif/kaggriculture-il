# EXP-20260926 v135 runner blocker / evaluation hardening

Status: **INFRASTRUCTURE ISSUE; v135 FORMAL EVIDENCE STILL PENDING**

## Formal context

- Formal champion: `v121_champion_same_turn_unwind.py`
- Candidate waiting for evaluation: `v135_candidate_milk_quote_boundary.py`
- Formal focused run: `36144084808`
- Formal job: `108100737763`
- Engine target: `kaggle_environments==1.32.7`
- Difference convention: `candidate_minus_champion = candidate - champion`
- `v66` is not used.

## Runner state

After the self-hosted Windows runner `CIYOI` was restarted, it successfully completed the v133 positive telemetry run `36141048570`, so runner connectivity is healthy.

The formal v135 run remains queued because `CIYOI` is occupied by exploratory v115-lineage run `36143337087` (`v147 self-hosted public panel`). The active job is `108098248881` on runner `CIYOI` with labels `[self-hosted, Windows, X64]`.

That job entered step `Reproduce historical v140 public panel exactly` at `2026-09-25T16:43:05Z` and remained in that step across repeated checks. The workflow uses `ci/eval_candidate_vs_champion_panel.py`, which delegates to `scripts.eval.evaluate()` and `ProcessPoolExecutor.map()` without an individual-game wall timeout. Therefore one hung game/worker can block the whole step until the workflow-level timeout.

This is infrastructure evidence only. It is not evidence for or against v135.

## Hosted fallback attempt

A development-only hosted workflow was added:

- `.github/workflows/v135-ubuntu-dev-screen.yml`
- commit `83c31c52d2140a40a007340170c1f025da06f837`
- run `36163962833`
- job `108167058986`

The job failed in approximately two seconds with `steps=[]`, `runner_id=0`, and no runner name. No candidate code or Kaggriculture game executed. Treat this as hosted-runner / account infrastructure failure, not candidate failure and not evaluation evidence.

## Timeout mitigation

Added `scripts/ci/run_exact_pair_guarded.py` in commit `c7df39cfa811efe1266f77e6891cf6e3e8a12eeb`.

The guard:

- leaves the existing exact evaluator unchanged;
- preserves official-engine execution, seat swap, scoring, and diff convention;
- wraps each already-isolated single game with a wall timeout;
- defaults to 180 seconds per game (`KAGGRICULTURE_SINGLE_GAME_TIMEOUT_SECONDS` overrides it);
- converts timeout into explicit `RUN-TIMEOUT`, exceptions, and `ok=False` so a timeout can never become promotion evidence.

The currently queued formal run `36144084808` is pinned to its earlier commit and therefore does not use this guard. Use the guarded runner for any newly triggered formal/resume workflow if the original run stalls after assignment.

## Decision

**KEEP TESTING. Formal champion remains v121.**

Do not PROMOTE or REJECT v135 from runner scheduling state.

Next executable step is still the intended v135 matched-seat panel. If the original formal run executes successfully, use it. If it hangs or fails technically, rerun the same evaluation with the guarded runner before changing candidate logic.

## 2026-09-26 follow-up

- The previously blocking exploratory run `36143337087` later completed successfully. Its job `108098248881` finished all evaluation and artifact-upload steps.
- Its `v147` artifact is not a promotion signal for the formal v121 line: `v147_confirmed_v111_clone` was exactly tied with its own `v115_champion_same_turn_open_squeeze` baseline on all 24 paired rows (0 wins / 0 losses / 24 draws, mean `candidate_minus_champion = 0.0`, exceptions 0).
- After that completion, repository Actions showed `0` jobs in progress and `9` queued runs. Formal v135 run `36144084808` / job `108100737763` was still queued.
- This changes the blocker diagnosis: the earlier long-running v147 job is no longer occupying `CIYOI`; the remaining evidence is consistent with the self-hosted runner not currently accepting jobs. No candidate logic conclusion follows from this state.
- Do not create duplicate unguarded v135 evaluations while the original formal job is still queued. Once `CIYOI` is accepting work again, consume the existing formal run first; if it hangs or fails technically after assignment, switch to the guarded exact runner.

Decision remains **KEEP TESTING; champion v121 unchanged**.
