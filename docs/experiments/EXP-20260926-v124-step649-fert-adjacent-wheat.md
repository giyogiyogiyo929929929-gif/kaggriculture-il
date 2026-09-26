# EXP-20260926 — v124 step649 FERT-adjacent WHEAT

## Status

**PREREGISTERED / EVALUATING. Not promoted.**

## Version / parent / champion

- formal champion / parent: `v122_champion_step649_wheat_after_fert.py`
- exact parent SHA256: `ae4c0f5a9afabf2e6d668cf0571b41bfe9a52a9179b499a71aeb6b7508ace8f1`
- candidate: `v124_candidate_step649_fert_adjacent_wheat.py`
- candidate SHA256: `e5386b0708e7a5bde1b348a4942545a8e9ab453585fdd354ffaf9528c7cb9710`
- comparison convention: `candidate_minus_champion = v124 - v122`

## Telemetry basis

Exact-engine v123 observation-only telemetry reproduced the known v122 mechanism on priority seeds `401001..401003` and validation seeds `402001..402012`, both seats.

- v122 fired on 14/15 seeds and every fired seed had positive matched-pair delta versus v104.
- the only non-fire control, seed `401002`, was exactly 0 versus v104.
- in `401002`, FERTILIZER was already before WHEAT and the ungated predecessor's only effective WHEAT/EGG crossing had previously produced a negative result.
- in many positive v122 fires, moving WHEAT to block-end crosses FERTILIZER and then one or more unrelated trailing SELLs, commonly EGG.

This suggests the useful interaction may be specifically `FERTILIZER before WHEAT`, while crossing unrelated trailing SELLs is unnecessary or potentially harmful.

## Hypothesis

When v122 fires at step 649, keep its intended `FERTILIZER before WHEAT` relation but place WHEAT immediately after the **last FERTILIZER SELL** in the initial contiguous SELL block instead of forcing WHEAT behind every unrelated trailing SELL.

If the v122 gain is driven by the FERTILIZER/WHEAT relation, this should retain that mechanism while removing incidental EGG/other-item crossings.

## Changes

One tactical change only, appended on exact v122:

1. Detect whether v122 fired on the current step-649 call by comparing the v122 fire counter before/after the parent call.
2. Only on those calls, move WHEAT from v122's SELL-block end to immediately after the last FERTILIZER SELL.
3. Preserve all quantities, execution turn, BUY/HIRE barriers, and relative order of every non-WHEAT order.
4. No route, farm, prediction, quantity, purchase, or liquidation change.

## Evaluation plan

1. exact SHA gate and `py_compile` / AST
2. focused synthetic order test
3. burned mechanism screen: `401001..401003` + `402001..402012`, both seats, v124 vs exact v122
4. stop immediately if pair mean <= 0, any pair regression, exception, or non-DONE game occurs
5. only if the mechanism screen passes, evaluate fresh `407001..407020`, both seats
6. only if fresh has `mean - 2SE > 0`, zero pair regressions, zero exceptions and zero non-DONE games, open sealed `408001..408020`
7. known-opponent/starter/runtime promotion panel only after sealed success

Diagnostic seeds are mechanism-development evidence only. Fresh/sealed blocks, not 401/402, will carry adoption weight.

## Decision

Pending. Formal champion remains exact v122.
