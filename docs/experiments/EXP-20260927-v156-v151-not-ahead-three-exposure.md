# EXP-20260927 — v156 exact-v151 not-ahead + three-exposure guard

## Status

RUNTIME CHARACTERIZATION PASS / FRESH SEALED RESERVED AND QUEUED. Formal champion remains `v151_none_observation_guard`.

Fresh sealed block `855641..855652` was preregistered before first execution in `SEALED-RESERVATION-20260927-v156.md`. Sealed run `36310398164` was queued at the time of this update. No Kaggle submission.

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
- seed 691 had opposite raw seat deltas `-54 / +54`, giving matched-pair delta `0`; seat swap cancels the seat effect as intended.

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

Both outcome improvements are `score_2820 / 520104`, both seats: champion margin `-9` -> candidate margin `+34`, candidate_minus_champion cash `+20`.

This is the key difference from v154: the intended loss-to-win cell remains, while the hard-panel cash worst improves from `-19` to `0` under the unchanged strict gate.

## Preflight / internal telemetry

Run `36305115867`: SUCCESS. Artifact `v156-v151-preflight-telemetry`.

Preflight:

- last callable `agent` — PASS;
- standard-library / own-module imports only — PASS;
- Kaggle-compatible loader — PASS;
- action shape — PASS;
- five malformed-observation fallback patterns — PASS.

Internal telemetry over the consumed burned + hard panels:

- games: `88`;
- eligible: `36`;
- changed: `22`;
- ahead_skips: `10787`;
- exposure_skips: `12`;
- errors: `0`.

This confirms that both guards actively filter reorder opportunities rather than making the candidate inert, while retaining zero internal exceptions.

## Runtime characterization

Run `36308693426`: SUCCESS. Artifact `v156-v151-runtime-characterization`. PR #13 was closed without merge after artifact collection.

Preregistered method: three repetitions with alternating execution order (`v151->v156`, `v156->v151`, `v151->v156`), GC enabled, consumed `score_2820 / 520101..520104` with seat swap.

Wall-clock results:

- rep 1: v151 p99 `15.5777 ms`, max `280.1249 ms`, >200ms `3`; v156 p99 `13.9443 ms`, max `194.2144 ms`, >200ms `0`;
- rep 2: v156 p99 `13.6061 ms`, max `206.0014 ms`, >200ms `2`; v151 p99 `15.0018 ms`, max `344.5302 ms`, >200ms `3`;
- rep 3: v151 p99 `17.6337 ms`, max `307.7933 ms`, >200ms `3`; v156 p99 `16.1809 ms`, max `221.6913 ms`, >200ms `2`.

- errors: `0` for both agents in all repetitions;
- v156 p99 `<50 ms` in all 3 repetitions — characterization gate PASS;
- v156 raw max `<200 ms` in `1/3` repetitions;
- v151 control raw max `<200 ms` in `0/3` repetitions.

Interpretation: the >200ms tail is present more strongly in the v151 control, so this characterization does not support a v156-specific tail regression. It does **not** waive the formal promotion requirement. A separate strict final runtime gate with unchanged thresholds `p99 <50 ms` and `max <200 ms` remains required before PROMOTE.

Prepared workflow: `.github/workflows/v156-v151-final-runtime.yml`.

## Fresh sealed reservation

Reservation committed before first execution:

- document: `docs/experiments/SEALED-RESERVATION-20260927-v156.md`;
- deterministic rule: `start = 700000 + int(candidate_sha256[:8],16) % 200000`;
- start: `855641`;
- reserved fresh block: `855641..855652`, 12 matched seeds, both seats;
- exact start-seed repository code search returned zero matches as supporting collision evidence;
- v154 reserved block `894322..894333` is not reused.

Sealed workflow: `.github/workflows/v156-v151-sealed-855641-855652.yml`.

First sealed run: `36310398164`, PR #14. Strict preregistered qualification requires 12 pairs, zero exceptions, zero matched losses, worst `>=0`, at least one win, and `mean - 2*SE > 0`. A telemetry replay occurs only after the first sealed evaluation has consumed the block.

## Evaluation order / gates

Completed:

1. exact v151 reconstruction + SHA assertion — PASS;
2. py_compile / `None` safety — PASS;
3. focused consumed cells — PASS;
4. focused strict gate — PASS;
5. burned 681..692 with seat swap — PASS;
6. full hard 8-opponent panel with seat swap — PASS;
7. internal telemetry / malformed preflight — PASS;
8. repeated-control runtime characterization — PASS its preregistered p99/error gate; formal max gate still pending.

Current / next:

9. fresh sealed `855641..855652` — run `36310398164` queued at time of update;
10. if sealed passes, run consumed public diversity plus strength/climb-band regression with matched seeds and seat swap;
11. strict final runtime with unchanged `p99 <50 ms`, `max <200 ms`;
12. final package/preflight and PROMOTE / KEEP TESTING / REJECT decision.

## Decision

KEEP TESTING. v156 has clean focused, strict burned/hard, preflight/internal telemetry, and repeated runtime characterization evidence. Formal champion remains v151 until fresh sealed, broader regression, strict final runtime, and final package gates pass.
