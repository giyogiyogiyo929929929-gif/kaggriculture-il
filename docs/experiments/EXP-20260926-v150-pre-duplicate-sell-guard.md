# EXP-20260926 — v150 pre-reorder duplicate-SELL guard

## Status

**EVALUATING. Do not promote from this plan.**

## Version / parent / champion

- candidate: `v150_pre_duplicate_sell_guard`
- builder: `ci/build_v150_pre_duplicate_sell_guard.py`
- logical parent mechanism: `v147_confirmed_v111_clone`
- source parent: exact formal `v115_champion_same_turn_open_squeeze`
- formal champion SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- v147 comparison SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- branch: `eval-v150-pre-duplicate-sell-guard-20260926`
- workflow run: `36231635413`
- metric: `candidate_minus_champion = candidate - champion`

## Hypothesis

v147's confirmed second-pass `_v111_reorder` improves final cash on multiple direct matched seeds, but seed 691 showed a seat-reversing `-52 / +56` leg when one market action contained multiple SELL orders for the same item (`CARROT`). The rejected v148 guard was downstream of v147 and therefore could not prevent the reorder it intended to block.

Build directly on exact formal v115, retain v147's confirmation logic, and check for duplicate SELL item kinds immediately before the confirmed second-pass `_v111_reorder`. Skip only that second pass when duplicate SELL item kinds are present.

## Changes

One tactical change relative to the v147 mechanism:

1. Before the confirmed second-pass reorder, detect duplicate SELL item kinds and skip the second pass for that action.

No farm strategy, sale quantity policy, prediction threshold, or endgame policy is intentionally changed.

## Evaluation environment

- engine: `kaggle_environments==1.32.7`
- runner: self-hosted Windows X64
- Python: 3.11
- champion reconstructed from the established v27 + v76 patch lineage and SHA-verified before evaluation
- candidate is generated from exact champion source, not by wrapping v147

## Evaluation sequence

1. static / `py_compile`
2. synthetic duplicate-SELL predicate checks
3. runtime preflight (`seed 681`, single process)
4. focused target `seed 691`, both seats, versus v115 and v147
5. burned matched screen `681..692`, seat swap
6. known-public regression panel (`starter`, `beat_v48`, `bl_v20`, `bl_v21`, `farming_v2`, `frontier_prvsiyan`)
7. unused sealed direct seeds `991001..991012`, seat swap, only after prior gates pass
8. fresh public screen `991101..991103`
9. stress direct seeds `991013..991032`

The sealed range was searched in the repository before use and had no match. It is used once for this candidate and must not be retuned against if the sealed gate fails.

## Gates before sealed evaluation

Burned gate requires:

- no matched-pair loss
- mean candidate-minus-champion at least `+40`
- worst matched pair nonnegative
- every burned single-seat leg nonnegative
- seed 691 single-seat minimum nonnegative
- zero candidate exceptions

Known-public gate requires no negative candidate-minus-champion rows and zero candidate exceptions.

Sealed gate requires no pair losses, at least one pair win, positive mean, every single-seat leg nonnegative, and zero exceptions before stress evaluation is spent.

## Results

Pending workflow completion.

## Runtime

Pending workflow completion.

## Telemetry findings

Pending. Required focused checks are seed 691 (guard must prevent the unsafe second pass) and positive reorder seeds such as 689 (safe unique-item reorder must remain active).

## Decision

**Pending. Formal champion remains exact v115 until all promotion conditions are satisfied.**

## Next hypothesis

Pending result and telemetry analysis.
