# uploaded 127ed3 feed0 starter-margin trace and earlythin-v1 hypothesis — 2026-09-27

Status: **TRACE COMPLETE; BYTE-PRESERVING EARLYTHIN-V1 FOCUSED TEST QUEUED**

## Formal champion

- `uploaded_127ed3_ca_feed0`
- SHA256 `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- previous champion / parent: `uploaded_127ed3_safety_v3`
- engine: `kaggle-environments==1.32.7`

## Starter margin trace

Run `36303683760`, artifact `10926957321`, known seeds only. Seed641 is the positive control; 642/643 are the known margin-compression cases. Both seats were traced against builtin starter, with feed0 and safety-v3 compared on the same observation for the first action divergence.

Pair margin deltas, feed0 minus safety-v3:

- seed641: `+7`
- seed642: `-19279`
- seed643: `-16354`

All trace errors: `0`.

### Shared first divergence on the damaging seeds

Seeds642 and643 first diverge at the same state:

- step `256` (day10)
- money `17043`
- WHEAT shed `4`
- crop counts: WHEAT `5`, STRAWBERRY `20`, MELON `2`
- CARROT2 `ca_min_wheat = 11`
- market quotes: WHEAT `31`, CARROT `41`, TOMATO `61`, STRAWBERRY `148`, MELON `226`

At this observation feed0 performs two WHEAT-to-CARROT substitutions, while safety-v3 increments `ca_feed_block` and keeps the two WHEAT plant actions. The two agents then enter different later market trajectories. The final margin loss is not just the immediate WHEAT/CARROT trade; it propagates into later premium-crop and animal-product sales.

### Separator versus known direct-parent gains

The earlier direct-parent divergence trace (`36295996084`) shows the clearly beneficial feed0 divergences starting later, at step323 or later, with a materially larger standing WHEAT base (roughly 8–23 WHEAT plots in the inspected gain cases). This separates the starter damage case from the main observed direct-parent gains better than a global feed-reserve restoration.

## Candidate: `uploaded_127ed3_ca_feed0_earlythin_v1`

Parent: current formal champion `uploaded_127ed3_ca_feed0`.

Formal byte-preserving candidate SHA256:

`e172cc82ff049766b9013a0a973817359d04349946544b1ba2091b552dc07c82`

Builder: `ci/build_uploaded_127ed3_ca_feed0_earlythin_v1.py`.

The initial builder used `read_text()` and therefore normalized the CRLF-heavy parent to LF. That produced SHA `d3cfbcbacb3530fc44e6db41fe7b336b00dcda6ae5823694869176de42711d9e`. That identity is **invalid for tactical evaluation** because its byte diff includes whole-file newline normalization. No result from that identity may be used as candidate evidence. The corrected builder operates on parent bytes and inserts only the intended guard while preserving all existing line endings.

### Single tactical change

Keep feed0 behavior by default, but when both conditions hold:

- `step < 300`
- current standing WHEAT plot count `<= 5`

restore the old one-day feed-reserve veto for the CARROT2 WHEAT-to-CARROT replacement. No other CARROT2 route, edge, cash, rescue, seed, liquidation, or market logic is changed.

Hypothesis: the large starter margin compression is caused by converting two of only five standing WHEAT plots before the farm's feed base is established. Reinstating the reserve only in this early/thin-WHEAT state should prevent seeds642/643's damaging divergence while preserving the later feed0 gains.

## Focused evaluation

The workflow is updated to assert the formal byte-preserving SHA before any game. No fresh seeds are used.

It checks:

1. starter seeds641–644, both seats, candidate/feed0/safety-v3 margins;
2. the existing burned dev 10-seed block, candidate minus current champion, both seats;
3. exceptions, DONE status, and 720-turn completion.

Decision gate before any fresh/sealed testing:

- candidate must materially repair 642/643 starter margin compression;
- it must not damage the 641 positive control materially;
- burned direct comparison versus feed0 must show no concerning regression signal.

If this focused gate fails, REJECT without consuming stress/fresh seeds. If it passes, proceed to the existing burned stress block 621–632 with seat swap before any sealed allocation.

No Kaggle submission is implied.
