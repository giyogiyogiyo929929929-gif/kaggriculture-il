# EXP-20260926 v149 late-game second-pass guard

## Status

**Decision: KEEP TESTING — evaluation queued, not eligible for promotion.**

Formal champion remains exact `v115_champion_same_turn_open_squeeze`.

## Version / parent / champion

- candidate: `v149_v147_late_guard`
- builder: `ci/build_v149_v147_late_guard.py`
- parent behavior: `v147_confirmed_v111_clone`
- formal champion: `v115_champion_same_turn_open_squeeze`
- champion SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- metric: `candidate_minus_champion = candidate - champion`

## Hypothesis

v148 demonstrated that duplicate-same-item SELL is not sufficient to explain v147's seat risk. The known adverse single-seat case first diverges very late (seed 691, step 673), while representative clean positive divergences occur earlier (seed 681 step 552, seed 682 step 481, seed 689 step 409).

Preserve v147's confirmed second-pass reorder before step 648, but disable that second pass for the final 72 turns. The aim is to retain the earlier order gains while preventing late market-order perturbations that have little time to mean-revert and can become seat-sensitive.

## Change

One tactical change only:

- if `step >= 648`, skip the confirmed second `_v111_reorder` pass;
- all parent farm strategy, sale quantities, clone confirmation, and earlier second-pass behavior remain unchanged.

## Focused synthetic test

A minimal deterministic wrapper test was run outside the Kaggle engine to validate the new guard logic in isolation:

- first-pass change creates a probe;
- equal own/rival realized cash deltas confirm clone state on the following observation;
- confirmed second-pass reorder remains active before step 648;
- at step 648 the parent market action is returned unchanged and the `late_guard` counter fires;
- wrapper errors: 0.

Result: **PASS**. This only validates the guard/control-flow logic; exact generated-agent syntax/runtime and game behavior still require the queued workflow.

## Planned / queued evaluation

1. exact v115 SHA reconstruction and syntax check;
2. seed 681 serial runtime preflight;
3. burned seeds 681..692 with seat swap;
4. focused seed 691 v149-vs-v147 comparison;
5. six-opponent public regression panel, seeds 661..664;
6. only if the focused/burned guard succeeds: unused sealed seeds, stress, final runtime and regression before any promotion decision.

### Infrastructure state

- GitHub-hosted workflow run `36234808209` failed before any job step started (`steps=[]`, `runner_id=0`), so it produced no candidate evidence and is not treated as a model/runtime failure.
- self-hosted Windows workflow run `36234914455` is queued on `[self-hosted, Windows, X64]`.
- separate v148 focused telemetry self-hosted run `36234672144` is also queued.

No sealed seeds have been consumed by v149 yet.

## Decision rule

Do not promote unless v149 removes or materially reduces the seed-691 single-seat downside while retaining broad burned gains, then reproduces on unused sealed seeds without known-opponent/runtime regressions.
