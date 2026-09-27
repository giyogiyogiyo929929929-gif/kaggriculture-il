# v153 fresh sealed2 seed reservation

Status: PRECOMMITTED / RESULTS UNSEEN
Date: 2026-09-27
Candidate parent: `f4cd698383e293e0b819a2d6cf1b1fffe3e5f974` (`eval-v153-v147-dense-self-exposure-guard-20260927`)
Formal champion: `v147_candidate_confirmed_v111_clone.py`
Formal champion SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`

## Purpose

Freeze the exact fresh sealed2 seed set before any v153 sealed2 result is observed. These values must not be changed after evaluation starts.

## Deterministic generation

Namespace: `kaggriculture|v153|fresh-sealed2|2026-09-27`

For i = 0,1,...:

1. `digest = SHA256(f"{namespace}|{i}")`
2. read the first 8 digest bytes as unsigned big-endian integer `x`
3. `seed = 900000000 + (x % 500000000)`
4. skip duplicates; retain the first 12 unique values

## Frozen sealed2 seeds

1. 961200427
2. 1307503965
3. 1065712661
4. 1202442902
5. 949799007
6. 1206911468
7. 1103449975
8. 1059124859
9. 911799718
10. 1207510134
11. 1366430876
12. 1251623999

## Freshness audit before reservation

Each of the 12 exact decimal seed strings was queried individually against the GitHub repository code index before this reservation commit; all 12 returned zero matches. None overlaps the conservative used/reserved registry below.

This code-index check is supplemental, not proof of historical absence by itself. Freshness also relies on the explicit used/reserved evidence registry accumulated from experiment logs, workflow history, user-confirmed runs, and Safety-v3 reservation records.

## Conservative used/reserved exclusion registry

Explicit ranges / blocks excluded:

- 621-632
- 641-644
- 681-692
- 721-732
- 1701-1712
- 407001-408020 inclusive (conservative interpretation of the historical `407001-408020 blocks` note)
- 409001-409012
- 520101-520104

Explicit singleton exclusions:

- 101, 211, 347, 509, 733, 911, 1201, 1601, 350003

Safety-v3 fresh sealed1, confirmed by precommit + successful run 36239779345 + job log:

- 645491, 839835, 927489, 524295, 654541, 709211, 640183, 546018, 709378, 901935, 574041, 685514

Safety-v3 alternate deterministic reservation, excluded even though not the accepted fresh sealed1 set:

- 1568256014, 1883909388, 367317921, 458289146, 782863572, 202158583, 832110153, 63047626, 1574966926, 42399278, 1542138614, 407900870

Also excluded by the current handover / formal evaluation history: 621-624, 641-644, 681-692, 1701-1712, and 520101-520104 (already covered above).

## Evaluation lock

Sealed2 must use exactly these 12 seeds, both seats, matched by seed/seat, with `candidate_minus_champion = candidate - champion`. Record outcome transitions, mean/worst cash delta, seat dependence, seed dependence, exceptions, and timeout status. Do not replace a seed after seeing any result.
