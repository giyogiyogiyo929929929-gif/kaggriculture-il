# KAGGRICULTURE_CHAT_MODE_v151_r1.md

## 1. Canonical state

- **Formal Champion: `v151_none_observation_guard`**
- Champion SHA256: `54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31`
- Promoted: 2026-09-27 JST
- Promotion record: `docs/experiments/PROMOTE-20260927-v151.md`
- Former champion: `v115_champion_same_turn_open_squeeze`
- v115 SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`

This file supersedes `KAGGRICULTURE_CHAT_MODE_v115_r9.md` and all older chat-mode files for champion selection.

Never infer champion from version numbers or filenames alone. Until another explicit PROMOTE record supersedes this one, all new promotion candidates must be evaluated against exact v151.

Do not edit the v151 lineage in-place. Build each improvement as a separate candidate.

## 2. Champion lineage

`v115 -> v147 -> v150 -> v151`

### v147: strategic change

`v147_confirmed_v111_clone`
SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`

Adds a guarded second `_v111_reorder` after clone-like behavior is confirmed.

Focused telemetry established only the following safe mechanism claim:

- tested divergences preserve the SELL multiset;
- SELL sequence/order changes;
- gains can arise from market order processing and later state cascades.

Do not invent or infer an exact internal `_v111_reorder` priority rule beyond observed replay evidence.

### v150: runtime optimization

`v150_skip_noop_second_pass`
SHA256: `0a5bfa1b9fa91dd7ebdee1f45640719b23a7b895cbd85cc1f4f17bddebb6387d`

One change only: require `parent_changed` before the confirmed second `_v111_reorder` pass.

This removes redundant searches without changing tested actions/rewards.

### v151: safety completion

`v151_none_observation_guard`
SHA256: `54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31`

One change only: for `observation is None`, return a valid PASS action; otherwise delegate directly to v150.

## 3. Promotion evidence

### Burned direct panel

v147 vs v115, seeds 681..692, same-seed seat swap:

- 9W / 0L / 3T
- mean +47.5
- worst 0
- best +230
- exceptions 0

v150 == v147 actions/rewards on all 24 burned games, run `36249173738`.

v151 == v150 actions/rewards on all 24 burned games, run `36259834091`.

### Sealed holdout

v147 vs v115, seeds 1701..1712, seat swapped:

- 10W / 0L / 2T
- mean +36.6667
- SE 11.5025
- mean - 2SE +13.6616
- worst 0
- best +112
- exceptions 0

v150 == v147 on all 24 sealed games, run `36252365551`.

v151 == v150 on all 24 sealed games, run `36259834091`.

### Hard-opponent regression

v150 vs v115, run `36256381428`:

- 32 matched pairs
- 0W / 0L / 32T
- mean/worst/best 0
- exceptions 0
- regression_free true

### Public diversity regression

v150 vs v115, run `36257645079`:

- 28 matched pairs
- 0W / 0L / 28T
- mean/worst/best 0
- exceptions 0
- 56/56 absolute wins vs tested opponents
- regression_free true

### v151 equivalence and safety

Run `36259834091`:

- burned + sealed total 48 games
- v150/v151 action traces identical 48/48
- rewards identical 48/48
- mismatches 0
- errors 0
- five malformed observations PASS, including `None`
- Kaggle-compatible loader PASS
- stdlib/local import audit PASS
- 720-turn completion PASS

### Formal runtime

Run `36259995740`, GC enabled, sequential single-process, seeds 681/682/689/691/692 with seat swap:

- calls 7,190
- median 4.167 ms
- p95 9.1638 ms
- p99 16.8518 ms
- max 162.0771 ms
- CPU max 171.875 ms
- >200 ms 0
- errors 0
- formal PASS

Formal runtime contract remains:

- p99 < 50 ms
- max < 200 ms

## 4. Packaging identity

Qualified package from run `36259834091`:

- source/main SHA256: `54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31`
- archive SHA256: `4220541594344fab249835fa8e453494709eff4b4f3895d764bb9596687a5ad0`
- archive bytes: 621,369
- members: exactly `main.py`
- packed bytes equal qualified source: yes

The qualification package was **not submitted to Kaggle**.

## 5. Evaluation contract going forward

Formal engine: `kaggle_environments==1.32.7`.

Normalize comparisons as:

`candidate_minus_champion = candidate - champion`

Formal champion is now exact v151, not v115.

Preferred order:

1. static / syntax
2. focused synthetic test
3. runtime / preflight
4. same-seed v151 vs candidate
5. seat swap
6. matched-pair aggregate
7. replay/telemetry on differing seeds
8. stress
9. unused sealed seeds
10. important-opponent regression
11. final runtime
12. PROMOTE / KEEP TESTING / REJECT

Do not promote from averages alone. Check worst regression, seat/seed dependence, exceptions/timeouts, sealed reproduction, known-opponent safety, runtime, and mechanism.

## 6. Closed/rejected findings to retain

- v148 duplicate-SELL guard: REJECT; weakened v147 and was motivated by an invalid seat-risk interpretation.
- v149 late guard: REJECT; weakened v147.
- duplicate-factor cache optimization: REJECT; only 72 duplicates among 436,786 evaluated candidates (~0.0165%), with no useful concentration on heavy 20,160-candidate turns.
- v150 direct package promotion: blocked by `observation=None`; superseded by v151 rather than edited in place.
- broad V92/K threshold families from v139/v140-era work remain low priority unless new activation telemetry justifies reopening them.

## 7. Current priority after promotion

First treat v151 as a frozen baseline and avoid mixing a new strategic change with champion cleanup.

Next candidate should be based on fresh loss/replay telemetry against meaningful current opponent families. Existing evidence suggests sale timing/order remains a productive axis, but do not implement a broad rule without a repeatable activation pattern.

A candidate must remain small (1-3 major changes) and should target conversion of close losses/ties rather than increasing already-large winning margins.

## 8. Submission status

PROMOTE is an internal evaluation decision only.

- v151 is **not automatically submitted**.
- Before a formal Kaggle submission, verify remaining submission slots, regenerate/check exact package bytes, rerun packaged preflight if the artifact has changed, and record SOURCE/license identity.
- Do not perform mass submissions or leaderboard probing.

## 9. Current decision

```text
FORMAL CHAMPION:
v151_none_observation_guard
SHA256:
54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31

STATUS:
PROMOTED 2026-09-27 JST

KAGGLE SUBMISSION:
NOT PERFORMED
```
