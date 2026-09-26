# safety-v3 sealed block 1 — seed reservation

Reserved **before any sealed result was observed** on 2026-09-26.

Candidate: safety-v3, SHA256 `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
Champion: v147, SHA256 `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
Engine: `kaggle-environments==1.32.7`, kaggriculture source SHA256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`

## Frozen sealed seeds

`645491, 839835, 927489, 524295, 654541, 709211, 640183, 546018, 709378, 901935, 574041, 685514`

Generation rule, fixed before evaluation: for `i=0..11`, SHA256 of `kaggriculture|safety-v3|sealed-1|2026-09-26|{i}`, use the first four digest bytes as a big-endian integer, then `500000 + value % 450000` (increment only on duplicate; no duplicate occurred).

Before reservation, repository code search returned no matches for either six-seed group. These seeds intentionally avoid all explicitly burned blocks in the current evaluation history, including 621–632, 641/642, 721–732, 101/211/347/509/733/911/1201/1601, 350003, and the unrelated 407001–408020 blocks.

This file is the precommit. Do not change the seed list after seeing results. Formal evaluation must use all 12 seeds, both seats, and report `candidate_minus_champion = candidate - champion`, W/L/D, mean, SE, mean-2SE, worst/best regression, seat means, exceptions and non-DONE counts.
