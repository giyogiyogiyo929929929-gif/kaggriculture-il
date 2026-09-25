# EXP-20260925: v144 public room_guard

Status: **KEEP TESTING — NOT PROMOTED**

## Canonical state

- Formal Champion: `v115_champion_same_turn_open_squeeze.py`
- Champion SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- v66: **never use**
- Formal engine: `kaggle_environments==1.32.7`
- Delta convention: `candidate_minus_champion = candidate - champion`
- Candidate: `v144_candidate_public_room_guard`
- Parent: exact v115

## Hypothesis / change

The inherited chassis already contains tetsutani's public `room_guard` mechanism but exact v115 leaves it disabled. v144 changes only:

```text
room_guard: False -> True
```

Unchanged: `budget_guard`, `clamp_sells`, `dead_stock`, `terminal_liquidation`, `front_run`, V92/KIL, farm policy and route tapes.

At hour 23, the guard estimates projected storage pressure and adds only enough SELL quantity to remain below capacity. It prioritizes products with no later route SELL, then higher visible price.

## Public source provenance

- Kaggle kernel: `tetsutani/shape-the-shop-work-the-pasture-kaggriculture`
- Frozen acquisition: `2026-09-18T00:47:08.602199+00:00`
- API response SHA256: `7081913fa660b8a060fdb2930243fe18c8079a1e201f2773e9ee044dd7cd0d55`
- Notebook payload SHA256: `a6027339030e6204e512ccf7cc3641cb158531d8924717d089638c276b94744f`
- Decoded source SHA256: `2b97e2c653018ac4aeffb8463ec91c8f26b097b4cef81289acc25ccdbc68f916`
- Mirrored Git blob SHA: `6f7f89ae425caf501a9a987bfded02145c192ffb`

Recheck the direct source license before formal Kaggle submission.

## Formal screen

Actions run: `36132699144`
Artifact: `v144-public-room-guard-screen`
Artifact ID: `10865546301`
Artifact digest: `sha256:b6b6c707b8034a1f5be1044705284971cef196183472329bd96a8f3d88ed1e33`

### Focused synthetic

Passed:

- day-close projected overflow adds only required SELL;
- no-overflow stays unchanged;
- non-day-close stays unchanged.

### Runtime smoke — seed 693, both seats

- direct candidate-v115 pair cash delta: `+479`
- candidate exceptions: 0
- champion exceptions: 0
- candidate median callback: ~2.71 ms
- candidate max callback: ~56.6 ms
- champion median callback: ~2.65 ms
- champion max callback: ~65.9 ms
- final shed: 0 for both

### Direct exact-v115 comparison — seeds 681..692, seat swap

12 matched pairs / 24 games:

- positive / negative / tie pair cash delta: **9 / 1 / 2**
- mean candidate-minus-champion: **+49.6667**
- SE: **41.9652**
- worst: **-84** at seed689
- best: **+492** at seed683
- exceptions: 0 / 0

Per-seed pair deltas:

- 681 +13
- 682 +1
- 683 +492
- 684 +5
- 685 +94
- 686 +4
- 687 0
- 688 +2
- 689 -84
- 690 +7
- 691 +62 (seat deltas +8 / +116)
- 692 0

Except seed691, non-zero pairs were seat-symmetric, so the main direct signal is not a simple seat artifact.

### Old easy public panel — seeds 681..684

Opponents: starter, beat_v48, bl_v20, bl_v21, farming_v2, frontier_prvsiyan.

24 opponent/seed matched rows:

- candidate-money delta positive / negative / tie: **9 / 12 / 3**
- mean: **+40.8333**
- worst: -4
- best: +315
- exceptions: 0
- absolute outcome conversions across 48 seat-games: **0**

These opponents are too easy for rating-oriented selection. This panel is cash/regression sanity only, not evidence of higher ladder win probability.

## Static interaction audit

### v144 is stacked on an existing shed guard

Exact v115 already has a downstream `SHEDROOM` layer acting at hours 21/22/23 with `_SR_MARGIN = 8`. Therefore v144 does not introduce the first storage guard; it enables an earlier chassis room_guard on top of an already guarded policy.

The public room_guard computes current-step planned SELLs, but additional availability is effectively:

```text
avail = shed[item] - current_step_planned_sell[item]
```

Later route SELL quantity only affects a boolean priority key (`has future sell` goes later); it is not subtracted from `avail`. If no-future-sale stock is insufficient, room_guard may sell inventory a later route SELL expects to use.

This is a plausible seed689 regression mechanism, not yet a causal conclusion. Do not implement blanket future-SELL reservation before telemetry: full reservation can itself restore overflow or over-reserve inventory that later production refills.

### Terminal liquidation duplicate audit

Do not create a generic `terminal_liquidation=True` candidate. Although the chassis flag is disabled in exact v115, a downstream v115 wrapper already performs final projected-shed liquidation near the terminal step. A new generic toggle would be largely duplicate unless a materially different terminal defect is demonstrated.

