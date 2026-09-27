# EXP-20260927-v118-premium-scarce-sell-front

## Status

**REJECT — no canonical activation**

Formal champion remains `v112_wheat_lead3_lowdemand`.

`v118_premium_scarce_sell_front` is a sibling of v116/v117 and was built directly on v112. It was not stacked with unpromoted sibling mechanisms. v117 was separately REJECTED for zero canonical activation.

## Hypothesis

Kaggriculture market orders are processed one order at a time with alternating players. Earlier SELL orders can therefore obtain the pre-race price before an opponent's same-item sell increases market inventory.

Premium items (`STRAWBERRY`, `MELON`, `MILK`, `WOOL`) have much steeper oversupply-side price collapse than WHEAT/EGG/FERTILIZER. When exactly one premium item is currently scarce and it appears behind only low-risk, non-scarce SELLs in the same action, moving that premium SELL to the front may improve race robustness without changing quantity, turn, slots, or cash dependencies.

## Change

One major change only: reorder exactly one premium SELL to market position 0 when all gates pass.

Safety gates:

1. step >= 239;
2. at least two market orders;
3. every market order is `SELL`;
4. exactly one positive-quantity premium SELL among `STRAWBERRY`, `MELON`, `MILK`, `WOOL`;
5. premium item is publicly scarce: market inventory < 10000 and current price >= 110% of base;
6. premium SELL is not already first;
7. every preceding SELL is one of `WHEAT`, `EGG`, `FERTILIZER`;
8. no preceding low-risk item is itself scarce/racing: inventory < 10000 and price >= 105% of base blocks the reorder.

The candidate preserves market order count, every item quantity, action turn, and relative order of every non-moved order. Mixed BUY/SELL actions are blocked.

## Static / synthetic

`test_v118_suffix_synthetic.py` covers scarce MILK and STRAWBERRY reorder cases plus already-front, non-scarce, multiple-premium, unsafe prefix, racing WHEAT prefix, mixed BUY/SELL, and zero-inventory scarcity.

Result: `v118 synthetic checks: PASS`.

The zero-inventory case caught and fixed a truthiness bug that would otherwise have treated `inventory=0` as missing and suppressed an extreme-scarcity activation.

## Canonical evaluation

Workflow: `.github/workflows/v112-v118-selfhosted.yml`.

Run: `36281995854` on self-hosted runner `CIYOI`.

Engine: `kaggle_environments==1.32.7`.

Source SHA-256:

- v112: `1c6e00ff0bd46b16189b1f6a93ce5e498ff8ffb5b0acb33591cdd247cd8b4771`
- v118: `25bb79c32a5fdc3e40f21436233f1993a60e7a0a6c55ca827f1e643fb3ce49e5`

Sign: `candidate_minus_champion = candidate - champion`.

Same-seed + seat-swap throughout.

### Champion H2H

- validation 300001–300012: **0W 0L 12D**, mean `0.0`, worst `0.0`, best `0.0`
- sealed 301001–301004: **0W 0L 4D**, mean `0.0`, worst `0.0`, best `0.0`
- stress 302001–302008: **0W 0L 8D**, mean `0.0`, worst `0.0`, best `0.0`
- starter seeds 1–5: v118 and v112 both **5W 0L 0D**, identical pair differences

All 24 champion matched seeds were exactly identical to v112.

### Runtime

Runtime pair seed `800502`:

- callbacks: `1438`
- median: `0.751750 ms`
- p99: `1.882200 ms`
- max: `2.538900 ms`
- callback errors: `0`

Runtime is comfortably inside the project gate.

### Telemetry

Validation:

- `reorders=0`, `units=0`, `moved_positions=0`
- `non_sell_blocks=1436`
- `multi_premium_blocks=202`
- `already_front_blocks=238`
- `scarcity_blocks=34`
- `front_race_blocks=4`
- `errors=0`

Sealed:

- `reorders=0`
- `non_sell_blocks=484`
- `multi_premium_blocks=68`
- `already_front_blocks=90`
- `scarcity_blocks=4`
- `front_race_blocks=2`
- `errors=0`

Stress:

- `reorders=0`
- `non_sell_blocks=958`
- `multi_premium_blocks=130`
- `already_front_blocks=174`
- `scarcity_blocks=18`
- `front_race_blocks=4`
- `errors=0`

The activation gate reported:

`{'validation_reorders': 0, 'total_reorders': 0, 'errors': 0, 'runtime_errors': 0}`

and terminated with `REJECT_GATE: no validation activation`.

The bronze external panel was therefore correctly skipped. No external score claim is made for v118.

## Interpretation

The mechanism is syntactically and operationally safe, but its conjunction of gates never occurs in the tested canonical distribution. The strongest blockers are the mixed/non-SELL-action gate, multiple-premium SELL gate, and premium-already-front condition. This means the candidate is not evidence that same-turn premium ordering is ineffective; it is evidence that this exact narrow trigger is too restrictive to test the mechanism in realistic play.

A direct repetition of v118 is not useful. A follow-up premium-ordering candidate should change the activation model rather than merely add more seeds. The most defensible next variant is to handle multiple premium SELLs by ranking them from public inventory/price race state while preserving the complete action multiset and keeping BUY-containing actions blocked.

## Decision

**REJECT — no activation.**

Reason: zero canonical reorders across validation, sealed, and stress. No exception, timeout, runtime regression, or repayment issue occurred.

Formal champion remains `v112_wheat_lead3_lowdemand`.
