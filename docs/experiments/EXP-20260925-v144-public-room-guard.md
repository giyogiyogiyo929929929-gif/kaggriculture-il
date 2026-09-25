# EXP-20260925: v144 public room_guard

Status: EVALUATING

## Canonical state

- Formal Champion: `v115_champion_same_turn_open_squeeze.py`
- Champion SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- Never use v66.
- Engine for formal evaluation: `kaggle_environments==1.32.7`.
- Metric: `candidate_minus_champion = candidate - champion`.

## Public source

Primary mechanism source:

- Kaggle kernel: `tetsutani/shape-the-shop-work-the-pasture-kaggriculture`
- Title at acquisition: `🌾 Shape the Shop Work the Pasture | Kaggriculture`
- Author metadata: `tetsu2131`
- Frozen acquisition time: `2026-09-18T00:47:08.602199+00:00`
- API response SHA256: `7081913fa660b8a060fdb2930243fe18c8079a1e201f2773e9ee044dd7cd0d55`
- Notebook payload SHA256: `a6027339030e6204e512ccf7cc3641cb158531d8924717d089638c276b94744f`
- Decoded source SHA256: `2b97e2c653018ac4aeffb8463ec91c8f26b097b4cef81289acc25ccdbc68f916`
- Mirrored Git blob SHA: `6f7f89ae425caf501a9a987bfded02145c192ffb`
- Frozen mirror: `S-Riku-tus/pj-kaggriculture/experiments/research_20260918_v120/acquisition/shape_tetsutani/decoded_main_1.py`

License evidence:

- Public downstream Kaggle output `Kaggriculture Rank Your Agent` retains attribution to tetsutani and labels the relevant route-replay derivations Apache-2.0, including the full Apache-2.0 notice.
- Keep this attribution and re-check the direct notebook license before any formal Kaggle submission artifact is made.

Static source audit:

- Public decoded source states no external data, network access, learned model, or hidden seed is used at runtime.
- The selected `room_guard` reads only public observation state: shed/inventories, current actions, market prices, and the route's own future planned sells.
- No notebook execution is required; the mechanism was inspected statically.

## Mechanism

The public `room_guard` is a one-slot day-close capacity reserve:

1. Fire only when `step % 24 == 23`.
2. Estimate projected end-of-day shed occupancy using current shed, carried inventory, same-turn harvest/collect, consumption/place, buys, and fillable sells.
3. Reserve one slot: target at most 99 items in a 100-capacity shed.
4. If projected occupancy exceeds 99, add only the SELL quantity needed to remove the excess.
5. Prefer items with no remaining planned future sale, then higher current visible price.

This directly targets inventory destruction from day-close overflow while limiting policy surface.

## Why this is a new candidate rather than copied code

The inherited route-replay chassis already contains the public `room_guard` implementation, but the v27 lineage runtime `_SETTINGS` disables it:

```python
'room_guard': False
```

v144 does not copy the public source. It changes only that existing switch in exact v115:

```text
room_guard: False -> True
```

The builder fails closed unless exact v115 contains exactly one disabled room_guard and the other dormant public layers remain disabled.

## Candidate

- Candidate: `v144_candidate_public_room_guard`
- Parent: exact formal v115
- Builder: `ci/build_v144_public_room_guard.py`
- Major changes: 1

Explicitly unchanged:

- `budget_guard=False`
- `clamp_sells=False`
- `dead_stock=False`
- `terminal_liquidation=False`
- `front_run=False`
- V92 / KIL behavior unchanged
- farm policy unchanged
- route tapes unchanged

## Hypothesis

When v115 reaches day close with projected occupancy above shed capacity, units can be discarded and therefore contribute zero final cash. A bounded pre-close SELL of only the excess can convert otherwise-destroyed inventory into cash. Because the guard only fires on hour 23 and only under projected overflow, its regression surface should be substantially smaller than broad market/farm changes.

Potential failure mode: if the guard must sell an item that has a later planned sale, it may realize that item at a worse current price. This must be checked in telemetry rather than assumed safe.

## Evaluation plan

1. Reconstruct exact v115 and verify SHA256.
2. Build v144; `py_compile`; assert candidate text equals exact v115 except the one room_guard toggle.
3. Focused synthetic checks:
   - day-close projected overflow adds exactly the needed SELL;
   - no overflow leaves action unchanged;
   - non-day-close leaves action unchanged.
4. Runtime smoke on official 1.32.7, single worker.
5. Direct v144 vs exact v115: seeds 681..692, both seats, 12 pairs / 24 games.
6. Public matched panel: seeds 681..684, both seats, starter + beat_v48 + bl_v20 + bl_v21 + farming_v2 + frontier_prvsiyan.
7. If any seed separates, inspect replay/telemetry around every hour-23 activation:
   - projected overflow units,
   - added SELL item/qty,
   - visible price,
   - actual shed loss avoided,
   - downstream planned sale displaced,
   - final cash delta.
8. If zero activations or exact ties with activations, classify no-separation/dormant; do not threshold-tune.
9. If positive with acceptable worst regression, move to a new unused stress set, then only after that allocate sealed seeds.

Seeds 681..692 are development seeds once run and must never be used for final sealed promotion evidence.

## Promotion rule

No automatic promotion from this screen. PROMOTE requires fresh matched seeds, seat-swap persistence, acceptable worst regression, public-opponent regression check, stress, completely unused sealed seeds, runtime acceptance, zero exceptions/timeouts, and a telemetry explanation for the gain.
