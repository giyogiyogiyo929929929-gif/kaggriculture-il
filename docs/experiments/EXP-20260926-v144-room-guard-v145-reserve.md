# EXP-20260926: v144 public room_guard / v145 planned-SELL reserve

## Champion

- Formal champion: exact `v115_champion_same_turn_open_squeeze.py`.
- Exact SHA-256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`.
- Do not promote from this experiment until matched seeds, seat swap, sealed tests, important-opponent regression, runtime, and telemetry all pass.

## v144

Parent: exact v115.

Hypothesis: enabling the dormant public tetsutani `room_guard` prevents hour-23 shed overflow destruction by adding emergency SELLs before carried inventory is returned to the shed.

Change: exactly one dormant capability switch, `'room_guard': False -> True`; budget_guard, clamp_sells, dead_stock, terminal_liquidation, and front_run remain disabled.

### Burned direct screen

Development-only seeds, direct v144 vs exact v115, both seats, pair delta = average candidate-minus-champion final money across seat swap:

- seed 683: `+492`
- seed 689: `-84`
- seed 693: `+479`

These seeds are burned and are not promotion evidence.

### Hard-opponent panel (run 36142946286; partial)

Environment: `kaggle-environments==1.32.7`; seeds 711001..711003; candidate and champion are each evaluated against the same opponent/seed with seat swap. Metric is `candidate_minus_champion = candidate - champion`.

| Opponent | mean cash delta | worst pair | best pair | outcome improved | outcome worsened | exceptions |
|---|---:|---:|---:|---:|---:|---:|
| jaxa_2802 | +181.333 | +2 | +524 | 0 | 0 | 0 |
| score_2820 | +176.000 | +1 | +524 | 0 | 0 | 0 |
| tetsutani_dpts_b | +176.333 | 0 | +513 | 0 | 0 | 0 |
| v50 | +1.000 | 0 | +3 | 0 | 0 | 0 |
| k256_h2_q_v1 | +104.000 | -17 | +331 | 0 | 0 | 0 |
| salem_2900 | +35.333 | 0 | +94 | 0 | 0 | 0 |
| kf_v58 | +128.000 | +7 | +297 | 0 | 0 | 0 |

Partial aggregate over 7 opponents / 21 matched seed-pairs: `15W / 2L / 4T` by cash delta, mean `+114.571`, worst `-17`, best `+524`. The two negative pair deltas are both against `k256_h2_q_v1` (`-2`, `-17`). All 42 outcome cells remain the same outcome; the champion and candidate both win every completed cell. Therefore this panel currently shows cash improvement but no win/loss conversion evidence.

Remaining hard-panel opponents at the time of this log: `peak_2950`, `metav4_v13`, `v49`.

## Telemetry correction

The first telemetry run `36140907244` produced unusable traces and is not causal evidence.

`ci/diagnose_public_room_guard.py` now validates the original direct screen correctly as pair-averaged direct margins: seed 683 is generated from seat margins `+984` and `0`, averaging to `+492`; expected pair deltas are 683 `+492`, 689 `-84`, 693 `+479`.

GitHub-hosted telemetry run `36168760165` failed before useful job steps. The workflow was moved to the self-hosted Windows runner in commit `97e98de1f1856943c7c6589cb4fd9843a6d01860`; run `36171032150` is queued. It also uploads a source context around the exact-v115 room_guard for audit.

## v145 candidate

Parent conceptually: v144 behavior, implemented from exact v115 by enabling room_guard and replacing only its emergency SELL selection loop.

Hypothesis: v144's regression surface comes from consuming inventory already committed to later native SELLs. Preserve future planned SELL quantity on the first emergency pass; only consume that reserve if surplus-only selling cannot create enough physical shed room.

Implementation: `ci/build_v145_room_guard_planned_reserve.py` (commit `e72258e24cefe89746c362c7e784030f3a28449e`). The original room_guard priority order is retained. First pass caps each item's emergency availability to `current unsold shed - future_sells(route,item,step+1)`. If `needed > 0` remains, a second pass falls back to the original availability/priority. `_add_sell(..., merge=True)` means the fallback can extend an existing same-item SELL without consuming an extra market slot.

Focused workflow: `.github/workflows/v145-room-guard-reserve-focused.yml`, commit `9f02447e9dd00c6da0508525bd079c4da2062236`, run `36171236186` queued. It reconstructs exact v115, builds v144/v145, compiles them, verifies the one intended source delta, then runs direct v144 and v145 vs exact v115 on burned seeds 683/689/693 with seat swap. It asserts v144 reproduces `+492/-84/+479` before interpreting v145.

## Current decision

- Champion: **exact v115 unchanged**.
- v144: **KEEP TESTING**. Positive cash signal so far, but no outcome conversions and a small hard-panel tail regression exists.
- v145: **TESTING / not eligible for promotion yet**.
- No PROMOTE action.

## Next

1. Finish hard-panel run `36142946286` and recompute aggregate including `peak_2950`, `metav4_v13`, `v49`.
2. Collect corrected telemetry run `36171032150`; identify first action divergence, added emergency SELL item/quantity, and later native SELL evidence on seeds 683/689/693 both seats.
3. Collect v145 focused run `36171236186`. Determine whether seed 689 regression is reduced without losing the seed 683/693 gains.
4. Only if v145 is causally supported and tail-safe, run fresh matched/seat-swapped seeds, then sealed seeds and important-opponent regression. Burned seeds must not be used for promotion.
