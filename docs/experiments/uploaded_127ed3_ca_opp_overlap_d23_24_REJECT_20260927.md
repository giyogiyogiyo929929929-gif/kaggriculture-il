# uploaded 127ed3 CARROT2 opponent-overlap d23-24 — REJECT — 2026-09-27

Decision: **REJECT**

## Identity

- Formal parent/champion: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Candidate: `ca_opp_overlap_d23_24`
- Candidate SHA256: `7c77abad57f00db5c459fb3133cc55bda75218a2ebdf69916c252cc05dba835b`
- Formal engine: `kaggle-environments==1.32.7`
- Official source SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- Difference convention: `candidate_minus_champion = candidate - champion`

## Hypothesis

On days 23-24, suppress CARROT2 WHEAT->CARROT swaps only if the opponent already has a standing CARROT plot. The focal loss seeds appeared to overlap the opponent's CARROT production, while the large-win seed 733 initially appeared to create relatively uncontested CARROT supply.

## Change

One CARROT2 gate only: on days 23-24, require that the opponent has no standing CARROT crop before accepting the swap. Day 27 and all other CARROT2 windows remain unchanged.

## Evaluation

Actions run: `36293943821`

Artifact: `uploaded-127ed3-ca-opp-overlap-d23-24-dev`, artifact id `10923353176`.

Burned 10 seeds, both seats:

`641, 350003, 101, 211, 347, 509, 733, 911, 1201, 1601`

Money results:

- W/L/D = **4 / 3 / 3**
- mean = **+20.3**
- median = `0`
- SE = `54.0855`
- mean - 2SE = **-87.8711**
- worst = **-375**
- best = `+267`
- seat0 mean = `+20.3`
- seat1 mean = `+20.3`
- candidate exceptions = `0`
- parent exceptions = `0`
- all games reached 720 turns

Seed deltas:

| seed | candidate - parent |
|---:|---:|
| 641 | **-39** |
| 350003 | +165 |
| 101 | 0 |
| 211 | +158 |
| 347 | +40 |
| 509 | 0 |
| 733 | **-375** |
| 911 | 0 |
| 1201 | +267 |
| 1601 | -13 |

Both seat deltas were identical for every seed.

## Harness note

The workflow concluded failure because it treated a scalar `statuses="DONE"` value as an iterable and counted its characters, producing `non_done=20`. This is the same known instrumentation bug as the earlier swap-cap workflow. Money results, 720-turn completion, and exception counts are valid and are sufficient for the tactical decision. Future workflows must normalize string status to a one-element list before checking it.

## Interpretation

The hypothesized overlap separator is not robust. Although seed 350003 improves, seed 641 regresses and, critically, the already-strong seed 733 loses `375`. The mean is mildly positive only because of several unrelated positive seeds; uncertainty is large and worst regression is unacceptable.

Standing opponent CARROT is therefore not a safe standalone gate for CARROT2. Do not consume stress or sealed seeds on this candidate.

## Decision

**REJECT.** Formal champion remains `uploaded_127ed3_safety_v3`.
