# EXP-20260926 uploaded dbc709 candidate — evaluation

Status: **REJECT full candidate / do not advance to fresh sealed**

## Identity

- uploaded filename: `main(1).py`
- byte size: `841471`
- SHA256: `dbc709febaef6b7b3f77ce8ee7dd2466548be0bd52763aa89905f61940f153b7`
- prior expected upload SHA: `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- identity decision: SHA mismatch, therefore a new candidate
- current formal champion: `v147_candidate_confirmed_v111_clone.py`
- champion SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- formal engine target: `kaggle_environments==1.32.7`
- metric: `candidate_minus_champion = candidate - champion`

## Static / preflight

- `python -m py_compile`: PASS
- stdlib load: PASS
- final callable: `agent(observation, configuration)`
- no requests/urllib/socket/subprocess/http imports found
- final policy is a long wrapper chain; base `_SETTINGS` alone does not describe the active behavior
- notable active layers include RACE/RACEPX/RACEGATE, CARROT2, ORDERPRI2, CAPHARV, SHEDROOM, HERD2 and COWSWAP
- completely empty observation raises `KeyError('player')`; normal `step/player` malformed probes fall back to PASS in the tested path

## Evaluator calibration

A local stdlib Kaggriculture evaluator was available in the sandbox. Before using it for this candidate, it was calibrated against the already-known formal v147-v115 result on burned seeds 681..692, both seats.

Expected formal pair deltas:

`[4, 170, 0, 2, 38, 23, 0, 58, 230, 0, 2, 43]`

The local evaluator reproduced **all 12/12 pair deltas exactly**, including seed 691 legs `-52/+56 -> pair +2`. Therefore it is accepted for burned-development screening in this experiment, but it is not used to declare a fresh sealed promotion.

## Full candidate vs formal v147 — burned dev screen

Seeds 681..692, both seats, 12 matched pairs.

- wins: **1**
- losses: **11**
- ties: **0**
- mean candidate-minus-champion: **-859.7083**
- SE: **350.8493**
- mean - 2SE: **-1561.4070**
- worst regression: **-2784**
- best: **+1528.5**
- exceptions: **0**

| seed | pair diff | legs |
|---:|---:|---|
| 681 | -1963 | -1963 / -1963 |
| 682 | +1528.5 | +3656 / -599 |
| 683 | -717 | -717 / -717 |
| 684 | -527 | -527 / -527 |
| 685 | -89 | -89 / -89 |
| 686 | -2686 | -2671 / -2701 |
| 687 | -2784 | -2784 / -2784 |
| 688 | -1311 | -1311 / -1311 |
| 689 | -973 | -973 / -973 |
| 690 | -87 | -87 / -87 |
| 691 | -8 | -35 / +19 |
| 692 | -700 | -700 / -700 |

This fails the development gate decisively. Fresh sealed seeds 721..732 remain burned from v147 and were not reused; no new sealed range was consumed.

## Telemetry / mechanism findings

Representative candidate telemetry:

- seed 682: CARROT2 fired heavily (`ca_swaps` 22/26 by seat), ORDERPRI2 reordered 45/42 turns and made 3/2 slot swaps, SHEDROOM sold 63/45 extra units, OVERFLOW fired; COWSWAP was blocked by the shop rule. Despite the positive pair mean, the two legs were +3656 and -599, so this is strongly seat-dependent.
- seed 686: CARROT2 did not fire; ORDERPRI2 still reordered 29/26 turns and SHEDROOM fired. Final pair was -2686.
- seed 687: CARROT2 fired 17 swaps, CAPHARV saved/sold 8 units, ORDERPRI2 reordered 20 turns, SHEDROOM fired, HERD2 evaluated alternatives but kept the inherited choice. Final pair was -2784 in both seats.

The candidate differs from v147 from step 0: candidate opening is `BUY_PRODUCT WHEAT 20 / SELL WHEAT 15` in the observed final action path versus v147 `BUY_PRODUCT WHEAT 7 / SELL WHEAT 2` in the calibrated game. Therefore late-layer telemetry alone cannot attribute the full money delta.

## Candidate-inspired isolated transplants onto v147

All below use the same burned screen seeds 681, 682, 686 with both seats. Each is a small v147-based candidate.

- opening constant `13,30,30` replacing v147 `5,10,60`: mean **-3350**, worst -3355 -> **REJECT**
- ORDERPRI2 slot margin `8 -> 50`: mean **-158.33**, worst -458 -> **REJECT**
- SHEDROOM `margin 8 -> 4`, hours `(21,22,23) -> (22,23)`: mean **-185**, worst -425 -> **REJECT**
- fertilizer first day `14 -> 16`: mean **-28.67**, worst -46 -> **REJECT**
- V92-P `(EVERY,K,TOP) = (1,1,3) -> (3,4,1)`: mean **-285.33**, worst -712 -> **REJECT**
- R36 native-lead start `216 -> 288`: 0 / 0 / 0 -> no evidence of benefit
- R37 window start `216 -> 192`: 0 / 0 / 0 -> no evidence of benefit
- CARROT feed reserve `1 -> 2`: seed681 0, seed682 -99 before the long process was recycled; no positive evidence, do not advance

A full-candidate ablation that restored only the v147 opening was also tested. It catastrophically broke the candidate's coupled route assumptions (four tested pairs between -71k and -154k), so the candidate opening cannot be removed in isolation inside the full candidate. This does **not** rescue the opening transplant: the direct v147-based isolated opening test above is strongly negative.

## Candidate-only mechanisms not promoted

- `PREDICT2/V92-Q` depends on an external `V92_SELL_LIB` environment path. Without that external library the stream set is empty and the layer is inert, so it is not a self-contained submission improvement.
- `CTRTABLE` is fingerprint-specific to two recorded rival patterns and is an overfit-risk mechanism, not a general v147 improvement candidate.
- `OVERFLOW` is an older public V43/R148-style overflow idea; formal v147 already contains later overflow/storage safety machinery. No evidence here justifies replacing the v147 implementation.

## Provenance/license

The source contains extensive Apache-2.0/public-lineage attribution, but the standalone uploaded `main.py` references external `LICENSE.txt` / NOTICE-equivalent material rather than carrying the complete package. This would require packaging audit before submission. Since the candidate fails the performance gate, no submission packaging is prepared.

## Decision

**REJECT `dbc709f...` as a full candidate.**

Reasons:

1. 11/12 burned matched pairs regress versus formal v147.
2. mean is strongly negative and worst regression is -2784.
3. the sole winning seed is highly seat-dependent.
4. no candidate-inspired small transplant tested so far improves v147.
5. no exception was observed, so the rejection is strategic/performance-based rather than a runtime crash issue.

No fresh sealed seeds, known-opponent regression budget, or formal submission slot should be spent on this full candidate.

## Next hypothesis

Keep v147 unchanged. Continue improvement from v147 with small isolated changes only. Candidate-derived parameter changes tested above are now burned/rejected and should not be repeated. The next useful search should target mechanisms not already dominated by v147's current R124/R127/R128/R148/R149/e343/v111 safety/order stack, with preference for changes that alter ties or low-margin losses without touching the opening contract.
