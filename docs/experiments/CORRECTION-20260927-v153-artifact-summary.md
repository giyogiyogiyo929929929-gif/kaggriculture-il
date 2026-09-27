# CORRECTION — v153 retained artifact summary

This note corrects historical v153 summary text using the retained artifact from self-hosted run `36256798350` (`v153-v147-burned-hard-gate`, artifact id `10912016767`). It does not change any champion decision. v153 remains historical hypothesis support only because it was built on v147, not the current formal v151.

## Burned direct v153 vs v147, seeds 681..692

Retained `burned_gate_summary.json` records:

- 8W / 0L / 4T
- mean candidate_minus_champion: +37.0
- worst: 0
- best: +97 (not +150)
- exceptions: 0

Per-seed values:

`681 0, 682 +67, 683 0, 684 +37, 685 +62, 686 0, 687 +53, 688 +97, 689 +46, 690 +36, 691 0, 692 +46`.

Seed 691 has seat legs `-54/+54`, giving matched pair 0; this is another reminder not to treat a raw seat leg as a pair regression.

## Hard panel v153 vs v147

Retained `v153_hard_gate_summary.json` records:

- 64 games
- transitions: W->W 62, L->W 2
- outcome regressions: 0
- outcome improvements: 2
- both improvements: `score_2820`, seed 520104, both seats, champion margin -9 -> candidate margin +34, candidate-minus-champion cash +20
- aggregate seed/opponent-pair candidate-minus-champion cash mean: +1.90625
- worst seed/opponent-pair cash delta: -19
- exceptions: 0

The retained individual hard files show negative final-cash deltas without outcome regression, including:

- `peak_2950`: seed-level deltas `[+12, -2, -6, -19]`, mean -3.75; the -19 cell is seed 520104, where candidate still wins with margin +329 vs champion margin +368;
- `tetsutani_ms`: `[-2, +1, 0, -4]`;
- `score_2820`: `[-2, +4, 0, +20]`;
- `jaxa_2802`: `[-2, 0, 0, +20]`;
- `shop_router_v7`: `[-2, 0, 0, +20]`;
- `melon_squeeze`: `[0, 0, 0, +23]`;
- `salem_2900` and `thomas_router_95`: all zero.

Therefore earlier prose claiming hard-panel cash worst 0 / seven opponents exactly zero is not supported by the retained artifact. The outcome-transition claim (62 W->W, 2 L->W, zero outcome regressions) is supported.

## Implication for v154

Do not copy the inaccurate historical cash claim into v154. Evaluate exact v154-v151 artifacts directly. Because Kaggriculture is decided by win/loss at final cash, outcome transitions remain the primary sampled-game metric, while negative cash deltas inside preserved wins must still be recorded as worst-regression evidence and investigated before PROMOTE. Fresh sealed and diversity/regression panels are required to determine whether that risk generalizes.
