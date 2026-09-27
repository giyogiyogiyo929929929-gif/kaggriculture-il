# uploaded 127ed3 CARROT2 feed0 — causal divergence trace — 2026-09-27

Decision: **CAUSAL HYPOTHESIS SUPPORTED; retain feed0 for remaining gates**

## Identity

- Candidate: `uploaded_127ed3_ca_feed0`
- Candidate SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- Parent/champion: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Run: `36295996084`
- Artifact: `uploaded-127ed3-ca-feed0-divergence-trace`, id `10924761416`
- Exceptions: `0`
- All traced games: 720 turns, direct final state `DONE`

## Method

For each candidate turn, the workflow calls the actual feed0 agent and an independently loaded safety-v3 shadow parent on the **same observation**. It records the first action divergences and both CARROT2 reports. This isolates the immediate decision difference before interactive market/game dynamics can cause downstream state divergence.

Burned nonzero seeds traced on both candidate seats:

`641,350003,347,1201,1601,623,625,628,629,630,632`

Seat0 and seat1 reproduce the same first-divergence step and final candidate-minus-parent delta for every traced seed.

## First divergence

| seed | final delta | first step | immediate difference |
|---:|---:|---:|---|
| 641 | +193 | 323 | feed0 PLANT CARROT / parent PLANT WHEAT |
| 350003 | +147 | 656 | feed0 PLANT CARROT / parent PLANT WHEAT |
| 347 | -12 | 656 | feed0 PLANT CARROT / parent PLANT WHEAT |
| 1201 | +66 | 566 | feed0 converts two parent WHEAT plants to CARROT |
| 1601 | +15 | 566 | feed0 converts two parent WHEAT plants to CARROT |
| 623 | +15 | 566 | feed0 converts two parent WHEAT plants to CARROT |
| 625 | -4 | 656 | feed0 PLANT CARROT / parent PLANT WHEAT |
| 628 | -16 | 656 | feed0 PLANT CARROT / parent PLANT WHEAT |
| 629 | +255 | 500 | feed0 PLANT CARROT / parent PLANT WHEAT |
| 630 | +22 | 656 | feed0 PLANT CARROT / parent PLANT WHEAT |
| 632 | +186 | 656 | feed0 PLANT CARROT / parent PLANT WHEAT |

At the first divergence, the shadow parent CARROT2 report has already incremented `ca_feed_block`, while feed0 has no feed block and performs the extra CARROT substitution. Examples:

- seed641 step323: candidate `ca_swaps=18`, parent `ca_swaps=17`, parent `ca_feed_block=1`;
- seed350003 step656: candidate `ca_swaps=22`, parent `ca_swaps=21`, parent `ca_feed_block=1`;
- seed629 step500: candidate `ca_swaps=10`, parent `ca_swaps=9`, parent `ca_feed_block=5`.

This demonstrates that the final money differences are downstream of the intended single change: removing the one-day WHEAT feed-reserve block from CARROT2. The high feed-block count is not merely correlated with hard games; the same-observation trace shows the exact reserve-blocked WHEAT→CARROT action as the first behavioral divergence.

## Interpretation

The trace supports the mechanism behind feed0's gains, but does not prove that removing the reserve globally is the best condition. Small negative cases (`347`, `625`, `628`) arise from the same immediate extra CARROT conversion as the positive cases. The known-opponent starter margin compression therefore remains a real robustness concern.

This is why `harvestcredit_v1` is being tested separately: preserve the one-day reserve but relax it only when route-scheduled near-term WHEAT harvests keep feed inventory solvent.

## Next gates

For feed0:

1. first sealed direct verifier — PASS (`36295374931`);
2. second precommitted sealed — released after gates, run `36300290715` queued;
3. runtime — `36295797394` queued;
4. final preflight — `36295816696` queued;
5. PROMOTE / KEEP TESTING / REJECT only after all remaining results are reviewed.

For harvestcredit_v1, use only burned dev first; do not consume fresh seeds unless it passes.
