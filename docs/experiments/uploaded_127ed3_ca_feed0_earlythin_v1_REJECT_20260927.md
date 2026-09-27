# uploaded_127ed3_ca_feed0_earlythin_v1 — REJECT — 2026-09-27

## Identity

- formal champion / parent: `uploaded_127ed3_ca_feed0`
- parent SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- candidate: `uploaded_127ed3_ca_feed0_earlythin_v1`
- candidate SHA256: `e172cc82ff049766b9013a0a973817359d04349946544b1ba2091b552dc07c82`
- builder: `ci/build_uploaded_127ed3_ca_feed0_earlythin_v1.py`
- formal engine: `kaggle-environments==1.32.7`
- official source SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`

## Hypothesis

The known starter margin compression on seeds 642/643 begins at a shared first divergence at step256 with only five standing WHEAT plots. The candidate restores the old one-day feed-reserve veto only when `step < 300` and standing WHEAT plot count is `<= 5`, leaving later feed0 behavior unchanged.

## Focused evaluation

Formal self-hosted run: `36306499287`
Artifact: `10927603057` (`uploaded-127ed3-ca-feed0-earlythin-v1-focused`)

Known starter margins, candidate minus current champion:

- seed641: `0`
- seed642: `+9`
- seed643: `+105`
- seed644: `0`

Candidate minus previous safety-v3 on the compression cases remains:

- seed642: `-19270`
- seed643: `-16249`

Thus the large known compression is essentially unchanged.

Existing burned direct 10-seed block, candidate minus current champion:

- seeds: `641,350003,101,211,347,509,733,911,1201,1601`
- all 10 pair deltas: `0`
- W/L/D: `0/0/10`
- mean: `0`
- mean - 2SE: `0`
- worst: `0`
- exceptions: `0`
- all games reached `DONE` / 720 turns.

## Interpretation

The step256 WHEAT-to-CARROT substitutions on seeds642/643 are a reproducible first divergence but are not a major causal driver of the final `-19k/-16k` starter margin compression. Preventing that early/thin-WHEAT conversion changes final margin by only `+9/+105`.

This is consistent with the earlier `harvestcredit_v1` result: local modifications to the feed-reserve path do not recover most of the starter margin. The feed-reserve / early-WHEAT branch should therefore not be pursued further based only on this correlation.

## Decision

**REJECT.**

The predeclared focused gate required material repair of seeds642/643 before any stress or fresh/sealed allocation. That condition failed. Do not trigger the prepared 621-632 stress workflow for this candidate. No fresh seeds were consumed.

Formal champion remains `uploaded_127ed3_ca_feed0`.

## Next hypothesis

Do not infer causality from first divergence alone. If starter margin compression is investigated further, trace the later divergence cascade (especially day17 onward premium-crop / market-order differences) and require a separator that is not simply another feed-reserve proxy. Given that starter outcomes remain W->W with very large winning margins, outcome-oriented improvement work should take priority over optimizing this margin-only weakness.

No Kaggle submission is implied.
