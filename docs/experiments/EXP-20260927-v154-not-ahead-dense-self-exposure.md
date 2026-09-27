# EXP-20260927 v154 — not-ahead gate for dense self-impact SELL reorder

## Status

**FOCUSED PASS / BURNED DIRECT PASS / FULL HARD PANEL PASS-WITH-TINY-REGRESSION / BURNED STRESS PASS / SEALED PASS / TELEMETRY PENDING / NOT PROMOTED.** Formal champion remains exact v147 SHA `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`.

## Parent / hypothesis

- parent/champion: exact v147
- tactical parent: v153 dense self-impact SELL reorder
- builder: `ci/build_v154_v147_dense_self_exposure_not_ahead.py`
- formal engine: `kaggle_environments==1.32.7`
- single major delta vs v153: only permit the dense reorder when current own money is not ahead of rival money.

Hypothesis: v153's self-impact ordering is useful when trying to recover a tied/losing market race, but creates unnecessary downside when already ahead because it ignores which product the opponent is racing first.

## Causal basis from v153 diagnostic

Formal diagnostic run `36290900542` succeeded. At step649 the same v153 reorder was beneficial against `score_2820` but harmful against `peak_2950` and slightly harmful against `tetsutani_ms`.

- score_2820/520104: candidate was about 178 behind at the activation; v153 `+20` money and loss -> win.
- peak_2950/520104: candidate was already about 141 ahead; v153 `-19` money while still winning.
- tetsutani_ms/520104: candidate was about 46 behind; v153 `-4` money while still winning.

The opponent SELL ordering differs across these cases, while v153's own reordered leading SELL block is the same. Therefore self-impact alone does not determine the best race target.

## Formal focused/direct result

Workflow run `36294926392` completed successfully.

Focused cells:

- `score_2820 / 520104`: v154-v147 `+20` both seats; champion margin `-9`, v154 margin `+34`; loss -> win preserved.
- `peak_2950 / 520101..520104`: all four pairs exactly `0`; the v153 worst `-19` regression is eliminated.
- `tetsutani_ms / 520104`: `-4` both seats; margin remains a clear win (`+240 -> +236`).
- candidate exceptions `0`.

Burned direct seeds `681..692`, both seats:

- 12 pairs / 24 games
- `8W / 0L / 4D`
- mean `+28.1667`
- SE `8.973`
- mean - 2SE `+10.22`
- worst pair `0`
- best `+94`
- seat0 mean `+23.67`
- seat1 mean `+32.67`
- candidate exceptions `0`
- champion exceptions `0`

Compared with v153, the direct mean is lower, but pair-level worst remains zero while the known peak regression is removed.

## Full hard-opponent panel

Workflow run `36300134144` completed successfully across 8 hard opponents, seeds `520101..520104`, both seats: 32 matched opponent/seed pairs.

Aggregate `candidate_minus_champion_money`:

- `3W / 1L / 28D`
- mean `+1.75`
- SE `1.06161`
- mean - 2SE `-0.37322`
- worst `-4`
- best `+20`
- candidate exceptions `0`
- champion exceptions `0`

Nonzero cells only:

- `score_2820 / 520104`: `+20` money, `+43` margin delta; loss -> win.
- `jaxa_2802 / 520104`: `+20` money, `+43` margin delta; win remains win.
- `shop_router_v7 / 520104`: `+20` money, `+43` margin delta; win remains win.
- `tetsutani_ms / 520104`: `-4` money, `-4` margin delta; win remains win (`+240 -> +236`).

All `peak_2950`, `salem_2900`, `thomas_router_95`, and `melon_squeeze` cells are exactly unchanged. There are zero win -> loss conversions and one loss -> win conversion.

The residual tetsutani regression is causally localized to step649. At activation v154 is 46 behind, so the not-ahead gate allows the reorder; the opponent delays FERTILIZER relative to v154, making FERTILIZER-first slightly suboptimal. The effect is only `-4`, symmetric across seats, with no outcome regression.

## Burned development stress — seeds 641..672

Workflow run `36301876016` completed successfully under the formal engine. These are development/burned seeds, not sealed.

- 32 matched pairs / 64 games
- `21W / 2L / 9D`
- mean `+21.6719`
- SE `5.1262`
- mean - 2SE `+11.4195`
- worst pair `-13`
- best `+86`
- seat0 mean `+26.78`
- seat1 mean `+16.56`
- candidate exceptions `0`
- champion exceptions `0`

Negative pairs were seed658 `-13` and seed671 `-1`. Some seat dependence exists (notably 655, 663, 669), but aggregate paired evidence remains strongly positive.

## Predeclared sealed test — seeds 1801..1812

Seeds `1801..1812` were declared as a fresh unused sealed range before the workflow was created. Workflow run `36305174326` completed successfully under the exact formal engine. These seeds are now burned and must not be reused as sealed.

- 12 matched pairs / 24 games
- `7W / 0L / 5D`
- mean `+18.9167`
- SE `6.3407`
- mean - 2SE `+6.2354`
- worst pair `0`
- best `+55`
- seat0 mean `+14.6667`
- seat1 mean `+23.1667`
- candidate exceptions `0`
- champion exceptions `0`

Per-seed pair deltas:

- 1801 `0`
- 1802 `+27` from seat legs `-24 / +78`
- 1803 `0`
- 1804 `+12 / +12`
- 1805 `0`
- 1806 `+43 / +43`
- 1807 `+49 / +49`
- 1808 `+38 / +38`
- 1809 `+55 / +55`
- 1810 `+3 / +3`
- 1811 `0`
- 1812 `0`

The sealed result passes the primary matched-pair gate: positive mean, positive mean-minus-2SE, zero pair-level regression, zero exceptions, and improvement spread across multiple seeds. The only notable seat-specific anomaly is seed1802 (`-24 / +78`), so telemetry/replay is required before promotion.

## Current telemetry gate

A dedicated sealed direct diagnostic was added to compare each v154 action with a shadow v147 action on the same observation and record v154 report deltas plus money/market/shed state around every changed step. Diagnostic targets:

- seed1802 both seats — seat-asymmetric primary case;
- seed1806 both seats — symmetric positive control;
- seed1809 both seats — strongest symmetric positive control;
- seed1810 both seats — small positive control.

After telemetry, remaining promotion gates are dedicated runtime, submission preflight, and final important-opponent regression confirmation as needed.

## Decision

- v153: superseded by v154 for safety; do not promote v153.
- v154: **KEEP TESTING / SEALED PASS / current leading candidate**.
- champion remains exact v147 until telemetry/runtime/preflight gates pass.
- sealed seeds 1801..1812 are burned.
- no Kaggle submission.
