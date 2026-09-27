# EXP-20260927 — v125_day10_melon_probe

## Status

**PROBE COMPLETE — DAY10 SELL GAP CONFIRMED; INVENTORY ORIGIN NEEDS FOLLOW-UP**

Formal champion remains `v112_wheat_lead3_lowdemand`.

## Parent / environment

- source: exact `v112_wheat_lead3_lowdemand`
- engine: `kaggle_environments==1.32.7`
- workflow run: `36311788633`
- job: `108599018185`
- head: `d0b6b94c001fc64d4b1140be467648efafa8302e`
- artifact: `v112-v125-day10-melon-probe`, ID `10928987847`

## Motivation

v124 external economic-gap attribution showed that the first large persistent deficit against the important external panel appears around day 10, with step 250 the strongest common early negative event. External opponents begin a MELON liquidation wave there while v112 cash-in lags.

## Panel

Five important external opponents:

- `thomas_router_93`
- `metav4_v13`
- `k256_h2_q_v1`
- `ready_stock`
- `jaxa_2802`

Seeds `309001` and `309004`, both seats: 20 games.

Exact runtime observations/actions were recorded for steps 240–270 for both v112 and the opponent.

## Findings

The day-10 gap is real and highly repeatable across both seeds and both seats.

At step 250:

- v112 MELON shed is `0` in all captured games;
- MELON public price is `266`;
- v112 market action is only a small WHEAT purchase (`BUY_PRODUCT WHEAT 1`);
- the external opponents already request `SELL MELON 24` at the same public price.

The opponent liquidation wave commonly continues around steps 251–255 with additional MELON sells.

v112 begins its own runtime MELON sell wave later:

- step 256: `SELL MELON 12`, public price about `226`;
- step 258: `SELL MELON 24`, price about `213`;
- step 259: `SELL MELON 12`, price about `178`;
- step 261: `SELL MELON 12`, price about `156`;
- step 264: `SELL MELON 12`, price about `131`.

The money trajectory confirms these are economically material sell events rather than only inert requests. In a representative `metav4_v13 / 309001` game, the opponent cash rises sharply during the 250–255 MELON wave while v112 remains near ~1k cash until its own wave begins at 256.

At step 264 both agents show `melon_shed=12` and sell 12 MELON, so the gap is concentrated substantially earlier than the shared later liquidation.

## Interpretation

The simple hypothesis "v112 already has MELON in shed at step 250 but waits too long to sell it" is **not supported** by this probe: observed `private.shed.MELON` is 0 at step 250.

However, shed alone is not sufficient to determine whether a player can execute a MELON sell, because the observation also contains `private.inventories` for the farmer/hands. The probe did not record those inventories. Therefore it is not yet safe to conclude that the gap is purely production timing or to create an early-SELL mutation.

The next probe must identify where MELON is carried at steps 248–256 by recording exact `private.inventories`, shed and runtime actions for both v112 and the opponent.

## Decision

- v125 is telemetry only; no promotion decision.
- Do **not** create a blind step-250 MELON SELL candidate from shed data alone.
- Follow with v126 day-10 MELON carry/inventory probe.
