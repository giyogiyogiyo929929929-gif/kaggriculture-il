# EXP-20260927 — v156 exact-v151 not-ahead + three-exposure guard

## Status

STRICT BURNED/HARD PASS / PREFLIGHT+TELEMETRY NEXT. Formal champion remains `v151_none_observation_guard`.

No fresh sealed seeds consumed. No Kaggle submission.

## Parent / identity

- formal champion / source parent: exact `v151_none_observation_guard`
- v151 SHA256: `54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31`
- v156 SHA256: `14f142f9ca933a208150895e60fa3ee5838d6230782e7fa7807707280b26bcdb`
- v156 branch: `eval-v156-v151-not-ahead-three-exposure-20260927`
- v156 is reconstructed directly from exact v151; it does not use generated v155 or v154 source as its input.
- environment: Python 3.11, `kaggle-environments==1.32.7`.

## Hypothesis

The v154 dense leading-SELL reorder has a reproducible loss-to-win cell against `score_2820 / 520104`, but also small cash regressions in preserved wins. The v155 `do not reorder while already ahead in cash` guard removed the historical `peak_2950` regressions but retained `tetsutani_ms / 520104 = -4` on exact v151.

Consumed-cell diagnostics showed a structural distinction:

- positive `score_2820 / 520104`, step 649: exposures include `57, 35, 14, 0, 0` — three SELL items >=10;
- negative `tetsutani_ms / 520104`, step 649: `57, 35, 4, 0, 0` — only two items >=10;
- other low-density tetsutani changed states similarly have fewer than three material exposures.

The tactic is therefore gated to genuine multi-item market-race states.

## Changes

Relative to v155 conditions, one additional general guard:

`count(self_exposure >= 10.0) >= 3`

inside the leading distinct SELL block before reordering.

The threshold `10.0` and count `3` were preregistered from already-consumed diagnostics before any v156 evaluation. Do not tune them after v156 outcomes.

No opponent name, seed, seat, or hard-cell identifier is used.

## Exact-v151 focused qualification

Run `36301900628`: SUCCESS. Artifact `v156-v151-focused`.

Static / identity:

- exact v151 SHA matched `54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31`;
- v156 SHA `14f142f9ca933a208150895e60fa3ee5838d6230782e7fa7807707280b26bcdb`;
- py_compile PASS;
- `observation=None` preserved v151 PASS action.

Focused consumed cells, both seats:

- `score_2820 / 520104`: candidate_minus_champion `+20 / +20`; mean/worst `+20`; margin improvement `+43`; champion margin `-9` -> candidate `+34`;
- `peak_2950 / 520101..520104`: all four matched seed deltas `0`; worst `0`;
- `tetsutani_ms / 520101..520104`: all four matched seed deltas `0`; worst `0`;
- candidate/champion exceptions: 0.

This fixes the exact-v151 v155 `tetsutani_ms / 520104 = -4` regression while retaining the intended score_2820 loss-to-win cell.

## Strict burned / hard qualification

Run `36302471481`: SUCCESS. Artifact `v156-v151-strict-burned-hard`.

Burned direct seeds `681..692`, both seats:

- matched pairs: `8W / 0L / 4T`;
- mean candidate_minus_champion: `+28.1667`;
- worst: `0`;
- best: `+94`;
- exceptions: `0`;
- seed 691 had opposite raw seat deltas `-54 / +54`, giving matched-pair delta `0`; seat swap therefore cancels the seat effect as intended.

Hard 8 opponents x seeds `520101..520104`, both seats:

- outcome transitions: `W->W 62`, `L->W 2`;
- outcome regressions: `0`;
- outcome improvements: `2`;
- mean candidate_minus_champion: `+1.875`;
- worst: `0`;
- best: `+20`;
- exceptions: `0`.

Per-opponent matched cash delta:

- `jaxa_2802`: mean `+5`, worst `0`, best `+20`;
- `melon_squeeze`: all `0`;
- `peak_2950`: all `0`;
- `salem_2900`: all `0`;
- `score_2820`: mean `+5`, worst `0`, best `+20`;
- `shop_router_v7`: mean `+5`, worst `0`, best `+20`;
- `tetsutani_ms`: all `0`;
- `thomas_router_95`: all `0`.

Both improvements are `score_2820 / 520104`, both seats: champion margin `-9` -> candidate margin `+34`, candidate_minus_champion cash `+20`.

This is the key difference from v154: the intended loss-to-win cell remains, while the hard-panel cash worst improves from `-19` to `0` under the unchanged strict gate.

## Evaluation order / gates

Completed:

1. exact v151 reconstruction + SHA assertion — PASS;
2. py_compile / `None` safety — PASS;
3. focused consumed cells — PASS;
4. focused strict gate — PASS;
5. burned 681..692 with seat swap, matched worst >=0, exceptions0 — PASS;
6. full hard 8-opponent panel with seat swap, zero outcome regressions, at least one improvement, cash worst >=0, exceptions0 — PASS.

Next:

7. internal telemetry / malformed preflight — run `36305115867` queued at time of this update;
8. preregistered repeated-control runtime characterization, followed later by a strict final runtime gate;
9. only after pre-sealed gates qualify, reserve a new SHA-derived fresh sealed block for v156. Do not reuse v154's reserved `894322..894333` as v156 fresh evidence;
10. sealed, important-opponent/climb-band regression, final package/preflight, then PROMOTE/REJECT.

Prepared but not yet counted as evidence:

- `.github/workflows/v156-v151-preflight-telemetry.yml`
- `.github/workflows/v156-v151-runtime-characterization.yml`

## Decision

KEEP TESTING. v156 has now passed focused and strict consumed-seed burned/hard gates with zero hard cash regression and two reproducible loss-to-win outcomes. Formal champion remains v151 until preflight, runtime, fresh sealed and final regression gates pass.
