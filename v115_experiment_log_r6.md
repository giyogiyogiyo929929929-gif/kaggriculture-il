# Kaggriculture experiment log — v115 continuation r6

Date: 2026-09-25

## Status

- Formal Champion: **v115_champion_same_turn_open_squeeze.py**
- Champion SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- Evaluation environment: **kaggle_environments==1.32.7**, official `kaggriculture`
- Diff convention: **candidate_minus_champion = candidate - champion**
- v66: **never use**
- Historical v119/v121 branches are not the formal Champion for this continuation.

## 1. live-herd family closed

### v129 demand-backed high-price gate

Fresh sealed seeds 201..280, 80 matched pairs / both seats, reproduced by runs `36103855560` and `36106788489`:

```text
0W / 1L / 79T
candidate_minus_champion mean = -33.3125
SE = 33.3125
mean >= 2*SE = false
worst = -2665  (seed 216)
best = 0
exceptions = 0
```

Only seed 216 differed. The high-price/demand gate removed the old seed105 failure but exposed another negative activation world. After ratio 1.15/1.20/1.25/1.30 and the demand-backed gate, the live-herd family is closed rather than threshold-tuned further.

**Decision: REJECT v129 / CLOSE live-herd family.**

## 2. v130 advanced-sale quote-priority reorder

Hypothesis: R37 sale ordering runs before `_adv_apply`, so newly advanced sales might bypass the existing quote-exposure ordering.

Change: preserve all advanced-sale item/quantity/horizon rules; only order candidate advanced items with existing `_r37_quote_priority`.

Runs:
- direct/starter: `36113931911`
- public activation panel: `36114363219`

Results:

```text
direct exact-v115 H2H, seeds 501..512: 12/12 ties
starter matched panel: 12/12 ties
5 public opponents x seeds 521..524: 20/20 ties
exceptions: 0
```

Telemetry:

```text
direct 501..504, both seats: adv_turns = 0, adv_units = 0
public activation panel, 40 games: adv_turns = 0, order changes = 0
```

The modified surface did not activate.

**Decision: NO SEPARATION / REJECT v130.**

## 3. v136 preguard quote-order

Hypothesis: hour21/22 preguard adds extra SELLs after earlier sale-order logic. Preserve selected items/quantities and only reorder those extra SELLs by `_r37_quote_priority`.

Run: `36114909575`

Results:

```text
direct seeds 541..552: 12/12 ties
5 public opponents x seeds 541..544: 20/20 ties
exceptions: 0
```

Direct telemetry seeds541..544 both seats:

```text
preguard_turns = 0
preguard_units = 0
pg_order_changes = 0
errors = 0
```

**Decision: NO SEPARATION / REJECT v136.**

## 4. v137 courier insertion-order fix

Hypothesis: V9 courier iterates delivered items by descending `price * qty` but repeatedly calls `market.insert(0, ...)`, reversing the final order. Change iteration direction only; delivery target, quantity and route unchanged.

Run: `36115297771`

Results:

```text
direct seeds 561..572: 12/12 ties
5 public opponents x seeds 561..564: 20/20 ties
exceptions: 0
```

Across 40 public telemetry games:

```text
courier_trips = 0
courier_units = 0
courier_order_changes = 0
errors = 0
```

**Decision: NO SEPARATION / REJECT v137.**

## 5. Telemetry-first pivot

Repeated no-op candidates showed that dormant layers should be measured before candidate creation.

Diagnostic workflow: `v115-multisell-diagnostic.yml`
Run: `36115734714`
Diagnostic seeds: **581..584** (development-only; never use for final sealed)

Two late insertion layers were instrumented without intentional behavior changes:

1. V92 PREDICT preempt
2. KIL v52 preempt

### V92 PREDICT

All five public opponents activated V92 in all 8 seat-games tested per opponent. Multi-item preempt turns were real:

```text
beat_v48:          pred_fires 54,  multi-item turns 8, max items 3
bl_v20:            pred_fires 102, multi-item turns 4, max items 2
bl_v21:            pred_fires 102, multi-item turns 4, max items 2
farming_v2:        pred_fires 54,  multi-item turns 8, max items 3
frontier_prvsiyan: pred_fires 126, multi-item turns 6, max items 2
```

### KIL v52

```text
copy games = 0
preempt fires = 0
multi-item turns = 0
```

Therefore KIL is not pursued. V92 is the first confirmed active multi-SELL surface after the no-op sequence.

## 6. Current candidate — v138 V92 quote-order

Candidate SHA256:
`33d495561774c1379a0f66c6a863b344ae0249fe64e196fc208a15c53188438f`

Builder:
`ci/build_v138_v92_quote_order.py`

Mechanism:

- retain V92 prediction, item eligibility, score gate, vote gate, lookahead, quantity, and market-capacity semantics;
- collect V92-generated preempt SELLs into a temporary `pending` list;
- if multiple V92 SELLs are produced on the same turn, rank only that block by existing `_r37_quote_priority`;
- prepend the resulting block exactly where V92 previously inserted the orders;
- single-item V92 turns remain behaviorally equivalent.

Targeted screen workflow:
`.github/workflows/v138-v115-v92-order-screen.yml`

Run: `36116242273`

Development/screen seeds:
- direct exact-v115 H2H: 601..612
- starter/public panel: 601..604

These seeds are **not eligible for final sealed evaluation**.

### Promotion gate

Do not promote from this screen. If v138 is positive, continue with new validation/stress seeds, then a completely fresh sealed set. Required properties remain:

- candidate_minus_champion mean > 0
- mean >= 2*SE on the relevant promotion panel
- no severe worst regression
- no dangerous seat dependence
- exceptions = 0
- final sealed seeds not used during development

## Current decision

```text
CHAMPION: v115_champion_same_turn_open_squeeze.py

REJECT / CLOSED:
- v129 demand-backed live herd
- v130 advanced-sale quote ordering (no activation)
- v136 preguard quote ordering (no activation)
- v137 courier order fix (no activation)

CURRENT CANDIDATE:
- v138 V92 multi-item quote ordering

CURRENT RUN:
- 36116242273
```
