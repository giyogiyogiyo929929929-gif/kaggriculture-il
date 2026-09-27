# uploaded 127ed3 CARROT2 feed0 — second sealed precommit — 2026-09-27

Status: **PRECOMMITTED — DO NOT INSPECT/REPLACE SEEDS BASED ON RESULTS**

## Candidate identity

- Candidate: `uploaded_127ed3_ca_feed0`
- Candidate SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- Formal parent/champion at precommit: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Formal engine: `kaggle-environments==1.32.7`
- Difference convention: `candidate_minus_champion = candidate - champion`

## Why a second sealed block is justified

The first precommitted fresh block was directionally positive but tie-heavy (`2W / 1L / 9D`, mean `+28.1667`, worst `-38`). Across all 34 distinct dev/stress/first-sealed seeds available before this precommit, feed0 is `10W / 4L / 20D`, mean `+35.4412`, with mean minus two standard errors approximately `+8.51` and worst `-38`.

A second untouched block is therefore precommitted before seeing any results, to test whether the small positive edge survives another independent sample rather than promoting from a tie-heavy first sealed block.

## Execution gate

**Do not run this block unless both conditions hold:**

1. feed0 vs current formal champion has zero outcome regressions on the established six known/public opponents over burned `621–624` and formal-known `641–644` blocks; and
2. the first sealed block's apparent `non_done=24` is confirmed as the known `scripts/eval.py` status-serialization bug by direct final-state verification (`DONE`, 720 turns, zero exceptions, exact reproduced money deltas).

If either condition fails materially, leave these seeds unused and evaluate/reject based on that failure first.

## Fresh seed list

Precommitted ordered seeds:

```text
323743
992353
766816
468935
311561
814751
325596
507226
602943
874235
479622
296115
```

Compact ordered representation used for the hash:

```text
[323743,992353,766816,468935,311561,814751,325596,507226,602943,874235,479622,296115]
```

SHA256 of that exact compact UTF-8 string:

`da7aeb107fa8dcf4501e196f813aa9ea5ce75059fc4a8d7dd2821d1286cf33b9`

A repository search before commit returned no occurrence of the complete seed set. This block is treated as fresh and must not be altered after any execution result is observed.

## Planned evaluation

If the execution gate opens:

- exact candidate and parent SHA reconstruction,
- exact formal engine/source SHA verification,
- all 12 seeds,
- both seats,
- matched pair aggregation,
- exceptions / final statuses / 720-turn completion,
- W/L/D, mean, median, SE, mean−2SE, worst/best, seat means,
- no seed replacement or selective rerun based on score.
