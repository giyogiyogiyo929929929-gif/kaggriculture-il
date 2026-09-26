# uploaded 127ed3 evaluation — 2026-09-26

## Identity

- role: candidate only; never champion
- uploaded parent: `/mnt/data/main.py`
- uploaded SHA256: `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- formal champion: `v147_candidate_confirmed_v111_clone.py`
- champion SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- formal engine: `kaggle-environments==1.32.7`
- engine source SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- evaluation branch: `eval-uploaded-127ed3-20260926`

## Static / syntax

- local Python AST parse: PASS
- local `py_compile`: PASS
- exact upload transport is reconstructed from `ci/uploaded_127ed3/part00.b64` ... `part11.b64` and SHA-checked before formal runs.
- final uploaded callable tail: `ig_agent`.
- generic Chassis settings: `sell_lead=True`; `front_run=False`, `budget_guard=False`, `room_guard=False`, `dead_stock=False`, `terminal_liquidation=False`.
- later wrappers implement independent sale timing, overflow, endgame, inventory-gap and race/copy logic; code presence is not treated as proof of firing.

## Formal dev H2H: uploaded raw vs v147

Actions run: `36228521905` (`uploaded-127ed3-v147-dev`).

Seeds: `641, 350003, 101, 211, 347, 509, 733, 911, 1201, 1601`, both seats.

`candidate_minus_champion = candidate - champion`:

- matched pairs: 10
- W/L/D: **8/2/0**
- mean: **+688.5**
- median: **+392**
- worst regression: **-520**
- best: **+3428**
- seat0 mean: **+688.5**
- seat1 mean: **+688.5**
- exceptions: 0
- non-DONE games: 0
- max candidate game p99: 11.7561 ms
- worst observed candidate turn: 268.3734 ms

Pair means:

- 641: -406
- 350003: -520
- 101: +467
- 211: +593
- 347: +317
- 509: +292
- 733: +3428
- 911: +1178
- 1201: +1283
- 1601: +253

Decision after dev H2H: **KEEP TESTING**. No PROMOTE.

## Robustness regression

Malformed-observation probes on the raw uploaded candidate produced four `KeyError` failures and one `AttributeError` failure. v147 handled the first four and failed only the final `None` probe. This is a real preflight regression and must be fixed separately from tactical changes before any promotion.

A safety-only wrapper validation workflow was prepared to return a legal PASS action on unexpected exceptions while preserving valid-game behavior. Formal validation is currently queued behind the unavailable self-hosted runner.

## Diagnostic seeds / telemetry

Formal diagnostic run: `36230151111`, seeds `641, 350003, 733, 911`, both seats.

### Item-level candidate-minus-champion net market deltas

| seed | WHEAT | CARROT | STRAWBERRY | EGG | MILK | WOOL | FERTILIZER | final |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 641 | -1722 | +1691 | +331 | +133 | -353 | -372 | -114 | -406 |
| 350003 | -1008 | +405 | +374 | +306 | -93 | -527 | +23 | -520 |
| 733 | -1472 | +2324 | +996 | 0 | +150 | +1926 | -729 | +3428 |
| 911 | +163 | -6 | +860 | 0 | +425 | -293 | +29 | +1178 |

For WHEAT, early sale timing itself is not the simple failure mode. In seed 350003, same-size 89-unit lots sold one turn earlier by the candidate realized about `4010 vs 3812` and `3980 vs 3767`; final WHEAT deficits therefore come from broader quantity / production / purchasing differences, not merely a worse one-turn quote.

### Realized sell-rate pattern

Across all four diagnostic seeds, STRAWBERRY sell quantity is unchanged and candidate average realized unit price is higher:

- 641: +1.34/unit
- 350003: +1.51/unit
- 733: +4.05/unit
- 911: +3.45/unit

WOOL is worse on 641, 350003 and 911, but strongly better on 733. MILK is mixed.

This argues against applying one universal premium-product lead-sell rule to every item.

## Replay finding: E402 is not the root cause of the losing WHEAT paths

`E402` activates from step 624 and uses route 2 from step 648 when estimating future WHEAT/CARROT planting demand. Route 2 has no WHEAT/CARROT PLANT operations from step 672 onward.

Actual replay PLANT counts show no late planting shortfall attributable to E402:

- seed 350003: candidate/champion late planting is essentially identical; main crop differences are only two CARROT-for-WHEAT substitutions before step 624.
- seed 641: the important WHEAT→CARROT divergence starts at step 260, long before E402.
- seed 733: the important crop shift starts at step 561, also before E402.
- seed 911: planting is almost identical after the opening.

Therefore E402 removal is **not** the current priority.

## Replay finding: CARROT2 (`_CA_`) explains the crop-mix divergence

The uploaded candidate has a day 10–28 CARROT2 layer that conditionally replaces planned WHEAT planting with CARROT when its modeled value is higher.

First material substitutions:

- seed 641: step 260
- seed 350003: step 453
- seed 733: step 561
- seed 911: no material later substitution

This layer is not an obvious deletion target: on seed 733 the candidate earns +2324 CARROT while losing -1472 WHEAT and wins the pair by +3428. On seed 641 WHEAT -1722 and CARROT +1691 nearly cancel, so the remaining loss is elsewhere.

## Sale-timing layers

The uploaded candidate contains several active sale-timing layers. Diagnostic telemetry includes:

- `ADV`: 99 / 31 / 32 / 43 units on seeds 641 / 350003 / 733 / 911
- evening lead (`EV`): 64 / 23 / 9 / 6 units
- dawn lead (`DP`): 27 / 11 / 0 / 4 units
- midday lead (`MP`): 23 / 21 / 39 / 8 units
- model lead (`MPX`): 68 / 45 / 100 / 56 units
- `FLOWPX` rival-flow direct fires: 0 on all four diagnostic seeds (`_FX_FLOW_MIN=999`), despite rival-flow observations being collected
- old `V9_RACE` detector is active (nonzero rival sales / lead evidence); do not call the uploaded candidate's race machinery dormant.

## New candidate: MPX shop-aware town draw

Hypothesis: `MODELPX` currently predicts town consumption with a generic `+1 every 4 turns, +1 every 24 turns` model, ignoring shop type and multiplicity. This can mis-estimate the next inventory/price for MILK/STRAWBERRY/WOOL. The file already contains `_v9_town_draw(shops, step)`, which models item- and shop-specific draw.

Candidate changes only the MPX prediction model:

1. `_mpx_draw_units(item, step, shops)` delegates to `_v9_town_draw`.
2. MPX stores the previous step's shop list for rival-flow recovery.
3. Current-step expected inventory uses the current shop list.

Parent SHA: `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`

Candidate SHA: `e2d48abbfff9c885cefe80d6b746ec54870341284117e1f8d5436a3393b7c490`

Builder: `ci/build_uploaded_127ed3_mpx_shopdraw.py`

Local syntax: PASS.
Synthetic draw checks:

- one `YARN_STORE`, normal shop tick: WOOL draw 2
- two `YARN_STORE`, normal shop tick: WOOL draw 4
- `PIZZA_SHOP + SMOOTHIE_SHOP`, normal shop tick: MILK draw 2

Focused matched workflow: `.github/workflows/uploaded-127ed3-mpx-shopdraw.yml`, run `36232817779` queued.

Initial focused seeds are deliberately already-burned diagnostic seeds `641, 350003, 733, 911`, both seats. No fresh sealed seed is consumed at this stage.

## Runner / infrastructure status

The self-hosted Windows runner that produced the formal 1.32.7 results is currently unavailable; new self-hosted runs remain queued.

A temporary `windows-latest` fallback was tried for the focused tail ablation and safety-wrapper validation. Both failed before any workflow step started (`runner_id=0`, empty step list). These are infrastructure failures, not candidate failures. Final runtime / promotion decisions must still use the self-hosted formal path.

## Pending focused evaluations

- full / no-IG / no-MG+IG tail ablation on diagnostic seeds
- safety-only wrapper valid-game equivalence + malformed-input regression
- MPX shop-aware candidate vs raw uploaded parent

## Decision

- formal champion remains **v147**.
- raw uploaded candidate: **KEEP TESTING**.
- MPX shop-aware candidate: **TESTING / queued**, not promotion-eligible yet.
- no sealed test yet.
- no Kaggle submission performed.

## Next hypothesis / next actions

After the focused runs become available:

1. reject any ablation/model change that damages the +3428 seed 733 mechanism without compensating stability gains;
2. if MPX shop-aware improves the losing seeds without a material regression on 733/911, expand to burned dev seeds before sealed testing;
3. if tail IG/MG ablation is neutral, stop spending experiments on those layers;
4. continue item-specific sell-timing analysis, especially keeping the consistently positive STRAWBERRY behavior separate from the unstable WOOL behavior;
5. only after the uploaded candidate path is resolved, continue the planned ~24-turn h20/h24 counterfactual market study for EGG/MILK/STRAWBERRY/FERTILIZER;
6. fresh sealed seeds and known-opponent regression remain mandatory before any PROMOTE.
