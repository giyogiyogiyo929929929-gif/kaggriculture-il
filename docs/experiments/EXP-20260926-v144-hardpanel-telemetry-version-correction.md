# EXP-20260926: v144 hard-panel / telemetry / version correction

## Canonical state

- Formal Champion remains `v115_champion_same_turn_open_squeeze.py`.
- Exact Champion SHA-256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`.
- Formal engine: `kaggle_environments==1.32.7`.
- Delta convention: `candidate_minus_champion = candidate - champion`.
- `v66` is forbidden and was not used.
- v144 remains **KEEP TESTING / NOT PROMOTED**.

## Version collision correction

An older branch-local experiment created files/logs named `v145` for a planned-SELL-reserve room_guard variant. This numbering is now superseded by the current canonical project state: **v145 has already been used for the public four-turn-sales audit/candidate and must not be reused**.

Therefore:

- old `ci/build_v145_room_guard_planned_reserve.py`, `.github/workflows/v145-room-guard-reserve-focused.yml`, and `EXP-20260926-v144-room-guard-v145-reserve.md` are historical/stale naming only;
- they are not a current candidate and are not eligible for promotion;
- if causal telemetry confirms planned-SELL reserve invasion, the isolated reserve candidate must be recreated/referenced as **v146 or later**;
- no v146 is declared active until that causal predicate is confirmed dynamically.

The old source can be used as implementation reference because it contains the intended one-change two-pass selection logic, but results must be attributed to the correctly versioned candidate only after rebuilding/revalidation.

## Hard-opponent run 36142946286

Protocol: exact v115 and v144 are evaluated independently against the same opponent/seed/seat; seeds `711001..711003`; seat swap; one opponent per resumable job. Primary decision metric is actual outcome conversion, not final-cash padding.

Completed artifacts at this checkpoint: 9/10 opponents (`v49` still queued).

| opponent | mean cash delta | worst pair | best pair | outcome improved | outcome worsened | exceptions |
|---|---:|---:|---:|---:|---:|---:|
| jaxa_2802 | +181.333 | +2 | +524 | 0 | 0 | 0 |
| score_2820 | +176.000 | +1 | +524 | 0 | 0 | 0 |
| tetsutani_dpts_b | +176.333 | 0 | +513 | 0 | 0 | 0 |
| k256_h2_q_v1 | +104.000 | -17 | +331 | 0 | 0 | 0 |
| kf_v58 | +128.000 | +7 | +297 | 0 | 0 | 0 |
| salem_2900 | +35.333 | 0 | +94 | 0 | 0 | 0 |
| v50 | +1.000 | 0 | +3 | 0 | 0 | 0 |
| metav4_v13 | +151.333 | -2 | +434 | 0 | 0 | 0 |
| peak_2950 | +193.000 | -5 | +584 | 0 | 0 | 0 |

Aggregate over 9 opponents / 27 matched seed-pairs / 54 seat-games:

- pair cash delta: 18 positive / 4 negative / 5 tie;
- mean `+127.370`;
- worst `-17`;
- best `+584`;
- candidate/champion exceptions: 0;
- outcome matrix: **52 W->W, 2 L->L, 0 improved conversions, 0 worsened conversions**.

Important control: `metav4_v13` seed 711002 remains a loss in both versions (Champion margin -525, candidate margin -487), so the cash/margin improvement is not a loss-to-tie/win conversion.

Interpretation: v144 still shows broad cash uplift with a small tail regression, but **the completed hard panel provides no demonstrated rating-relevant outcome improvement**. Do not promote on this evidence.

## room_guard static audit

The exact inherited room_guard subtracts current-turn planned SELL from `avail`, but later route SELLs only affect boolean priority. It does not quantitatively reserve later planned SELL inventory. Therefore the proposed failure mode is mechanically possible:

1. no-future-SELL stock is sold first;
2. if insufficient, the guard may emergency-sell stock expected by a later native SELL;
3. this can front-load inventory into a worse quote/market state or starve a later scheduled sale.

This is a **static mechanism**, not yet proof that it caused seed689 `-84`.

## telemetry repair

`ci/diagnose_public_room_guard.py` was repaired to:

- require long traces;
- record the first exact v115/v144 action divergence;
- monkeypatch/probe `_room_guard` before/after action mutation;
- capture shed, carried inventory, current-turn production/consumption, BUY/current SELL, projected shed, overflow/guard need, item-wise future planned SELL quantity and future SELL schedule, market inventory/price, and town context;
- validate the original direct screen correctly as **pair-averaged candidate-v115 direct margins** (`683 +492`, `689 -84`, `693 +479`) rather than comparing a per-seat margin with a pair average.

The latest GitHub-hosted Ubuntu telemetry attempt ended with `steps=[]` before code execution. This is infrastructure failure and is not tactical evidence. Self-hosted telemetry runs remain queued at this checkpoint.

## decision / next gate

- Champion: **exact v115 unchanged**.
- v144: **KEEP TESTING**, but current hard-panel rate evidence is null (0 outcome conversions).
- v146 planned-SELL-reserve: **not active yet**; create only if corrected seed683/689 telemetry shows that the divergent room_guard SELL consumed later planned SELL inventory in the regression case.
- Sealed seeds remain unconsumed.

Next execution order after telemetry becomes available:

1. causal compare seed683 vs seed689 both seats;
2. if confirmed, rebuild the reserve logic as v146 (one principal tactical change);
3. focused synthetic cases (overflow/no-overflow/future reserve/free excess sufficient/free excess insufficient);
4. syntax + formal preflight/runtime;
5. burned 683/689 controls vs v144 and exact v115;
6. fresh matched/seat-swapped direct seeds;
7. hard opponents/outcome conversion;
8. stress, then sealed only if still promising;
9. known-opponent regression and final runtime;
10. PROMOTE / KEEP TESTING / REJECT.
