# EXP-20260927 — v126_day10_melon_inventory_probe

## Status

**PROBE COMPLETE — DAY10 MELON GAP IS CARRY/RETURN ROUTING, NOT PRODUCTION SHORTAGE**

Formal champion remains `v112_wheat_lead3_lowdemand`.

## Parent / environment

- source: exact `v112_wheat_lead3_lowdemand`
- engine: `kaggle_environments==1.32.7`
- workflow run: `36314784721`
- job: `108607323051`
- runner: `CIYOI`, Windows X64, Python 3.11.9
- artifact: `v112-v126-day10-melon-inventory-probe`, ID `10930273583`
- artifact digest: `sha256:21e667de53f4649b25f088651a5a94dd7d6447ccd9d69ecb4a9286ec0da1054f`

A GitHub-hosted fallback was also attempted but failed before any workflow step/log was created; this is infrastructure evidence only and is not candidate evidence.

## Motivation

v124 economic attribution identified day-10 MELON cash-in as the first large common external deficit. v125 exact-runtime tracing confirmed that important external opponents start a MELON liquidation wave around step 250 while v112's corresponding wave starts around step 256.

v125 showed `private.shed.MELON = 0` for v112 at step 250, but did not record carried inventory. v126 therefore traced full private carry inventory and public positions/actions around the separating window.

## Probe design

No action mutation. Exact v112 and the opponent were traced directly.

Panel:

- opponents: `thomas_router_93`, `metav4_v13`, `k256_h2_q_v1`, `ready_stock`, `jaxa_2802`;
- seeds: `309001`, `309004`;
- both seats;
- 20 games total;
- steps 248–256;
- engine: `kaggle_environments==1.32.7`.

Recorded:

- full `private.inventories`;
- total carried MELON quantity;
- shed;
- farmer / hands positions;
- MELON public market inventory and price;
- exact runtime action and MELON SELL orders;
- money trajectory.

## Findings

### 1. v112 already has substantial MELON before step 250

At steps 249–250, v112 already carries **30 MELON total** while `shed.MELON = 0`.

The stable inventory shape is five hands carrying six MELON each:

```text
[{}, {}, {}, {}, {MELON: 6}, {MELON: 6}, {MELON: 6}, {MELON: 6}, {MELON: 6}]
```

Index 0 is the farmer, so hands h3–h7 are the MELON carriers.

Therefore the day-10 gap is **not caused by v112 failing to produce/harvest the first MELON batch**.

### 2. The key difference is return/PLACE timing

Representative v112 path for h3:

- step 249: position `[3,1]`, carry 6 MELON, action `EAST`;
- step 250: position `[4,1]`, carry 6, action `WATER`;
- step 251: carry 6, action `HARVEST`;
- step 252: carry 12, action `PLANT MELON`;
- step 253: starts moving `SOUTH` toward shed;
- step 254: continues `SOUTH`;
- step 255: reaches the shed row/position `[4,4]`;
- step 256: action `DROP`, then same-turn market `SELL MELON 12`.

Thus v112 deliberately performs another local WATER/HARVEST/PLANT cycle, increasing that hand from 6 to 12 MELON before returning to shed.

### 3. Same-turn deposit then sell is valid and already used by v112

At step 256, the pre-action shed snapshot is zero, h3 carries 12 MELON, runtime action includes `DROP`, and the same turn market action requests `SELL MELON 12`.

This directly confirms that farm deposit happens early enough for same-turn market liquidation in the canonical runtime path.

### 4. External opponents monetize the first batch sooner

Around step 250, important opponents carry a larger MELON batch and commonly issue four `PLACE MELON 6` operations plus `SELL MELON 24` in the same turn.

They therefore turn harvested MELON into cash while the public MELON price is still about 266, whereas v112 waits for the second local harvest/replant cycle and begins its sell wave around step 256 at a materially lower price.

## Interpretation

The causal mechanism is now substantially narrower:

- not a generic SELL-order bug;
- not a production shortage;
- not a lack of MELON at step 250;
- **v112 batches a second harvest before returning carried MELON to shed, trading earlier high-price liquidation for more local farm work.**

A blind step-250 SELL addition would be invalid because the first batch is carried by hands rather than in shed. The actionable change is a farm-route tradeoff: return one selected six-MELON carrier earlier, PLACE/DROP, and allow earlier liquidation instead of completing that hand's second local harvest/replant cycle first.

This may sacrifice or defer crop production, so the economic effect cannot be inferred from the higher immediate sale price alone. It requires direct H2H evaluation.

## Decision

- v126 is telemetry only; no promotion decision.
- Root cause is classified as **carry/return routing delay**.
- Do not create a broad farm-macro change.
- Next step: trace slightly earlier steps to identify the first-harvest acquisition point and the safest single-hand diversion point.
- Then test a narrow sibling candidate that redirects only one six-MELON carrier toward shed during the day-10 high-price window.
- Any candidate must pass same-seed seat swap, fresh validation/sealed/stress seeds, external regression checks, and runtime gates before promotion.
