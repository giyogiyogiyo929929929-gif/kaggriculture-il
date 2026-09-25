# EXP-20260926-v148: room_guard future-SELL reserve

## Status

PLANNED / DIAGNOSTIC CANDIDATE. Do not promote from this log alone.

## Champion

- `v115_champion_same_turn_open_squeeze.py`
- SHA256 `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- Formal engine: `kaggle_environments==1.32.7`

## Parent / motivation

Parent mechanism is v144 public `room_guard`, currently **KEEP TESTING**.

v144 direct development screen on seeds 681-692, both seats:
- 9W / 1L / 2T paired cash deltas
- mean `+49.67`
- best seed683 `+492`
- worst seed689 `-84`
- zero exceptions
- seat means approximately `+48.92 / +50.42`

Those cash deltas are not sufficient promotion evidence. Hard-opponent outcome conversion and causal telemetry are still pending because the self-hosted runner is unavailable.

## Static finding

The inherited chassis `room_guard` uses future planned SELLs only as a boolean priority term:

```python
priority = sorted(PRODUCTS, key=lambda it: (
    self.future_sells(route, it, step + 1) > 0,
    -view.prices.get(it, 0), it,
))
```

but its sellable quantity is currently:

```python
avail = max(0, view.shed.get(item, 0) - planned_sells.get(item, 0))
```

Therefore, when dead/unreserved stock is insufficient to cover estimated overflow, v144 may pre-sell inventory that the route expects to SELL later. Exact v115 already contains a separate outer SHEDROOM mechanism, so the extra chassis room_guard should be conservative rather than consume route-reserved inventory.

## Hypothesis

Keep v144's hour-23 room_guard activation, but restrict its extra SELL quantity to stock above all remaining planned SELL quantity:

```python
avail = max(
    0,
    view.shed.get(item, 0)
    - planned_sells.get(item, 0)
    - self.future_sells(route, item, step + 1),
)
```

This should preserve v144's useful disposal of genuinely spare stock while reducing regressions caused by pre-selling route-reserved inventory. Any overflow that cannot be handled from surplus is left to exact-v115's existing later/outer safety behavior.

## Changes

`ci/build_v148_room_guard_future_reserve.py` performs exactly two linked edits relative to exact v115:
1. enable the same public chassis `room_guard` switch as v144;
2. modify only room_guard's `avail` expression to reserve future planned SELL quantity.

All other dormant chassis switches remain unchanged:
- `budget_guard=False`
- `clamp_sells=False`
- `dead_stock=False`
- `terminal_liquidation=False`
- `front_run=False`

## Evaluation plan

1. exact-v115 SHA verification
2. builder fail-closed checks + `py_compile`
3. synthetic comparison against v144:
   - no future SELL -> v148 must match v144 room_guard behavior
   - future SELL reserve constrains extra SELL quantity
   - no overflow -> no added SELL
   - non-hour23 -> no added SELL
4. burned causal/control seeds 681-693 as diagnostics only, especially 683 / 689 / 693
5. fresh development seeds with both seats
6. only after positive direct evidence: hard-opponent outcome conversion
7. telemetry/replay on separating seeds
8. stress, then unused/sealed only if earlier gates pass

## Pending causal evidence

Enhanced v144 telemetry commit `8063c840a94fa5eb92e2cb5b9306d30e0ada9002` records 48 turns after the first v115/v144 action divergence for seeds 683, 689 and 693. The corresponding Actions run is queued while the self-hosted runner is unavailable.

The future-reserve explanation for seed689 is therefore **plausible but not yet confirmed**. If telemetry contradicts it, v148 should be CLOSED rather than threshold-tuned.

## Decision

KEEP AS DIAGNOSTIC CANDIDATE. Champion remains exact v115.
