# EXP-20260926 v150 — v147 + singleton weak-vote gate

## Status

**KEEP TESTING / NOT PROMOTED.** Formal champion remains v147 SHA `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`.

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

This reproduces the historical v143 shape: one robust +12 control and two seat-cancelling rows. No evidence yet that v147 interaction removes the seat dependence.

A narrower v151 experiment adding v147 clone-confirmation as a prerequisite produced exactly the same 651/663/669 results, so clone-confirmation does not filter these cases and v151 is rejected as redundant.

## Hard-cell motivation

Recovered formal v147 hard-opponent artifact run `36238658392`. v147-v115 was 0 on all 32 opponent/seed rows, but absolute v147 margins identify near-loss cells. The priority cell is:

- opponent `score_2820`
- seed `520104`
- both seats
- v147 final margin: **-9**

Other narrow margins include shop_router_v7/jaxa +124, tetsutani_ms +240, peak_2950 +368 at seed520104.

## Formal focused workflows

- v150 vs v147 + score_2820 seed520104: run `36245426356`, currently queued at last observation.
- v147 vs score_2820 seed520104 market/shed/price ledger: run `36245506969`, currently queued at last observation.

No result from a queued workflow is counted as evidence.

## Decision so far

Do not spend fresh sealed seeds. If the hard-cell run does not convert or materially improve the -9 loss, v150 should remain HOLD/REJECT and the ledger should drive the next 1-change candidate. No Kaggle submission was performed.
