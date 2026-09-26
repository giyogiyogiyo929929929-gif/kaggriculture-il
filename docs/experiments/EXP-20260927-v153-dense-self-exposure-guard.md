# EXP-20260927 v153 — v152 dense self-impact reorder + empty-order guard

## Status

**FOCUSED TEST RUNNING / NOT PROMOTED.** Formal champion remains v147 SHA `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`.

## Parent / scope

- champion/parent: exact v147
- tactical parent: v152 mechanism
- builder: `ci/build_v153_v147_dense_self_exposure_guard.py`
- formal engine: `kaggle_environments==1.32.7`
- focused workflow run: `36259740294`

v153 preserves the v152 tactical mechanism exactly and adds one bugfix only: if the first market entry is an empty order `[]`, return the parent action before evaluating `orders[0][0]`.

## Why the bugfix is separated

Formal v152 focused run `36250312541` completed its game evaluation successfully against `score_2820`, seed `520104`, both seats:

- v147: final margin `-9` in both seats
- v152: final margin `+34` in both seats
- candidate-minus-champion money: `+20 / +20`, pair `+20`
- margin delta: `+43 / +43`
- external candidate exceptions: `0`
- v152 telemetry per seat: `eligible=3`, `changed=1`, `errors=11`

The 11 internal errors were traced to parent market actions whose first entry was `[]`; v152 indexed `orders[0][0]` before checking that first order was non-empty. Example affected steps in the source replay include 474, 569, 573, 670, 671, 677, 686, 687, 688, 689, 690. These turns were not the tactical reorder turn.

The useful change remained one valid reorder per game. The bugfix therefore does not alter the economic hypothesis and should preserve the focused gain while reducing internal errors to zero.

## Required focused acceptance

Before any broader regression:

1. exact v147 SHA assertion passes;
2. syntax passes;
3. same score_2820 / 520104 both seats;
4. candidate-minus-champion remains `+20/+20` (or at least preserves the loss-to-win conversion in both seats);
5. `_V153_REPORT.errors == 0` in both seats;
6. `_V153_REPORT.changed == 1` in both seats;
7. external exceptions == 0.

If all pass, next gate is burned direct seeds 681..692, both seats. No sealed seeds are to be spent before direct regression and hard-panel checks.

## Decision discipline

- v152: tactically promising but implementation has internal exception path; do not promote.
- v153: KEEP TESTING.
- champion remains v147.
- no Kaggle submission.
- no new sealed seeds spent.
