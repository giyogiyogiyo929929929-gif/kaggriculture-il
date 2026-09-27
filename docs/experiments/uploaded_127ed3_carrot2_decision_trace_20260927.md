# uploaded 127ed3 CARROT2 decision-state trace — 2026-09-27

Decision: **ANALYSIS ONLY — CARROT2 late-swap suppression direction closed**

## Identity

- Formal champion under analysis: `uploaded_127ed3_safety_v3`
- Champion SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Comparison reference in focal replays: former champion `v147_candidate_confirmed_v111_clone.py`
- Trace workflow: `.github/workflows/uploaded-127ed3-carrot2-decision-trace.yml`
- Actions run: `36287041338`
- Artifact: `uploaded-127ed3-carrot2-decision-trace`, artifact id `10919874736`
- Focal burned seeds: `641, 350003, 733, 911`, both candidate seats
- No fresh/sealed seed was consumed.

## Instrumentation safety

The trace rebuilt exact uploaded raw, appended the same safety-v3 wrapper, and added observation-only CARROT2 decision logging. It then replayed the exact focal games against reconstructed v147 and asserted final money against the prior diagnostic for every seed/seat.

Behavior identity: **PASS**.

Expected/final results reproduced exactly:

- 641: safety-v3 `64032`, v147 `64438`, delta `-406`
- 350003: safety-v3 `100144`, v147 `100664`, delta `-520`
- 733: safety-v3 `92204`, v147 `88776`, delta `+3428`
- 911: safety-v3 `137651`, v147 `136473`, delta `+1178`

Both seat swaps reproduced the same respective money values reversed.

## What was logged

For every base `PLANT WHEAT` opportunity in the CARROT2 day window, the trace records:

- accepted/rejected reason,
- current WHEAT/CARROT price and market inventory,
- WHEAT stock and 1/2/3-day feed demand,
- spare seeds,
- predicted WHEAT yield `wu`, CARROT normal/rescue yield and chosen `cu`,
- predicted CARROT realization step/horizon,
- current CARROT2 edge,
- WHEAT/CARROT standing plot counts/yield,
- private inventories,
- unlocked Town shops.

## Accepted decisions

| seed | safety-v3-v147 final | all accepted | accepted day>=24 | day27 accepted |
|---:|---:|---:|---:|---:|
| 641 | -406 | 46 | 14 | 7 |
| 350003 | -520 | 29 | 10 | 8 |
| 733 | +3428 | 22 | 13 | 8 |
| 911 | +1178 | 0 | 0 | 0 |

Late accepted-swap count is therefore **not a loss separator**: winning seed 733 has essentially the same late count as 641/350003.

Accepted by day:

- 641: d10 4, d11 8, d12 4, d16 3, d17 1, d18 1, d20 1, d21 5, d22 4, d23 1, d24 6, d26 1, d27 7
- 350003: d18 1, d20 1, d21 5, d22 4, d23 8, d24 1, d26 1, d27 8
- 733: d23 9, d24 5, d27 8
- 911: none; all 130 traced WHEAT-plant opportunities failed the global `pays_now` condition

## Current-price edge

CARROT2 accepts when its route-aware edge is greater than `_CA_MARGIN = -20`.

Accepted edge distribution:

- 641: min `-18`, median `+35`, max `+146`
- 350003: min `-15`, median `+41`, max `+62`
- 733: min `-17`, median `+31`, max `+38`

Again, weak/negative-at-current-price accepts are not unique to the loss seeds.

## Harvest horizon

Median CARROT realization horizon among accepted swaps:

- 641: 71 turns
- 350003: 71 turns
- 733: 70 turns

The late (day >=24) mean horizons are 56.6, 49.8, and 56.5 turns respectively. A simple horizon cap would not distinguish the losses from seed 733.

## Actual-price backcheck

The trace's predicted realization step was joined to the already-saved compact replay market quote at that step. This is not used by the live agent; it is a post-hoc check of whether current CARROT price badly overstates the quote seen when the CARROT would actually be harvested/sold.

For day 26-27 accepted swaps:

- seed 641: current CARROT quote falls strongly by realization (`~91` to `~75` on day-27 accepts), but substituting the **actual future CARROT quote** into the CARROT2 edge still leaves every day26-27 accepted swap positive; proxy edge min/mean/median/max = `+58 / +64 / +60 / +92`.
- seed 350003: future quote is also lower (day-27 roughly `61` to `55`), but every day26-27 accepted swap remains positive; proxy edge min/mean/median/max = `+18 / +21.7 / +20 / +35`.
- seed 733: day-27 future quote falls only slightly; proxy edge min/mean/median/max = `+24 / +25.8 / +26 / +30`.

This backcheck still uses the decision-time WHEAT quote for the counterfactual WHEAT side, so it is not a full causal valuation. However, it shows that the obvious `CARROT current quote is stale/high` explanation is insufficient: even after replacing CARROT price with the observed realization-step price, the focal loss-seed late swaps remain economically positive under the same WHEAT valuation convention.

## Relation to the failed cap experiment

The prior swap-cap-24 candidate made seed 641 **-1572** versus direct parent and 350003 `-120`, with no positive block-level evidence. The new trace explains why a blanket late/quantity suppression was structurally wrong: the late swaps are not uniquely numerous, not uniquely long-horizon, and are not rendered negative merely by the observed CARROT quote decay.

## Conclusion

Close the following directions unless materially new telemetry appears:

- total CARROT2 swap cap,
- generic late-day CARROT2 disable,
- generic harvest-horizon cap,
- current-CARROT-price-only gate,
- simple CARROT quote-decay discount.

The broader late-money result remains: loss seeds exhibit uncompensated WHEAT opportunity cost at the whole-agent level, but the CARROT2 swaps themselves are not isolated as the causal defect.

A stronger independent correlation was found in the evening lead-sale (`EV`) layer: `ev_fires` is 20 / 6 / 2 / 1 on 641 / 350003 / 733 / 911. A direct-parent EV-off ablation has therefore been launched on the burned 10-seed block before changing any promotion state.
