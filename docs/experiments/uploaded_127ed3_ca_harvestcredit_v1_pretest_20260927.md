# uploaded 127ed3 CARROT2 harvest-credit v1 — pretest — 2026-09-27

Status: **CANDIDATE BUILT / BURNED DEV QUEUED**

## Identity

- Formal parent/champion: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Candidate: `uploaded_127ed3_ca_harvestcredit_v1`
- Candidate SHA256: `56736e406f6cc023b0b720bd1b7aee556ed7aba4caa92a9ba427336cb047a95f`
- Builder: `ci/build_uploaded_127ed3_ca_harvestcredit_v1.py`
- Formal engine target: `kaggle-environments==1.32.7`
- Difference convention: `candidate_minus_champion = candidate - champion`

## Motivation

`uploaded_127ed3_ca_feed0` removes CARROT2's one-day WHEAT feed reserve globally and has strong direct-parent evidence so far, including combined 34-seed mean `+35.4412` and mean-2SE `+8.5122`. It also passed the competition-primary known/public-opponent outcome gate with 96/96 wins and zero outcome regressions.

However the known-opponent artifact exposed a large money-margin weakness against `starter` on formal-known seeds despite W→W outcomes:

- seed642: `feed0 - safety-v3` margin = `-19279`
- seed643: `feed0 - safety-v3` margin = `-16354`
- formal-known starter mean margin delta = `-8906.5`

Because a future stronger opponent can make margin compression matter, removing the reserve unconditionally is treated as a robustness concern rather than automatically promoted.

Prior CARROT2 trace also showed the opposite problem in focal seed641: the parent one-day reserve blocks CARROT conversion when current WHEAT is only about `3–9` versus planned next-day feed need around `17–19`, even while substantial standing WHEAT yield remains scheduled for harvest. This suggests the reserve is useful, but its current-stock-only implementation is overconservative.

## Hypothesis

Keep `_CA_FEED_DAYS = 1`, but when the old current-stock test would block a CARROT swap, credit only WHEAT from existing plots that the route actually schedules to harvest inside the same one-day horizon.

Simulate the horizon chronologically and require WHEAT stock to remain nonnegative at every planned FEED event. For conservatism, a harvest occurring on the same step as FEED is credited only after that step's FEED demand, avoiding reliance on Kaggriculture intra-step processing order.

Expected behavior:

- retain the parent reserve when no near-term harvest can fund feed;
- relax false feed blocks like the observed seed641 pattern;
- avoid the blanket-risk profile of feed0;
- preserve attribution to the CARROT2 feed-reserve mechanism.

## Changes

One tactical concept with telemetry:

1. add `_ca_wheat_feed_safe(...)` to project scheduled WHEAT harvest credit through the next `_CA_FEED_DAYS` horizon;
2. invoke it only after the original current-stock test fails;
3. add `ca_feed_harvest_credit` telemetry counter.

No global feed-days constant change; `_CA_FEED_DAYS` remains `1`.

## Static / syntax

The exact formal safety-v3 `main.py` was recovered from formal preflight run `36247002100`, artifact `10908718544`; recovered `main.py` SHA256 matches the formal champion exactly.

The candidate was generated from that exact parent and locally checked:

- candidate SHA256 = `56736e406f6cc023b0b720bd1b7aee556ed7aba4caa92a9ba427336cb047a95f`
- Python `py_compile` = **PASS**
- unified diff confined to CARROT2 report/helper/reset/feed-gate code

The repo builder independently asserts both parent and candidate SHA before writing output.

## Burned dev evaluation

Workflow: `.github/workflows/uploaded-127ed3-ca-harvestcredit-v1-dev.yml`

Run: `36297870476`

Seeds, both seats:

`641,350003,101,211,347,509,733,911,1201,1601`

The workflow directly checks final `env.state` statuses rather than using the known `scripts/eval.py` scalar-status serialization bug. It records:

- pair deltas and W/L/D;
- mean / median / SE / mean-2SE / worst / best;
- seat0 / seat1 means;
- exceptions / non-DONE / 720-turn completion;
- `ca_feed_harvest_credit` counts and full candidate/parent CARROT2 reports.

Status at log creation: **queued; self-hosted runner unavailable/offline after the completed known-opponent run**.

## Decision rule

Do not consume stress or fresh sealed seeds from this candidate until burned dev is positive enough to justify continuation. In particular, verify that:

- seed641 and/or 350003 retain useful improvement;
- known small-regression seeds do not worsen materially;
- the harvest-credit telemetry actually fires on improved games;
- runtime remains plausible before any larger evaluation.

If burned dev is weak or negative, REJECT without stress/sealed evaluation.
