# EXP-20260925: public room_guard

Status: **KEEP TESTING — NOT PROMOTED**

## Canonical state

- Formal Champion: `v115_champion_same_turn_open_squeeze.py`
- Champion SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- Never use v66.
- Engine for formal evaluation: `kaggle_environments==1.32.7`.
- Metric: `candidate_minus_champion = candidate - champion`.

## Public source

Primary mechanism source:

- Kaggle kernel: `tetsutani/shape-the-shop-work-the-pasture-kaggriculture`
- Title at acquisition: `🌾 Shape the Shop Work the Pasture | Kaggriculture`
- Author metadata: `tetsu2131`
- Frozen acquisition time: `2026-09-18T00:47:08.602199+00:00`
- API response SHA256: `7081913fa660b8a060fdb2930243fe18c8079a1e201f2773e9ee044dd7cd0d55`
- Notebook payload SHA256: `a6027339030e6204e512ccf7cc3641cb158531d8924717d089638c276b94744f`
- Decoded source SHA256: `2b97e2c653018ac4aeffb8463ec91c8f26b097b4cef81289acc25ccdbc68f916`
- Mirrored Git blob SHA: `6f7f89ae425caf501a9a987bfded02145c192ffb`

The inherited chassis already contains this public mechanism but exact v115 has it disabled. The candidate changes only:

```text
room_guard: False -> True
```

Explicitly unchanged: budget_guard, clamp_sells, dead_stock, terminal_liquidation, front_run, V92/KIL, farm policy and route tapes.

## Formal screen

Actions run: `36132699144`
Artifact: `v144-public-room-guard-screen`
Artifact ID: `10865546301`
Artifact digest: `sha256:b6b6c707b8034a1f5be1044705284971cef196183472329bd96a8f3d88ed1e33`

All setup/focused/runtime/direct/public/aggregate steps completed successfully.

### Focused synthetic

Passed:

- day-close projected overflow adds only the required SELL;
- no-overflow case remains unchanged;
- non-day-close case remains unchanged.

### Runtime smoke — seed 693, both seats

- direct candidate-v115 pair margin: **+479**
- candidate exceptions: 0
- champion exceptions: 0
- candidate median callback: ~2.71 ms
- candidate max callback: ~56.6 ms
- champion median callback: ~2.65 ms
- champion max callback: ~65.9 ms
- final shed: 0 for both

Runtime is acceptable on this smoke; no timeout/exception evidence.

### Direct candidate vs exact v115 — seeds 681..692, seat swap

12 matched pairs / 24 games:

- W/L/T: **9 / 1 / 2**
- mean candidate-minus-champion: **+49.6667**
- SE: **41.9652**
- worst: **-84** (seed689)
- best: **+492** (seed683)
- candidate exceptions: 0
- champion exceptions: 0

Pair rows:

- 681 +13
- 682 +1
- 683 **+492**
- 684 +5
- 685 +94
- 686 +4
- 687 0
- 688 +2
- 689 **-84**
- 690 +7
- 691 +62 (seat deltas +8/+116)
- 692 0

All other non-zero seeds except691 are identical across the two seats, so the primary direct gain is not explained by a simple seat asymmetry.

### Old easy public panel — seeds 681..684

24 opponent/seed matched rows across starter, beat_v48, bl_v20, bl_v21, farming_v2 and frontier_prvsiyan:

- candidate-money delta W/L/T: **9 / 12 / 3**
- mean candidate-money delta: **+40.8333**
- worst candidate-money delta: **-4**
- best candidate-money delta: **+315**
- exceptions: 0

However, these six opponents are too easy for rating-oriented selection: candidate and Champion have **zero absolute win/loss outcome conversions across all 48 seat-games** in this panel. The positive/negative rows only change cash/margin inside outcomes the Champion already wins.

Therefore this panel is a regression/cash sanity check, not evidence of improved ladder win probability.

## Interpretation

The mechanism is active and direct separation is real. Unlike v143, it shows a broad direct direction: 9 positive pairs, one negative pair and two ties. The effect is concentrated enough that the large +492 seed683 and -84 seed689 must be explained before promotion.

The old public panel does not validate rating gain because it contains no hard cells. Do not infer rating improvement from its positive mean cash delta.

A static audit also shows that a new generic terminal-liquidation candidate would be redundant: although exact-v115 keeps the chassis `terminal_liquidation` setting disabled, the inherited downstream agent already has a final-step projected-shed SELL rescue. Do not create that candidate unless a materially different terminal defect is demonstrated.

## Telemetry follow-up

Files:

- `ci/diagnose_public_room_guard.py`
- `.github/workflows/public-room-guard-telemetry.yml`

Use only already-consumed seeds:

- 683 both seats — largest direct gain
- 689 both seats — only direct regression
- 693 both seats — runtime/direct +479 control

Counterfactual protocol:

- baseline focal: exact v115 vs exact v115
- candidate focal: room_guard vs exact v115
- same seed and focal seat
- record first action divergence, same-observation check, added/removed market order, day/hour, shed, carried inventory, current prices and final focal/margin delta

No unused/sealed seed is consumed by telemetry.

Initial telemetry run `36136980588` reached candidate construction successfully, then failed immediately in the diagnostic step. This was test infrastructure, not tactical evidence. Root cause audit found `ci/diagnose_public_room_guard.py` imported `scripts.eval` without adding the repository root to `sys.path`, unlike the established CI evaluators. Commit `5c2477d67041bae3fd29240701ca5c79f5e5e6b4` adds the repo root before that import. Repair run: `36140907244`.

## Hard-opponent outcome gate

Workflow: `.github/workflows/v144-v115-hard-opponent-screen.yml`
Commit: `17a4b3797dfa683fc51418f2d4b3aec5ffc7473f`
Run: `36140496806`
Development seeds: `711001..711003`, both seats.

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

For every opponent/seed/seat, exact-v115 and v144 are evaluated independently against the same opponent. The primary statistic is outcome conversion, not cash padding:

- improved outcome vs worsened outcome;
- Champion non-win -> candidate win;
- Champion loss -> candidate tie;
- Champion win -> candidate non-win;
- Champion tie -> candidate loss.

Cash and margin delta are secondary diagnostics. The workflow asserts the exact v115 SHA before evaluation. At the latest checkpoint, candidate construction had passed and the 10-opponent evaluation step was running on self-hosted Windows runner `CIYOI`.

Do not allocate sealed seeds until:

1. seed683/689 telemetry explains the gain/regression;
2. the hard-opponent screen shows useful outcome conversion or a clearly defensible safety effect;
3. a fresh direct/stress set preserves positive matched direction with acceptable worst regression.

## Decision

**KEEP TESTING.**

This remains more promising than v143, but the evidence is not sufficient for PROMOTE. Champion remains exact v115.