### General dead stock remains separate

v115 contains a herd-specific WOOL/MILK surplus seller that subtracts later planned SELLs before liquidating excess. It is not a general all-product dead-stock layer. General dead-stock remains a possible later one-change candidate, but must not be bundled into v144.

## Burned causal telemetry

Files:

- `ci/diagnose_public_room_guard.py`
- `.github/workflows/public-room-guard-telemetry.yml`

Burned cases only:

- seed683 both seats — largest direct gain
- seed689 both seats — only direct regression
- seed693 both seats — runtime/direct +479 control

Protocol:

- baseline focal: exact v115 vs exact v115
- candidate focal: v144 vs exact v115
- same seed and focal seat
- compare first action divergence, observation identity, added/removed market orders, shed/carried state, visible price and final focal/margin delta

Initial telemetry run `36136980588` reconstructed exact v115 and v144 successfully, then failed before any game because `ci/diagnose_public_room_guard.py` could not import `scripts.eval` (`ModuleNotFoundError: No module named 'scripts'`). This is infrastructure/test-code failure, not tactical evidence.

Fix commit: `5c2477d67041bae3fd29240701ca5c79f5e5e6b4` adds repo root to `sys.path`.
Repair self-hosted run: `36140907244`.
Latest state: queued, no runner assigned.

A GitHub-hosted Ubuntu fallback was added in commit `951450d72fa54eaa6a9734e2af866645cec68a58`, run `36143257908`. It ended before any step started (`steps=[]`), so this is another hosted infrastructure/pre-start failure and contains no candidate evidence.

## Hard-opponent outcome gate

Development seeds: `711001..711003`, both seats. No sealed seeds used.

Ten stored opponents:

- `k256_h2_q_v1`
- `metav4_v13`
- `v49`
- `v50`
- `tetsutani_dpts_b`
- `salem_2900`
- `peak_2950`
- `jaxa_2802`
- `kf_v58`
- `score_2820`

Exact v115 and v144 are evaluated independently against the same opponent/seed/seat. Primary metrics are actual outcome conversions:

- improved outcome / worsened outcome
- Champion non-win -> candidate win
- Champion loss -> candidate tie
- Champion win -> candidate non-win
- Champion tie -> candidate loss

Cash/margin delta is secondary.

### Original sequential hard-panel run

Workflow: `.github/workflows/v144-v115-hard-opponent-screen.yml`
Commit: `17a4b3797dfa683fc51418f2d4b3aec5ffc7473f`
Run: `36140496806`
Job: `108088861516`

Setup, exact engine, v115 SHA assertion and v144 construction all passed. The self-hosted runner `CIYOI` then received a shutdown signal during the opponent loop. The evaluation step was cancelled before aggregate/artifact upload. This is **infrastructure cancellation, not tactical failure**.

Seven opponents completed before shutdown. Preliminary mean candidate-minus-champion cash deltas were:

- k256_h2_q_v1: +104
- metav4_v13: +151.3333
- v49: +2
- v50: +1
- tetsutani_dpts_b: +176.3333
- salem_2900: +35.3333
- peak_2950: +193

All completed opponent summaries reported candidate exceptions=0 and champion exceptions=0.

These figures are encouraging diagnostics only. The evaluator deliberately omitted seat rows from stdout, so actual win/tie/loss conversions cannot be reconstructed from the cancelled log. Do not infer outcome improvement from these cash means.

### Resumable hard-panel redesign

To prevent future runner shutdown from discarding all completed work:

- `ci/summarize_single_opponent_outcomes.py`
  - commit `14571f74294edd66103ab378b6ed15efbbe5b58b`
  - derives seat-level actual outcome conversion from each opponent JSON.
- `.github/workflows/v144-v115-hard-opponent-resumable.yml`
  - commit `abd397693d23ddf60ee517e23addb719fbf35f8d`
  - one opponent = one independent matrix job
  - `fail-fast: false`
  - exact 1.32.7 and exact v115 SHA checked in every job
  - each completed opponent uploads its own artifact.

Resumable run: `36142946286`.
Latest state: all 10 jobs queued with no self-hosted runner assigned.

## Promotion gate / next hypothesis

Do not allocate final sealed seeds until:

1. seed683/689 telemetry explains the large gain/regression;
2. hard-opponent evaluation yields useful actual outcome conversion, not cash padding only;
3. a fresh direct/stress set preserves positive matched direction with acceptable worst regression;
4. key-opponent regressions, runtime, exceptions/timeouts remain acceptable.

If seed689 confirms that room_guard consumed inventory required by a later scheduled SELL, the next candidate should make the smallest possible item-selection/reservation change while preserving emergency overflow relief. Do not threshold-sweep and do not blanket-reserve all future SELL quantity without evidence.

If the hard panel produces no outcome conversion and only cash movement, close v144 without spending sealed seeds unless telemetry identifies a tightly localized safety defect worth a separate candidate.

## Decision

**KEEP TESTING — NOT PROMOTED.**

Champion remains exact v115.
