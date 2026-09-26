# EXP-20260927 v153 — v152 dense self-impact reorder + empty-order guard

## Status

**FOCUSED PASS / DIRECT BURNED REGRESSION QUEUED / NOT PROMOTED.** Formal champion remains v147 SHA `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`.

## Parent / scope

- champion/parent: exact v147
- tactical parent: v152 mechanism
- builder: `ci/build_v153_v147_dense_self_exposure_guard.py`
- formal engine: `kaggle_environments==1.32.7`
- focused workflow run: `36259740294`
- burned direct workflow run: `36259855401`

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

## Next gate

Burned direct regression workflow `36259855401` evaluates v153 directly against exact v147 on seeds `681..692`, both seats, using `candidate_minus_champion = candidate - champion`. These are already-burned development seeds; no sealed information is consumed.

Acceptance before hard-panel expansion:

- no candidate exceptions;
- no material worst regression;
- no systematic seat bias;
- any changed seed is inspected before proceeding;
- if neutral on direct clone-like play, retain the hard-cell win as opponent-specific evidence but do not infer general improvement from that alone.

If the direct gate is acceptable, next steps are hard-opponent cells 520101..520104, activation/wash-item net-revenue telemetry, then stress. Only after those gates may an unused sealed range be declared.

## Decision discipline

- v152: tactically successful but implementation has an internal exception path; do not promote.
- v153: KEEP TESTING.
- champion remains exact v147.
- no Kaggle submission.
- no new sealed seeds spent.
