# uploaded 127ed3 CARROT2 feed0 — fresh sealed seed precommit — 2026-09-27

Status: **PRECOMMITTED, NOT YET RUN**

This seed set was committed while the burned stress run `36294326359` was still in progress. It must only be executed if that stress result passes the predefined continuation screen; otherwise these seeds remain unconsumed.

## Candidate / parent

- Candidate: `uploaded_127ed3_ca_feed0`
- Candidate SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- Formal parent/champion: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`

## Deterministic derivation

Label:

`uploaded_127ed3_ca_feed0_sealed_precommit_20260927_v1`

Take the first 8 bytes of `SHA256(label)` as a big-endian integer and initialize Python `random.Random` with it. Draw unique integers uniformly with `randint(100000, 999999)`, excluding all previously used canonical sealed seeds and the current burned/dev seed blocks, until 12 remain.

Derived RNG integer seed: `7835196988015558480`.

Precommitted fresh seeds, in order:

`446910, 885820, 619329, 999159, 438040, 240018, 833802, 418449, 899805, 893017, 955463, 986686`

SHA256 of the comma-separated seed list:

`7fcdac52798e5bcb00fe13d108c9324de5ab89f7ce909a0d9f17417e005bc456`

## Exclusions checked

The set excludes the earlier canonical sealed set:

`645491, 839835, 927489, 524295, 654541, 709211, 640183, 546018, 709378, 901935, 574041, 685514`

and excludes burned/current diagnostic seeds including `621–632`, `641`, `350003`, `101`, `211`, `347`, `509`, `733`, `911`, `1201`, `1601`.

## Execution gate

Do **not** run this sealed set unless burned stress remains meaningfully positive with no exception/non-DONE failures and no unacceptable worst regression. A failed/weak stress result ends the candidate without consuming these seeds.
