# EXP-20260927 v153 — v152 dense self-impact reorder + empty-order guard

## Status

**FOCUSED PASS / BURNED DIRECT PASS / HARD PANEL MIXED-POSITIVE / NOT PROMOTED.** Formal champion remains v147 SHA `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`.

## Parent / scope

- champion/parent: exact v147
- tactical parent: v152 mechanism
- builder: `ci/build_v153_v147_dense_self_exposure_guard.py`
- formal engine: `kaggle_environments==1.32.7`
- focused workflow run: `36259740294`
- burned direct workflow run: `36259855401`
- hard panel workflow run: `36281727401`

v153 preserves the v152 tactical mechanism exactly and adds one bugfix only: if the first market entry is an empty order `[]`, return the parent action before evaluating `orders[0][0]`.

## v152 bug that required v153

Formal v152 focused run `36250312541` completed its game evaluation successfully against `score_2820`, seed `520104`, both seats:

- v147 final margin: `-9` in both seats
- v152 final margin: `+34` in both seats
- candidate-minus-champion money: `+20 / +20`, pair `+20`
- margin delta: `+43 / +43`
- external candidate exceptions: `0`
- v152 telemetry per seat: `eligible=3`, `changed=1`, `errors=11`

The 11 internal errors were traced to parent market actions whose first entry was `[]`; v152 indexed `orders[0][0]` before checking that first order was non-empty. Example affected steps in the source replay include 474, 569, 573, 670, 671, 677, 686, 687, 688, 689, 690. These were not the tactical reorder turn.

## v153 focused formal result

The guarded implementation reproduces the tactical gain exactly on `score_2820`, seed `520104`, both seats:

- v153 money: `148766` in both candidate seats
- v147 money: `148746` in both corresponding champion controls
- candidate-minus-champion money: `+20 / +20`, pair `+20`
- v153 margin: `+34` in both seats
- v147 margin: `-9` in both seats
- margin delta: `+43 / +43`
- seat dependence: none in this cell
- external candidate exceptions: `0`
- telemetry per seat: `eligible=3`, `changed=1`, `errors=0`

Thus the empty-order bugfix removes all observed internal errors without changing the single useful reorder or the loss-to-win conversion.

The historical v111 counterfactual run `36250732794` also completed successfully with zero errors and showed no v111 change at step649. This supports the interpretation that the v153 mechanism reaches a market-order case structurally excluded by existing v111 rather than duplicating a current champion reorder.

## Burned direct regression — seeds 681..692, both seats

Workflow `36259855401` completed successfully under the formal engine.

Pair-level `candidate_minus_champion = candidate money - champion money`:

- 12 matched pairs / 24 games
- `8W / 0L / 4D`
- mean `+37.0`
- SE `9.137`
- mean - 2SE `+18.726`
- worst pair regression `0`
- best `+97`
- seat0 mean `+32.5`
- seat1 mean `+41.5`
- candidate exceptions `0`
- champion exceptions `0`

Per-seed pair deltas:

- 681: `0`
- 682: `+67`
- 683: `0`
- 684: `+37`
- 685: `+62`
- 686: `0`
- 687: `+53`
- 688: `+97`
- 689: `+46`
- 690: `+36`
- 691: `0` pair from seat legs `-54 / +54`
- 692: `+46`

The only material seat cancellation is seed691. It does not create a pair-level regression but remains a seat-dependence item to remember in stress/sealed interpretation.

## Existing hard-opponent panel — seeds 520101..520104, both seats

Workflow `36281727401` completed successfully across 8 hard opponents, 4 seeds each, both seats: 32 matched opponent/seed pairs.

Aggregate candidate-money deltas:

- positive pairs: `7`
- negative pairs: `8`
- unchanged pairs: `17`
- aggregate mean `+1.90625`
- aggregate SE `1.49148`
- mean - 2SE `-1.07671`
- worst `-19`
- best `+23`
- candidate exceptions `0`
- champion exceptions `0`

This panel is not uniformly positive in money, so it is not by itself promotion evidence. However, outcome-level inspection is favorable:

- **one loss-to-win conversion:** `score_2820 / seed520104`, champion margin `-9` -> v153 margin `+34` in both seats;
- **zero win-to-loss conversions** anywhere in the panel;
- worst money regression is `peak_2950 / seed520104`: `-19` money and `-39` margin, but the match remains a clear win, margin `+368 -> +329` in both seats.

Opponent summaries (`candidate_minus_champion_money`):

- `peak_2950`: mean `-3.75`, worst `-19`, best `+12`; all four seeds remain wins versus the opponent.
- `salem_2900`: all zero.
- `score_2820`: mean `+5.5`, worst `-2`, best `+20`; seed520104 flips loss -> win.
- `jaxa_2802`: mean `+4.5`, worst `-2`, best `+20`.
- `thomas_router_95`: all zero.
- `tetsutani_ms`: mean `-1.25`, worst `-4`, best `+1`; all outcomes remain wins.
- `melon_squeeze`: mean `+5.75`, worst `0`, best `+23`.
- `shop_router_v7`: mean `+4.5`, worst `-2`, best `+20`.

Because peak_2950 shows repeated small regressions and a worst `-19`, do not spend a fresh sealed range yet. First diagnose the v153 activation/reorder steps on the peak regressions and contrast them with the successful score_2820/520104 cell. In particular inspect SELL ordering, any same-turn BUY_PRODUCT item, gross SELL revenue minus purchase cost, market inventory/price, and whether the reorder is changing cash only or also causing later state divergence.

## Next gate

1. telemetry/ledger on `peak_2950` seeds 520102..520104 (especially 520104) and positive control `score_2820/520104`;
2. verify no pathological wash-item net-revenue mechanism;
3. stress / broader burned panel if the causal rule remains coherent;
4. only then declare an unused sealed range;
5. runtime/preflight final before any PROMOTE.

## Decision discipline

- v152: tactically successful but implementation has an internal exception path; do not promote.
- v153: **KEEP TESTING**; direct regression is strong and hard panel creates a real loss-to-win conversion, but peak_2950 regression needs causal review before sealed.
- champion remains exact v147.
- no Kaggle submission.
- no new sealed seeds spent.
