# uploaded 127ed3 loss/win market telemetry — 2026-09-27

Decision: **ANALYSIS ONLY — use to condition the next tactical hypothesis**

## Identity / source

- Current formal champion while this analysis was performed: `uploaded_127ed3_safety_v3`
- Safety-v3 SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Comparison in the source diagnostic: safety-v3 versus former champion `v147_candidate_confirmed_v111_clone.py`
- Source Actions run: `36230151111`
- Artifact: `uploaded-127ed3-v147-diagnostic`, artifact id `10902052800`
- Contrast seeds, both candidate seats: `641, 350003, 733, 911`
- Difference convention: `candidate_minus_champion = safety-v3 - v147`

No fresh seed was consumed by this analysis.

## Question

The two diagnostic losses (641, 350003) deteriorate after roughly day 25, while 733 and 911 continue to gain. Determine whether the separator is a simple CARROT2 swap count, generic premium SELL timing, endgame residue, or a more specific realized-market compensation condition.

## Main result

A simple `more CARROT2 swaps => worse` causal story is false.

CARROT2 telemetry:

| seed | safety-v3 final delta vs v147 | safety-v3 CARROT2 swaps | v147 CARROT2 swaps |
|---|---:|---:|---:|
| 641 | -406 | 46 | 33 |
| 350003 | -520 | 29 | 27 |
| 733 | +3428 | 22 | 8 |
| 911 | +1178 | 0 | 0 |

Seed 733 has the same `+14` extra CARROT2 swaps versus v147 as seed 641, yet wins by +3428. This agrees with the already-rejected swap-cap-24 experiment: raw swap count is correlation, not a usable decision gate.

The separator in the late phase is instead whether the WHEAT opportunity cost is compensated by realized CARROT and/or premium-product revenue.

## Exact late-market decomposition

Use steps `600..719` (day 25 through end). Ledger entries are unit-level realized transactions, so SELL revenue and BUY costs are exact for recorded market transactions.

### seed 641 — loss

- cash delta at step 600: `+260`
- final delta: `-406`
- late change in relative cash: **`-666`**
- exact late ledger net difference: **`-666`**

Item contribution to safety-v3 minus v147 late market net:

| item | net difference |
|---|---:|
| WHEAT | **-1264** |
| CARROT | **+775** |
| STRAWBERRY | +291 |
| WOOL | -224 |
| MILK | -110 |
| EGG | -80 |
| FERTILIZER | -54 |
| total | **-666** |

WHEAT SELL quantity is 81 vs 114 over this window (33 fewer units). CARROT SELL quantity is 182 vs 175 (7 more), but the realized CARROT improvement is not enough to repay the WHEAT shortfall and smaller animal-product regressions.

### seed 350003 — loss

- cash delta at step 600: `-218`
- final delta: `-520`
- late change in relative cash: **`-302`**
- exact late ledger net difference: **`-302`**

| item | net difference |
|---|---:|
| WHEAT | **-513** |
| CARROT | +74 |
| EGG | +101 |
| FERTILIZER | +60 |
| STRAWBERRY | +58 |
| MILK | -69 |
| WOOL | -13 |
| total | **-302** |

WHEAT SELL quantity is 108 vs 121 (13 fewer). CARROT quantity is identical at 186 vs 186, so the crop substitution path does not create compensating CARROT volume here.

### seed 733 — strong win

- cash delta at step 600: `+463`
- final delta: `+3428`
- late change in relative cash: **`+2965`**
- recorded late market-net difference: `+2732`; the remaining `+233` is outside the recorded market ledger (e.g. non-ledger farm/labor cash effects).

| item | net difference |
|---|---:|
| WHEAT | **-1597** |
| CARROT | **+2764** |
| STRAWBERRY | +999 |
| WOOL | +301 |
| MILK | +280 |
| FERTILIZER | -15 |
| recorded market total | **+2732** |

