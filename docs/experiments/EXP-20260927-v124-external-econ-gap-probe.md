# EXP-20260927 — v124 external economics gap probe

## Status

**PROBE QUEUED — ACTION IDENTICAL / DO NOT PROMOTE**

Formal champion remains `v112_wheat_lead3_lowdemand`.

## Motivation

The current v112 lineage loses the bronze external panel by roughly `$25k–$59k` per matched opponent/seed pair. v121/v123 show that premium micro-timing changes are generally tens to low hundreds of dollars and therefore cannot plausibly explain or close the dominant gap.

The next task is causal attribution of the large external economics deficit before designing another tactical candidate.

## Probe

Branch: `eval/v112-v124-econ-gap-probe-20260927`

Canonical engine: `kaggle_environments==1.32.7`.

Workflow run: `36311126934` (latest bound-agent run).

Panel:

- opponents: `thomas_router_93`, `metav4_v13`, `k256_h2_q_v1`, `ready_stock`, `jaxa_2802`;
- seeds: `309001`, `309004`;
- both seats;
- 20 games total.

The probe wraps both v112 and the opponent without changing returned actions.

Recorded per agent:

- final money;
- requested SELL quantity by item;
- BUY quantity by opcode/item;
- HIRE / BUY_LAND and other market-order counts;
- day-boundary money trajectory;
- observed money deltas grouped by the preceding market-action class;
- last observed shed inventory;
- exact non-empty market action tape (capped);
- `quantity × pre-order public price` sell exposure by item;
- a simple dense SELL proxy: number of turns with at least three item families each sold at quantity >=10.

## Interpretation guard

`preprice_sell_value` is **not realized revenue**. Alternating opponent orders and within-order market impact change realized transaction prices. Use it only as an exposure/timing diagnostic and cross-check against actual money trajectories.

Requested BUY/SELL quantities may also differ from executed quantities when cash/inventory constraints intervene. Actual money deltas and final money remain authoritative.

## Decision logic

Prefer a next candidate only when the gap attribution points to a repeatable mechanism across multiple opponents/seeds. Priority order:

1. large repeatable missing SELL quantity or persistently lower sale-price exposure in one/few items;
2. large avoidable BUY/HIRE/LAND cost difference;
3. a specific day/phase where the money gap opens sharply and remains;
4. dense multi-item SELL states that correlate with the gap and are not already handled by v112.

Do not create a candidate from a one-seed micro difference or from gross sell exposure alone.

If the gap is dominated by farm production quantity rather than market timing, pivot to the smallest production/farm mechanism that explains that difference instead of continuing premium SELL micro-shifts.
