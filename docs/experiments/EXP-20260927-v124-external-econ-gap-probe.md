# EXP-20260927 — v124 external economics gap probe

## Status

**PROBE COMPLETE — LARGE SELL-CASH GAP; DAY10 MELON PHASE SELECTED FOR FOLLOW-UP**

Formal champion remains `v112_wheat_lead3_lowdemand`.

## Probe

Branch: `eval/v112-v124-econ-gap-probe-20260927`

Canonical engine: `kaggle_environments==1.32.7`.

Workflow run `36311126934`, job `108597136019`: **SUCCESS**.

Panel:

- opponents: `thomas_router_93`, `metav4_v13`, `k256_h2_q_v1`, `ready_stock`, `jaxa_2802`;
- seeds: `309001`, `309004`;
- both seats;
- 20 games total.

The probe is action-identical.

Mean final v112-minus-opponent gaps:

- `thomas_router_93`: `-36,808`;
- `metav4_v13`: `-55,108.5`;
- `k256_h2_q_v1`: `-56,428`;
- `ready_stock`: `-49,635.5`;
- `jaxa_2802`: `-49,240`.

## Main finding: cash-in deficit, not primarily a cost deficit

Observed money deltas grouped by the previous market-action class show a repeated pattern across all five opponents:

- v112 `sell_only` cash-in is tens of thousands lower than the opponent trace;
- BUY-only and HIRE-only differences are generally hundreds to a few thousand dollars, much smaller than the final deficit;
- therefore the dominant gap is not explained by simple excess HIRE/BUY/LAND cost.

Examples of mean `sell_only` cash-in deficit (v112 minus opponent):

- thomas: about `-51.9k`;
- metav4: about `-37.9k`;
- k256: about `-45.4k`;
- ready_stock: about `-42.4k`;
- jaxa: about `-33.7k`.

These class sums are diagnostic accounting, not a proof of item-level causality, but they are large enough to redirect the search away from tens-dollar premium micro-shifts.

All inspected v112 games still end with zero shed across the tracked items, so generic endgame liquidation is not the missing mechanism.

## Money-gap timing

Averaged over all 20 games, v112 is approximately even/ahead through day 7. The deficit starts to become persistent around days 8–11 and then grows through the rest of the game.

Approximate mean v112-minus-opponent money gap:

- day 7: `+944`;
- day 8: `-328`;
- day 9: `-1,435`;
- day 10: `-532`;
- day 11: `-5,439`;
- day 12: `-9,403`;
- day 17: `-26,207`;
- day 25: `-34,853`;
- day 29: `-42,951`;
- final: `-49,444` averaged over the 20-game panel.

The first major persistent collapse is therefore around the day-10/day-11 transition rather than only in the endgame.

## Step-level hotspot

Using actual observed money changes (not gross requested SELL quantities), step `250` is the strongest common early negative event in this panel, averaging roughly `-6.3k` v112-minus-opponent. Steps `251–255` add several thousand more negative cash-flow difference.

In representative traces, the external agents begin a high-value MELON sequence around this phase, commonly:

- step250: `SELL MELON 24`;
- step251: `SELL MELON 12`;
- step252/253/255: repeated `SELL MELON 6` batches;
- some agents add MILK/FERTILIZER around the same window.

At the same time v112 is mostly executing small WHEAT product/SELL actions and does not issue its larger MELON SELL until around step264.

Across steps 240–270, the mean cumulative cash-flow difference is about `-8.9k`, large enough to justify a dedicated runtime inventory/production diagnostic.

## Important measurement caveat

Some external agents use extremely large requested SELL quantities as a sell-all sentinel. Therefore:

- raw requested opponent SELL quantity is **not** a valid production or executed-volume comparison;
- `quantity × pre-order price` is also unusable for those sentinel orders as a realized-revenue estimate;
- actual money trajectories are authoritative.

The next probe must inspect real shed availability and exact runtime actions rather than infer production from requested quantities.

## Next hypothesis / v125 probe

The key question is whether v112 already has MELON inventory around step250.

- If MELON is already in shed, a larger earlier SELL timing mechanism could plausibly recover several thousand dollars and is worth a narrow candidate.
- If MELON is not yet available, the day10 deficit is a production/harvest timing issue and the next candidate should target the smallest farm mechanism that explains earlier MELON availability.

`v125_day10_melon_probe` records exact v112 and opponent shed, money, MELON public price/inventory, and runtime actions for steps 240–270 across the same five opponents, two seeds, and both seats.
