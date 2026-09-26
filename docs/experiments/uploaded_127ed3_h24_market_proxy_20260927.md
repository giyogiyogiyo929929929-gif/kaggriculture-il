# uploaded 127ed3 h24 market-timing proxy — 2026-09-27

## Scope

Analysis-only experiment. No candidate behavior changed and no new seed was consumed.

- formal champion: `v147_candidate_confirmed_v111_clone.py`
- surviving candidate: Safety-v3, SHA256 `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- source diagnostic run: Actions `36230151111`
- diagnostic artifact: `uploaded-127ed3-v147-diagnostic`, artifact id `10902052800`, digest `sha256:0555acb180106c315311aa024a7d7f47c5c2bfb5959358751fc6e6ddccc4f4af`
- already-burned contrast seeds: 641, 350003, 733, 911, both candidate seats

This follows the pending ~24-turn h20/h24 market study in `uploaded_127ed3_eval_20260926.md`.

## Method

For every realized SELL batch in the diagnostic ledger, compare its exact realized average unit price with the maximum *observed posted market price* for the same item during the next 24 turns. Define a timing-regret proxy:

`h24_proxy = quantity * max(0, max_observed_price_next_24 - realized_avg_sell_price)`

Aggregate across both candidate seats. This is deliberately a proxy, not an exact market counterfactual: delaying a sale changes inventory, later prices, opponent behavior and possibly downstream agent state. Therefore it is suitable for rejecting broad timing hypotheses or finding candidates for exact replay, not for claiming causal profit.

Loss seeds are 641 and 350003; win seeds are 733 and 911 in the direct Safety-v3/raw-vs-v147 contrast.

## Results

### Loss seeds 641 + 350003, both seats

| item | candidate qty | candidate h24 proxy | champion qty | champion h24 proxy | candidate - champion proxy |
|---|---:|---:|---:|---:|---:|
| EGG | 642 | 52 | 626 | 60 | -8 |
| MILK | 642 | 2,960 | 642 | 2,344 | +616 |
| STRAWBERRY | 988 | 3,884 | 988 | 5,910 | -2,026 |
| FERTILIZER | 1,332 | 422 | 1,338 | 542 | -120 |
| WOOL | 580 | 10,204 | 580 | 8,556 | +1,648 |
| WHEAT | 3,788 | 5,526 | 3,964 | 6,562 | -1,036 |
| CARROT | 872 | 1,344 | 800 | 1,444 | -100 |

Candidate realized average STRAWBERRY sell price over these two loss seeds was 106.10 vs champion 104.67. The prior diagnostic conclusion that candidate premium selling is not uniformly worse remains supported.

### Win seeds 733 + 911, both seats

| item | candidate qty | candidate h24 proxy | champion qty | champion h24 proxy | candidate - champion proxy |
|---|---:|---:|---:|---:|---:|
| MILK | 978 | 4,174 | 978 | 5,470 | -1,296 |
| STRAWBERRY | 990 | 4,878 | 990 | 7,830 | -2,952 |
| FERTILIZER | 1,384 | 378 | 1,450 | 450 | -72 |
| WOOL | 1,040 | 23,156 | 1,036 | 24,076 | -920 |
| WHEAT | 1,382 | 246 | 1,590 | 210 | +36 |
| CARROT | 482 | 84 | 392 | 16 | +68 |

The strongest apparent opportunity is *not* loss-specific. Seed 733, which candidate wins by +3428 pair mean, contains very large observed WOOL rebound windows: for example candidate sells 12 WOOL at step 504 at realized average 15.75 while the observed posted price reaches 133 inside the next 24 turns. Therefore a blanket `hold WOOL up to 24 turns` rule would be fitting a pattern that is present even more strongly in a large win.

## Additional sequencing observation

Across all four contrast seeds, v147 begins with:

- step 1: `BUY_PRODUCT WHEAT 7` then `SELL WHEAT 2`
- step 2: `BUY_PRODUCT WHEAT 30` then `SELL WHEAT 30`

The uploaded candidate instead begins with:

- step 1: `BUY_PRODUCT WHEAT 5` plus `BUY_SEED WHEAT 1`
- step 2: no corresponding 30-unit WHEAT buy/sell churn

The candidate is still $10 behind v147 immediately after this opening sequence in all four diagnostics, so the later overall gains are not a trivial opening cash saving. The sequence materially changes market chronology while leaving the early path broadly comparable, which makes BUY/SELL chronology a more plausible analysis target than a universal premium-item delay.

## Decision

**NO CANDIDATE from universal h24 deferral.**

Reasons:

1. STRAWBERRY timing proxy is better for candidate than champion in both loss and win groups.
2. WOOL timing-regret proxy is very large in a major candidate win, so large observed rebound opportunity does not separate losses from wins.
3. The proxy is ex-post and does not re-simulate the market/state effects of holding inventory.
4. Existing diagnostics already show final shed=0, so this is not a residue/liquidation problem.

Do not implement a blanket `hold EGG/MILK/STRAWBERRY/FERTILIZER/WOOL for 24 turns` rule from this evidence.

## Next hypothesis

Wait for the outcome-centric regression run `36250594997` and identify actual `champion outcome -> candidate outcome` regressions by opponent/seed/seat. If W->L transitions exist, analyze those exact games first. If no W->L transition is observed, expand strategy-diverse opponent coverage before changing tactics.

For tactical follow-up, prioritize conditional BUY/SELL chronology or crop-mix/WHEAT-quantity state conditions; do not retry global productive-WHEAT, simple CARROT margin tightening, FEED reserve increases, MG/IG changes, blanket liquidation, or universal premium-product hold.
