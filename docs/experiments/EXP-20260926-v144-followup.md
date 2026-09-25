# EXP-20260926 v144 public room_guard follow-up

## Status

- Champion: exact v115 (`c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`)
- Candidate: v144 public tetsutani `room_guard` only (`420dbce1ccf454900076bd3c0c10d6bfae5a057c99f5d500f7148196ab9b420e`)
- Decision: KEEP TESTING
- PROMOTE: no

## Diagnostic correction

The first causal telemetry run (`36140907244`) was invalid: all six cases returned `trace_len=0` and zero deltas even though the direct screen had non-zero v144-v115 pair deltas.

A later diagnostic revision correctly forced normal closure invocation and required long traces, but its screen self-check still compared each *per-seat direct margin* with the *pair-averaged screen cash delta*. That is dimensionally wrong. Example: seed 683 direct screen had seat margins `+984` and `0`, whose pair average is `+492`.

`ci/diagnose_public_room_guard.py` is now corrected to:

1. run exact v115 vs exact v115 and v144 vs exact v115 for both seats,
2. require `trace_len >= 700`,
3. require a real action divergence,
4. record first divergent action, added/removed market orders, shed/market state, and next-96-turn SELL evidence,
5. validate the average of the two candidate-v115 direct seat margins against the original direct-screen pair delta for each seed: seed 683 `+492`, seed 689 `-84`, seed 693 `+479`.

This telemetry uses already-burned seeds and is causal diagnosis only, not promotion evidence.

## Hard-opponent panel (`36142946286`)

Metric is `candidate_minus_champion = candidate - champion`, pair-averaged across both seats against the same opponent and seed. Three seeds per opponent starting at 711001.

Completed so far:

| opponent | mean | worst | best | outcome conversion | exceptions |
|---|---:|---:|---:|---|---:|
| jaxa_2802 | +181.333 | +2 | +524 | 0 improved / 0 worsened | 0 / 0 |
| score_2820 | +176.000 | +1 | +524 | 0 improved / 0 worsened | 0 / 0 |
| tetsutani_dpts_b | +56.333 | +1 | +167 | 0 improved / 0 worsened | 0 / 0 |
| v50 | +66.333 | +1 | +197 | 0 improved / 0 worsened | 0 / 0 |

For all four completed opponents, champion and candidate had the same win/loss outcome in all six seat-cells. Therefore these are cash-margin improvements, not demonstrated win conversions.

Still queued at the time of this log: `kf_v58`, `peak_2950`, `salem_2900`, `k256_h2_q_v1`, `metav4_v13`, `v49`.

## Next hypothesis

Do not build/promote a reserve variant until corrected causal telemetry identifies the first room_guard divergence on seeds 683/689/693. If the seed-689 regression is caused by room_guard selling inventory that exact v115 planned to SELL later, the next isolated candidate should reserve planned SELL quantity first:

`room_guard_disposable_qty = max(0, shed_qty - future_planned_sell_qty)`

Use disposable quantity first; only consume planned-SSELL reserve if overflow remains. This should be a separate candidate with one principal tactical change.

## Required next steps

1. Wait for corrected telemetry workflow to execute; inspect seed 689 against 683/693 controls.
2. Finish the hard-opponent panel and check worst regression/outcome conversions.
3. If planned-SELL front-loading is confirmed, build the reserve candidate separately.
4. static/syntax -> focused synthetic -> runtime/preflight -> matched seeds + seat swap -> telemetry -> stress -> sealed -> important-opponent regression.
5. Keep exact v115 as champion unless full promotion criteria are met.
