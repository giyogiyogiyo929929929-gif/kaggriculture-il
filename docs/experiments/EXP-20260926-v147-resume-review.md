# EXP-20260926 v147 resume review

Date: 2026-09-26

## Canonical state

- Formal champion: `v115_champion_same_turn_open_squeeze.py`
- Champion SHA-256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- Canonical source: `KAGGRICULTURE_CHAT_MODE_v115_r7.md`; it explicitly says not to substitute v119/v121 and that only a fully gated PROMOTE changes champion.
- Metric throughout: `candidate_minus_champion = candidate - champion`.
- Engine: `kaggle_environments==1.32.7` where recorded.

## v147_confirmed_v111_clone

Parent/reference lineage: exact v115 plus confirmed v111 second-pass reorder mechanism.
Candidate SHA-256 observed in later exact reconstruction: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`.

Run 36222557449 artifact:

- burned matched 12 pairs: 9W / 0L / 3T
- candidate_minus_champion mean: +47.50
- SE: 21.66
- pair worst: 0
- exceptions: 0
- seed 691 legs: -52 / +56 (pair +2)
- known-public panel: 24/24 pair deltas exactly 0
- sequential runtime seed 681: candidate max ~151 ms, exceptions 0
- artifact itself labels v115 as a lineage reference and says formal champion must be checked separately.

A separate run 36224507891 compared v147 to v121 and showed large regression, but that workflow's `formal champion=v121` label conflicts with the canonical champion record. It is not used for the formal v147 decision.

Decision: **KEEP TESTING**. Burned evidence is positive and pair-worst is non-negative, but there is no completed sealed/stress evidence against the formal champion in this lineage yet. Do not PROMOTE.

## v148_duplicate_sell_guard

Hypothesis: do not apply the confirmed second-pass reorder to an action containing duplicate same-item SELL orders.

Run 36230507162:

- burned 12 pairs: 7W / 0L / 5T
- mean +33.58
- SE 16.74
- pair worst 0
- exceptions 0
- seed 691 includes one -54 leg
- sequential runtime max ~160 ms

The workflow stopped before public/sealed only because its gate required every individual seat leg to be non-negative.

Decision: **KEEP TESTING / superseded by a cleaner pre-reorder guard experiment**, not a tactical REJECT based on that gate alone.

## v149_v147_pre_reorder_duplicate_guard

This is the v147-lineage v149; do not confuse it with the unrelated `v149_room_guard_buy_netting` candidate.

Run 36229344832:

- burned 12 pairs: 10W / 0L / 2T
- mean +27.17
- computed SE ~10.46
- pair worst 0
- known-public 24 pairs: all deltas 0
- seed 691 vs v115: legs -54 / +54, pair 0
- seed 691 vs v147: legs -56 / +52, pair -2
- telemetry at seed 691: probes=1, confirmed=1, duplicate_sell_guard=6, second_pass_changed=0, errors=0
- sequential runtime seed 681 max ~179 ms, exceptions 0

Decision: **KEEP TESTING**. The duplicate SELL guard removes second-pass changes at the target seed, but formal sealed/stress evidence is missing.

## Evaluation-gate bug / methodology finding

Formal evaluation policy uses the same seed with both seats swapped and evaluates `pair_diff` specifically to cancel seat advantage. Therefore a gate requiring `min_single_seat >= 0` is over-strict and can reject a candidate for pure seat asymmetry even when the matched pair is non-regressive.

Concrete example: seed 691 for the pre-reorder guard gives -54 / +54, pair 0. Rejecting this as a regression contradicts the pair-based formal methodology.

Evaluation infrastructure fix should be separated from tactical candidate changes. Promotion still requires inspection of seat dependence, but a single negative leg should not automatically fail when its swapped leg cancels it. Use pair-level worst/regression plus explicit seat-bias reporting.

## Unrelated v149_room_guard_buy_netting lineage

This is a separate v115-direct candidate and must not be merged conceptually with the v147-lineage v149.

Burned run 36213072188:

- 10W / 0L / 2T
- +144.92 +/- 115.36
- exceptions 0

Fresh run 36222646619:

- direct 20 pairs: 14W / 0L / 6T
- +224.65 +/- 96.84
- exceptions 0
- but fresh opponent panel regressed against `bl_v20`, `bl_v21`, and `frontier_prvsiyan` (small but consistent negative deltas).

Decision: **REJECT for promotion in current form** because important-opponent regression remains despite strong direct results. Keep as diagnostic evidence for room-guard/buy-netting behavior.

## v150_pre_duplicate_sell_guard

Built directly on exact formal v115 (not on a mutable champion copy). Main tactical change is the v147 confirmation mechanism with a duplicate SELL check immediately before the confirmed second-pass `_v111_reorder`, so the dangerous reapplication is blocked before it occurs.

Static builder asserts exact v115 SHA and compiles the generated source. Workflow includes focused synthetic guard tests, runtime preflight, seed 691 target tests, burned matched pairs, public regression panel, sealed direct, fresh public, and stress direct.

As of this review, run 36231635413 is queued on the self-hosted Windows runner; no result is claimed.

## Next actions

1. Treat v115 as formal champion until an explicit later PROMOTE record exists.
2. Do not promote v147 from burned/public evidence alone.
3. Evaluate v150 when compute is available, but revise the evaluation gate to pair-level regression logic; keep seat-leg asymmetry as telemetry rather than an automatic fail.
4. If v150 passes pair-level burned + public, spend sealed seeds, then stress/fresh panel and final runtime.
5. Only PROMOTE after sealed replication, no meaningful important-opponent regression, acceptable runtime, zero exceptions/timeouts, and a telemetry-supported causal explanation.
