# EXP-20260926 v150 — v147 + singleton weak-vote gate

## Status

**HOLD / DO NOT PROMOTE.** Formal champion remains v147 SHA `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`.

## Hypothesis

Layer the earlier v143 primary-V92 singleton weak-vote abstention onto formal v147. Only a one-unit preempt with positive quote exposure and exactly one weak replay vote is suppressed. Multi-unit behavior and all v147 second-v111 logic remain unchanged.

## Candidate

- local candidate SHA256: `6baf553d0e027cb892c9c83247afe3550535181879cce478f2aa28ac1adcf6ad`
- builder: `ci/build_v150_v147_single_weak_vote.py`
- branch: `eval-v150-v147-singleton-hardcell-20260926`
- syntax: PASS

## Burned focused controls

Against exact v147 using the calibrated local evaluator:

- seed 642: 0 / 0 (pair 0)
- seed 649: 0 / 0 (pair 0)
- seed 651: +12 / +12 (pair +12)
- seed 663: +50 / -50 (pair 0)
- seed 669: +41 / -41 (pair 0)
- exceptions observed: 0

This reproduces the historical v143 shape: one robust +12 control and two seat-cancelling rows. A narrower v151 experiment adding v147 clone-confirmation as a prerequisite produced exactly the same 651/663/669 results, so clone-confirmation does not filter these cases and v151 is rejected as redundant.

## Hard-cell selection

Recovered formal v147 hard-opponent artifact run `36238658392`. v147-v115 was 0 on all 32 opponent/seed rows, but absolute v147 margins identify near-loss cells. The priority cell is:

- opponent `score_2820`
- seed `520104`
- both seats
- v147 final money `148746` vs opponent `148755`
- v147 final margin **-9** in both seats

Other narrow margins include shop_router_v7/jaxa +124, tetsutani_ms +240, peak_2950 +368 at seed520104.

## Formal hard-cell result

Workflow run `36245426356` completed successfully under `kaggle_environments==1.32.7`.

- v150 vs score_2820 seed520104: final money `148746` vs `148755` in both seats
- v147 vs score_2820 seed520104: final money `148746` vs `148755` in both seats
- candidate-minus-champion: **0 / 0; pair 0**
- v150 does not fire usefully on this priority loss cell.

Decision: no expansion to fresh/sealed evaluation. Keep v150 as HOLD evidence only; do not promote.

## Ledger finding that supersedes v150

Formal ledger workflow run `36245506969` completed successfully. The cleanest causal divergence is step649:

- v147 and score_2820 have the same pre-turn cash, same relevant shed, same farmer/hands actions, and the same market-order multiset;
- only market order differs;
- v147 leading SELL order: MILK, WOOL, FERTILIZER, WHEAT, EGG;
- score_2820 leading SELL order: FERTILIZER, WOOL, WHEAT, EGG, ... MILK after a BUY barrier;
- exact one-turn market accounting reproduces a v147 relative loss of **22** on the turn;
- MILK-first contributes +35 relative benefit, but delayed FERTILIZER costs -57, net **-22**.

The final game loss is only -9, so this clean market-order loss is large enough to motivate a new one-change candidate. Terminal liquidation is not the root issue: v147 recovers substantially late and the final turn itself improves the relative margin by one.

## Decision

- v150: HOLD / DO NOT PROMOTE.
- v151 clone-filter variant: REJECT as redundant.
- no sealed seeds spent;
- no Kaggle submission performed;
- next candidate: v152 dense self-impact exposure ordering, tested first on the same already-burned hard cell.
