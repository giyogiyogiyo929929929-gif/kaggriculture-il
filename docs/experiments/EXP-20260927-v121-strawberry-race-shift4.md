# EXP-20260927 — v121_strawberry_race_shift4

## Status

**REJECT — targeted external economics regress despite exact activation/repayment**

Formal champion remains `v112_wheat_lead3_lowdemand`.

## Parent / lineage

- parent: `v112_wheat_lead3_lowdemand`
- sibling of v116/v117/v118; no stacking
- branch: `eval/v112-v121-strawberry-race-20260927`
- canonical engine: `kaggle_environments==1.32.7`

## Hypothesis

v120/v120b identified a public-state clean premium sell-pressure signal absent in v112 clone self-play but present against independent external opponents. v121 tested the strongest under-liquidated STRAWBERRY hotspot by advancing exactly 4 units from a later known STRAWBERRY SELL into the current existing SELL.

The telemetry-supported gate selected the seed-309003 step-577 state against five opponents in both seats:

- external STRAWBERRY inventory delta: +5;
- price: 153;
- shed: 32;
- parent same-turn STRAWBERRY SELL: 8;
- repayment target: step 599 static STRAWBERRY SELL 22.

## Change

Single tactical change:

1. If the narrow public-state STRAWBERRY race gate fires, increase the current STRAWBERRY SELL by 4 and repay exactly 4 units from the first sufficiently large future static STRAWBERRY SELL within 48 turns.

No WOOL/MILK/MELON changes were included.

## Static / synthetic evidence

- focused synthetic checks: PASS;
- exact v112 reconstruction: PASS;
- candidate source SHA256: `e68fe0d866216c20dcdfdbdcfd391f81943a0590a09c2534ad0bd45f303d4451`;
- exact schedule audit run `36301822441`: SUCCESS;
- confirmed schedule:
  - step 577: `SELL STRAWBERRY 8`;
  - step 599: `SELL STRAWBERRY 22`;
  - step 601: `SELL STRAWBERRY 4`;
  - step 615: `SELL STRAWBERRY 10`.

The normal activation therefore uses step 599 as the repayment target.

## Focused evaluation

Corrected focused run: `36303268698` — SUCCESS.

### Fresh champion H2H

Seeds `310001–310004`, same seed and both seats:

- 0W / 0L / 4D;
- mean `candidate_minus_champion = 0.0`;
- worst `0.0`;
- v121 activations: 0;
- errors: 0;
- repay_shortfalls: 0.

So the external-only gate does not regress clone/self-play on this fresh H2H set.

### Targeted external replay — seed 309003

All 10 bronze-panel opponents were replayed with champion and candidate, both seats.

Activated opponents:

- `v49`: `+80`;
- `v50`: `+80`;
- `metav4_v13`: `-143`;
- `k256_h2_q_v1`: `-143`;
- `story_of_seasons`: `-143`.

Non-activated opponents were all exactly `0` candidate-minus-champion:

- `market_rhythm`;
- `thomas_router_93`;
- `tetsutani_dpts_b`;
- `jaxa_2802`;
- `ready_stock`.

Aggregate targeted external result:

- mean `candidate_minus_champion = -26.9`;
- median `0.0`;
- worst `-143.0`;
- best `+80.0`;
- outcome regressions: 0;
- outcome improvements: 0.

## Telemetry findings

The implementation behaved exactly as intended, so the negative result is tactical rather than a wrapper bug.

For each activated opponent:

- 2 activations total, one per seat;
- activation step: 577;
- repayment step: 599;
- 4 units shifted per game;
- repayment exact in both seats;
- `repay_deferrals = 0`;
- `repay_shortfalls = 0`;
- `errors = 0`.

Thus the same apparently favorable public state can produce opposite economics depending on the opponent. The raw clean STRAWBERRY inventory-increase signal is not sufficient to decide that a 577→599 four-unit timing shift is profitable.

## Decision

**REJECT.**

Reason:

- targeted activation matched the intended state exactly;
- implementation and repayment were correct;
- nevertheless 3 of 5 activated opponents regressed by 143 while only 2 improved by 80;
- aggregate targeted external economics were negative;
- no win/loss outcome was flipped;
- existing STRAWBERRY evidence is also concentrated on seed 309003.

Per the bronze policy, do not spend fresh-external/sealed/stress budget on this candidate and do not loosen the STRAWBERRY gate by default.

## Do not repeat

Do not repeat the generic rule:

`clean STRAWBERRY inventory increase + high price + shed surplus + current SELL -> shift 4 units from the next later SELL`.

It is opponent-sensitive even when the observed public state is identical.

## Next hypothesis

Prefer the WOOL multi-seed overlap axis from v120b, because executable WOOL overlap was observed across multiple external seeds rather than being concentrated on seed 309003. Before changing actions, segment WOOL signals by step, opponent family, price, shed, and current/future SELL overlap so that a candidate can avoid another opponent-sensitive unconditional timing shift.
