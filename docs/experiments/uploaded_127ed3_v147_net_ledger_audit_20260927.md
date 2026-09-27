# uploaded 127ed3 vs v147 exact market-ledger audit — 2026-09-27

Decision: **ANALYSIS ONLY**

## Source

- Existing diagnostic run: `36266384305`
- Artifact: `uploaded-127ed3-v147-diagnostic`, artifact id `10902052800`
- Seeds: `641,350003,733,911`, both seats
- Candidate: exact uploaded raw tactical path; safety-v3 wrapper is independently proven behavior-inert on the dev isolation block.
- Reference: exact `v147_candidate_confirmed_v111_clone.py`.

The engine-side `Ledger` wraps `_process_market/_commit_unit` and records each successful market unit as `(step, player, op, item, price)`. For an item, `net_market = SELL revenue - all non-SELL market costs` (e.g. WHEAT product/seed purchases and seed/animal orders where applicable).

## Correct seat mapping

This audit explicitly maps candidate to `candidate_seat` before subtracting the v147 seat. Both seat swaps reproduce the same per-item differences. A prior scratch aggregation accidentally mixed seat identity across swapped files; those scratch numbers are discarded. The table below is the corrected result.

## Whole-game per-item net difference

`candidate_minus_v147`, dollars:

| item | seed641 | seed350003 | seed733 | seed911 |
|---|---:|---:|---:|---:|
| WHEAT | **-1722** | **-1008** | **-1472** | +163 |
| CARROT | +1691 | +405 | +2324 | -6 |
| STRAWBERRY | +331 | +374 | +996 | +860 |
| EGG | +133 | +306 | 0 | 0 |
| MILK | -353 | -93 | +150 | +425 |
| WOOL | -372 | -527 | +1926 | -293 |
| FERTILIZER | -114 | +23 | -729 | +29 |
| **market-ledger sum** | **-406** | **-520** | **+3195** | **+1178** |
| final-money delta | **-406** | **-520** | **+3428** | **+1178** |

For 641, 350003 and 911 the market-ledger delta exactly reproduces final-money delta. Seed733 has a remaining +233 outside the market ledger, so the ledger must not be presented as a complete cash identity for that seed; likely non-market spend/reward differences need separate accounting if 733 itself becomes the target of a candidate.

## WHEAT decomposition on the two losses

### seed641

- WHEAT sell revenue difference: `-1513`
- WHEAT non-SELL cost difference: `+209` cost to candidate
- net WHEAT: **-1722**
- CARROT offsets `+1691`, leaving the premium/fertilizer residual to determine the final `-406`.

### seed350003

- WHEAT sell revenue difference: `-852`
- WHEAT non-SELL cost difference: `+156` cost to candidate
- net WHEAT: **-1008**
- CARROT offsets `+405`; STRAWBERRY/EGG/FERTILIZER add further positives, while WOOL/MILK remain negative.

Thus the two focal losses do share a real WHEAT deficit after costs, but the size and compensation portfolio differ. This is stronger than using gross late SELL revenue alone.

## Relation to CARROT2

CARROT2 is not simply losing money: CARROT contributes strongly positive relative value on both loss seeds, especially 641. The failure is that the CARROT gain does not fully replace WHEAT plus the premium-product residual. This is consistent with prior causal tests:

- stricter feed reserve (`feed2`) was harmful,
- early margin tightening was harmful,
- swap-cap24 was harmful,
- generic late/horizon/price suppression was unsupported by the decision trace.

Therefore the next experiment should not suppress CARROT2 generically. The directly measured unexplored asymmetry is `ca_feed_block`: 641 has 21 blocked otherwise-pays-now WHEAT→CARROT opportunities, while 350003/733/911 have 0. The next single-change screen is the opposite direction (`_CA_FEED_DAYS 1 -> 0`) on burned matched seeds; a harvest-aware relaxation is preferred over permanent reserve removal if feed0 shows benefit but creates regressions.
