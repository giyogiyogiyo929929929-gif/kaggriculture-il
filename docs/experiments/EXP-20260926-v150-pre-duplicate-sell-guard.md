# EXP-20260926 — v150 pre-reorder duplicate-SELL guard

## Superseding lineage note — 2026-09-26

**This experiment is v115-lineage evidence only and is not a formal-champion promotion path.** After this plan was created, the newer primary handover / promotion report was recovered from the Project Library and SHA-verified against the exact source. The current formal champion is `v122_champion_step649_wheat_after_fert.py`, SHA256 `ae4c0f5a9afabf2e6d668cf0571b41bfe9a52a9179b499a71aeb6b7508ace8f1`. Therefore v150 must not be promoted even if its queued workflow later succeeds. Any mechanism worth retaining must be re-derived and evaluated from exact v122 as a separate candidate.

## Status

**SUPERSEDED / LINEAGE-ONLY. Do not promote.** Workflow run `36231635413` may remain queued for historical evidence, but its reference is v115 rather than the current formal champion.

## Version / parent / historical reference

- candidate: `v150_pre_duplicate_sell_guard`
- builder: `ci/build_v150_pre_duplicate_sell_guard.py`
- logical parent mechanism: `v147_confirmed_v111_clone`
- source/reference parent for this historical experiment: exact `v115_champion_same_turn_open_squeeze`
- v115 SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- v147 comparison SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- current formal champion (not the parent of this experiment): exact v122 SHA256 `ae4c0f5a9afabf2e6d668cf0571b41bfe9a52a9179b499a71aeb6b7508ace8f1`
- branch: `eval-v150-pre-duplicate-sell-guard-20260926`
- workflow run: `36231635413`
- metric inside this historical workflow: `candidate_minus_reference = v150 - v115`

## Hypothesis

v147's confirmed second-pass `_v111_reorder` improves final cash on multiple v115-lineage matched seeds, but seed 691 showed a seat-reversing `-52 / +56` leg when one market action contained multiple SELL orders for the same item (`CARROT`). The rejected v148 guard was downstream of v147 and therefore could not prevent the reorder it intended to block.

v150 builds directly on exact v115, retains v147's confirmation logic, and checks for duplicate SELL item kinds immediately before the confirmed second-pass `_v111_reorder`.

## Preregistered burned prediction

Recorded before the v150 workflow produced any match result. If the narrow v115-lineage hypothesis is correct, expected seeds 681..692 are 8W/0L/4D, mean `+47.333...`, worst pair `0`, minimum single-seat delta `0`, with seed 691 restored from `-52/+56` to `0/0`.

## Focused telemetry basis

The v147 focused artifact `10900648604` showed:

- seed 681: unique SELL kinds; `+4/+4`
- seed 682: unique SELL kinds; `+170/+170`
- seed 689: unique SELL kinds; `+230/+230`
- seed 691: duplicate `CARROT` SELL orders; `-52/+56`
- first-divergence observations were equal and SELL multisets unchanged; treatment changed order only.

This remains useful historical mechanism evidence, but it is not evidence that the same change helps v122.

## Decision

**SUPERSEDED / DO NOT PROMOTE. Formal champion remains exact v122.**

## Next

Use exact v122 as the parent. The immediate diagnostic is behavior-preserving step-649 realized-order telemetry; only after the realized execution pattern is known should another isolated order-only tactical candidate be created.
