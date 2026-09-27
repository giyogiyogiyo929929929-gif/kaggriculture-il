# uploaded 127ed3 CARROT2 harvest-credit v1 — pretest — 2026-09-27

Status: **CANDIDATE BUILT / BURNED DEV REQUEUED**

## Identity

- Formal parent/champion: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Candidate: `uploaded_127ed3_ca_harvestcredit_v1`
- Candidate SHA256: `ea296402b43b2e389e2f9cf8a23e27f92434b5b25212c3095f720840d9a91eb0`
- Builder: `ci/build_uploaded_127ed3_ca_harvestcredit_v1.py`
- Formal engine target: `kaggle-environments==1.32.7`
- Difference convention: `candidate_minus_champion = candidate - champion`

## Motivation

`uploaded_127ed3_ca_feed0` removes CARROT2's one-day WHEAT feed reserve globally and has positive direct-parent evidence. It passed the competition-primary known/public-opponent gate with 96/96 wins and zero outcome regressions, but formal-known starter margins compressed heavily: seed642 `-19279`, seed643 `-16354`, mean `-8906.5` candidate-minus-champion margin.

The completed same-observation divergence trace also confirms that feed0's behavioral changes start exactly where the parent reserve blocks WHEAT-to-CARROT substitutions. For example, seed641 first diverges at step323 and seed350003 at step656. This supports a narrower reserve correction rather than using firing-count correlation.

## Hypothesis

Keep `_CA_FEED_DAYS = 1`, but when the original current-stock reserve test would block a CARROT swap, credit only WHEAT from existing plots that the route actually schedules to harvest inside the same one-day horizon.

Simulate the horizon chronologically and require WHEAT stock to remain nonnegative at every planned FEED event. Same-step harvest is credited only after that step's FEED demand, so the condition does not rely on intra-step HARVEST/FEED processing order.

Expected behavior:

- preserve the reserve when no near-term WHEAT harvest can fund feed;
- relax false current-stock-only feed blocks;
- retain some feed0 gains while reducing blanket feed0 margin risk;
- keep attribution inside the CARROT2 feed-reserve mechanism.

## Changes

One tactical concept with telemetry:

1. add `_ca_wheat_feed_safe(...)` to project scheduled WHEAT harvest credit over the existing one-day horizon;
2. invoke it only after the original current-stock test fails;
3. add `ca_feed_harvest_credit` telemetry.

`_CA_FEED_DAYS` remains `1`.

## Static / syntax

The exact formal safety-v3 source was recovered from formal preflight run `36247002100`, artifact `10908718544`, and matches the champion SHA exactly.

The final candidate byte sequence was independently reconstructed from that CRLF source:

- candidate SHA256 = `ea296402b43b2e389e2f9cf8a23e27f92434b5b25212c3095f720840d9a91eb0`
- Python `py_compile` = **PASS**
- diff confined to CARROT2 report/helper/reset/feed-gate code

### Builder harness correction

Initial run `36297870476` did **not** evaluate the tactic. It failed during candidate construction with:

`report: expected exactly one match, got 0`

Cause: the formal safety-v3 source is CRLF, while the builder's multiline byte patterns were LF-only. The builder now detects and preserves the parent's newline convention before matching/replacing blocks. This changes the candidate byte SHA but not the intended tactical logic.

## Burned dev evaluation

Workflow: `.github/workflows/uploaded-127ed3-ca-harvestcredit-v1-dev.yml`

Corrected run: `36300251792`

Seeds, both seats:

`641,350003,101,211,347,509,733,911,1201,1601`

The workflow checks direct final `env.state` statuses and records:

- pair deltas and W/L/D;
- mean / median / SE / mean-2SE / worst / best;
- seat0 / seat1 means;
- exceptions / non-DONE / 720-turn completion;
- `ca_feed_harvest_credit` counts and full CARROT2 reports.

Status at this update: **queued**.

## Decision rule

Do not consume stress or fresh sealed seeds for this candidate until burned dev is positive enough to justify continuation. In particular:

- seed641 and/or 350003 should retain useful improvement;
- known small-regression seeds must not worsen materially;
- harvest-credit telemetry must fire on behavior-changing games;
- runtime must remain plausible before broader testing.

If burned dev is weak or negative, REJECT without stress/sealed evaluation.
