# EXP-20260926 v152 — dense self-impact exposure reorder

## Status

**FOCUSED TEST PENDING / RUNNER BLOCKED. NOT PROMOTED.** Formal champion remains exact v147 SHA `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`.

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

## Historical overlap / safety-boundary audit

This is related to, but is not a repeat of, the already-adopted Order Book Layer D from EXP-20260922-52.

Layer D was a successful market-order mechanism: on its 18-opponent regression all 18 opponent means improved, total wins moved from 73-17 to 81-9, and it became the v27 base lineage. However, that implementation deliberately excluded SELL orders for an item that was also bought with `BUY_PRODUCT` in the same turn (the historical "wash SELL" safety boundary).

The exact current v147 `_v111_reorder` retains the same important restriction: it first forms the set of items bought anywhere in the order list and excludes SELLs of those items from reorder candidates. Therefore the step649 FERTILIZER SELL is structurally unreachable by current v111 because the same turn contains `BUY_PRODUCT FERTILIZER 2`.

v152 opens only a narrower part of that boundary:

- it operates only inside the *leading contiguous SELL block*;
- it stops at the first non-SELL order;
- therefore it never moves a SELL across its later `BUY_PRODUCT` barrier;
- the SELL-before-own-BUY relation is preserved exactly;
- quantities and the BUY order itself are unchanged.

So v152 is not a broad "allow wash SELL reordering" experiment. It tests whether SELL-vs-SELL ordering inside a dense pre-BUY block can safely use executable self-impact exposure. Because it touches a region that older Layer D intentionally kept fixed, a hard-cell win is not enough: burned direct regression and wash-item telemetry are mandatory before any sealed test.

## Static implementation audit

The builder requires the exact v147 SHA before appending the mechanism and checks that `_r37_market_price`, `_R37_MARKET_PARAMS`, `projected_shed`, and `FarmView` are present.

The critical stock input is also consistent with the hypothesis: the inherited `projected_shed(action, FarmView(observation))` delegates to the chassis `_projected_shed`, whose contract is shed contents **after unit actions but before the market runs**. It therefore does not accidentally score SELL orders from post-sale residual stock. The v152 quantity is clamped to `min(order quantity, projected pre-market stock)`.

The reorder is stable on equal scores and edits only `orders[:end]`, where `end` is the first non-SELL order. No SELL crosses the later BUY barrier.

Static audit result: **PASS for the intended one-change mechanism.** This is not a substitute for the formal full-game focused test.

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

## Focused formal workflows / infrastructure state

Primary self-hosted workflow: `.github/workflows/v152-v147-dense-self-exposure-focused.yml`

- run `36250312541`
- state at latest observation: **queued**; no game step has run
- queued state is not candidate evidence

A GitHub-hosted Ubuntu fallback was added without changing the evaluation logic:

- workflow: `.github/workflows/v152-v147-dense-self-exposure-ghhosted.yml`
- run `36252244587`
- conclusion: **failure before any workflow step** (`steps=[]`)
- this is an infrastructure/runner-start failure and is explicitly **not** counted as a tactical or runtime failure of v152

The existing v111 counterfactual diagnostic run `36250732794` is also queued and supplies no additional evidence yet.

The formal focused workflow, once an execution environment actually starts, reconstructs exact v115/v147, asserts v147 SHA, builds v152, runs `py_compile`, evaluates v152 and v147 independently against score_2820 seed520104 in both seats under engine 1.32.7, and records candidate ledger/telemetry.

## Promotion discipline

Do not spend unused sealed seeds from this focused result alone. If v152 converts or materially improves the -9 loss with zero errors, next gates are:

1. burned direct v147 seeds681..692, both seats;
2. explicitly inspect every v152 activation where a reordered SELL item is also bought later that turn, using gross SELL revenue minus BUY_PRODUCT cost rather than gross sales alone;
3. existing hard-opponent panel cells 520101..520104, both seats;
4. telemetry on every changed outcome/margin row;
5. stress;
6. only then an unused sealed range;
7. runtime final.

If the focused result is neutral or regressive, reject v152 and use the recorded counterexample rather than threshold sweeping.

## Current decision

- v152: **KEEP TESTING**, blocked only on a valid formal runner execution.
- champion: keep exact v147 unchanged.
- no sealed seeds spent.
- no Kaggle submission performed.