This seed has a **larger WHEAT opportunity cost than either loss seed**, but CARROT and premium realization more than compensate it. Therefore a WHEAT-shortfall trigger alone would incorrectly suppress a major win path.

### seed 911 — win without CARROT2

- cash delta at step 600: `+529`
- final delta: `+1178`
- late change in relative cash: **`+649`**
- exact late ledger net difference: **`+649`**

| item | net difference |
|---|---:|
| WHEAT | -203 |
| CARROT | -6 |
| STRAWBERRY | **+804** |
| MILK | +36 |
| FERTILIZER | +18 |
| WOOL | 0 |
| total | **+649** |

Here premium realization, primarily STRAWBERRY, pays for the WHEAT shortfall; CARROT2 never fires.

## Late planting chronology proxy

The compact diagnostic does not contain full tile dictionaries, so exact per-turn standing plot composition cannot be reconstructed from this artifact. Successful/attempted PLANT action chronology is still informative.

Notable day-24 split:

- seed 641 safety-v3: `3 WHEAT + 10 CARROT`; v147: `8 WHEAT + 5 CARROT`
- seed 350003: both are `8 WHEAT + 5 CARROT`
- seed 733 safety-v3: `8 WHEAT + 5 CARROT`; v147: `13 WHEAT`
- seed 911: both are `9 WHEAT + 4 CARROT`

This again rejects a single fixed crop-count signature across both losses.

## Market state / demand observations

Late mean posted CARROT prices (steps 600..719, candidate-seat-0 diagnostic games):

- seed 641: `82.60`
- seed 350003: `60.52`
- seed 733: `57.53`
- seed 911: `33.52`

Thus loss 641 actually has the **highest** late CARROT quote. A rule based only on `CARROT price is low` would miss it. Realized compensation depends on quantity/harvest timing/order interaction, not just the contemporaneous quote.

Final shop mixes also do not yield a simple loss separator. Seed 641 has heavy CARROT town demand (`3 PET_CAFE + 2 FARMERS_MARKET`) yet still loses relative to v147; seed 733 has `2 PET_CAFE + 1 FARMERS_MARKET` and wins strongly.

## Endgame / generic timing checks

The earlier h24 proxy analysis already showed that large apparent premium rebound windows are not loss-specific, and diagnostics end with no meaningful residue/liquidation separator. Do not revive universal 24-turn premium holding or blanket endgame liquidation from these four seeds.

## Layer correlations worth causal testing

Safety-v3 telemetry on the same contrast games:

- DAWNPX: 641 `8 fires / 27 units`; 350003 `4 / 11`; 733 `0 / 0`; 911 `1 / 4`.
- CAPHARV: 641 `8 collect swaps / 16 saved+sold`; 350003 `9 collect + 1 care swap / 19 saved+sold`; 733 `0`; 911 `0`.

These are correlations only. Causal direct-parent ablations are required before using them as tactical gates.

The full DAWNPX-off causal diagnostic run `36284150337` later returned `1W/7L/2D`, mean `-134.7`, mean-2SE `-254.3`, worst `-594`, no exceptions; seed 641 was `-318` and 350003 `-74`. Therefore the blanket interpretation `DAWNPX activity causes the losses` is rejected.

## Conclusion / next hypothesis

The reproducible separator is **realized compensation**, not raw swap count, raw WHEAT shortfall, CARROT quote alone, shop count alone, or generic premium delay.

Any crop-mix candidate should therefore be conditional on a forward realization proxy that combines at least some of:

1. expected WHEAT units sacrificed,
2. predicted CARROT harvest before the relevant consumption/sell horizon,
3. market inventory / quote and planned SELL order timing,
4. premium-product revenue pipeline that can compensate the WHEAT opportunity cost,
5. late-game liquidity horizon.

Before implementing such a multi-signal gate, finish the smaller direct-parent causal screens already queued (DAWNPX hour-0-only and CAPHARV-off). Keep tactical changes to one layer/condition at a time.
