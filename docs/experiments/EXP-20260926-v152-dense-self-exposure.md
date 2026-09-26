# EXP-20260926 v152 — dense self-impact exposure reorder

## Status

**FOCUSED TEST PENDING. NOT PROMOTED.** Formal champion remains exact v147 SHA `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`.

## Parent / candidate

- parent/champion: v147 `v147_confirmed_v111_clone`
- parent SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- builder: `ci/build_v152_v147_dense_self_exposure.py`
- branch: `eval-v150-v147-singleton-hardcell-20260926`
- formal engine target: `kaggle_environments==1.32.7`

## Hypothesis

A dense multi-item SELL block creates an order-index race. Existing r37 quote exposure estimates loss after a hypothetical rival standing-production batch, but that is not the same quantity as the executable stock exposed by the current order. On the clean score_2820/520104 step649 divergence, v147 protects MILK but delays a larger FERTILIZER race exposure.

Define self-impact exposure for an executable SELL quantity `q` as:

`sum(price(inv + j), j=0..q-1) - sum(price(inv + q + j), j=0..q-1)`

This is the cash lost if an equal-size same-item batch reaches the market before our batch.

## One-change scope

v152 changes only market ordering when all of these hold:

- step 288..693;
- market starts with a contiguous SELL block;
- that leading block has at least five SELL orders;
- all items in that block are distinct.

Then only that leading block is stable-sorted by descending self-impact exposure. Quantities, items, non-SELL orders, BUY barriers, farm actions, opening and terminal windows are unchanged.

The `>=5` condition represents a dense multi-product liquidation/race rather than ordinary small sale blocks; it also keeps the focused hard-cell intervention narrow.

## Causal source cell

Formal ledger run `36245506969`, opponent `score_2820`, seed520104, both seats.

At step649, before actions:

- both sides have the same cash and relevant shed;
- farmer/hands actions are identical;
- market order multiset is identical;
- the only clean difference is order.

v147 leading SELL block:

`MILK 9, WOOL 7, FERTILIZER 18, WHEAT 6, EGG 2`

Executable stock is MILK9, WOOL4, FERTILIZER17, WHEAT6, EGG2. Using the observed market inventory and exact price curve, self-impact exposures are approximately:

- FERTILIZER: 57
- MILK: 35
- WOOL: 14
- WHEAT: 0
- EGG: 0

v152 therefore proposes:

`FERTILIZER, MILK, WOOL, WHEAT, EGG`

without crossing the later BUY_PRODUCT FERTILIZER barrier.

Exact one-turn accounting of the recorded state predicts the step649 relative result changes from `-22` to `+35`, a **+57 margin swing**. This is only a focused counterfactual; full-game cascade must be tested in the formal engine.

## Activation audit on the source replay

Scanning the full v147 vs score_2820 seed520104 ledger, the dense precondition is eligible at steps 577, 649 and 673 in each mirrored seat. However:

- step577 is already in self-impact order;
- step673 is already in self-impact order;
- only step649 changes.

Thus the source-cell intervention is a single action-order change per game despite a general market rule.

## Focused formal workflow

Workflow: `.github/workflows/v152-v147-dense-self-exposure-focused.yml`

Run at creation: `36250312541` (queued at last observation; no queued state is counted as evidence).

The workflow:

1. reconstructs exact v115 and exact v147;
2. asserts v147 SHA;
3. builds v152;
4. runs `py_compile`;
5. evaluates v152 vs v147 independently against score_2820 seed520104, both seats, formal engine 1.32.7;
6. records v152 telemetry and a full candidate ledger.

## Promotion discipline

Do not spend unused sealed seeds from this focused result alone. If v152 converts or materially improves the -9 loss with zero errors, next gates are:

1. burned direct v147 seeds681..692, both seats;
2. existing hard-opponent panel cells 520101..520104, both seats;
3. telemetry on every changed outcome/margin row;
4. stress;
5. only then an unused sealed range;
6. runtime final.

If the focused result is neutral or regressive, reject v152 and use the recorded counterexample rather than threshold sweeping.
