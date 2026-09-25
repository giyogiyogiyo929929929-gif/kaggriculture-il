# EXP-20260925 — v134 center nonsplit

- champion: `v121_champion_same_turn_unwind.py`
- parent candidate: `v133 center_only`
- candidate: `v134_candidate_center_nonsplit.py`
- decision: **KEEP TESTING**; do not promote yet

## Hypothesis

v133's only observed regression (`bl_v21`, seed 382002, matched pair `candidate_minus_champion=-2`) comes from partially splitting a same-item sale across the Town Center tick. At step 600, v121 sells MILK 2 while v133 sells MILK 1 even though the parent/native action already sells MILK 1. The withheld unit leaves MILK market inventory one lower. At step 602 the candidate world has MILK price 218 vs 217; the higher quote benefits both players. Candidate terminal cash is +1 vs v121, but the rival is +3, so relative margin is -2 in both seats.

## Change

One tactical change only: keep v133's Town-Center-only gate, but do not block an advanced sale when the parent action is already selling that same item now. This avoids partial same-item split sales while preserving center-tick holds for items not otherwise sold on the current turn.

## Static / synthetic

- v130 SHA256 `7a8e337b5651ba3bf0f805b588ba871ba1ad629f515e47bc4c42494862eacfa8`
- reconstructed v133 SHA256 `ff7e198954f3d0b1198184966e4ae76a16e0d344ca93cfccb30f99253c54ba65`
- v134 SHA256 `693ca693378f8adae5d57642610ca682e43a03ad636be71141e1615a5e2d1edd`
- syntax/compile PASS
- synthetic PASS: step600→601 MILK + native MILK sale does not block; no native same-item sale still blocks; no center tick does not block; item-local behavior preserved.

## Retained v133 evidence

Completed scout aggregate: 54 paired seeds, 10W / 1L / 43D, mean `candidate_minus_champion=+4.148`, SE `1.786`, `mean-2SE=+0.576`. Strong `farming_v2`, `farming_v2_b`, `first_in_line` were identical to v121. Only loss was `bl_v21 seed 382002=-2`.

Exact telemetry reproduced the -2 mechanism in both seats. First action divergence is step 600: candidate MILK 1 vs champion MILK 2. At step 601 candidate-world MILK inventory is one lower; at step 602 MILK price is 218 vs 217. Final own cash changes +1, rival cash +3, hence margin -2.

## Evaluation plan

1. focused `bl_v21 seed 382002`, both seats; v134 should remove the -2 branch.
2. preserve v133 positive seeds: bl16 382001-382006; bl21 382001/382004/382006; starter 382001/2/3/5/6; beat_v48 381003.
3. fresh weak/diverse matched seeds + seat swap.
4. strong regression: farming_v2, farming_v2_b, first_in_line.
5. unused sealed seeds.
6. single-process runtime: p99 <50ms, worst <200ms, exceptions 0.

## Infrastructure blocker

After earlier successful v133 jobs, new GitHub Actions jobs fail before runner assignment (`steps=[]`, `runner_id=0`), including a one-job telemetry workflow and a rerun. The latest 100 runs queried were failures while older runs in the repository include successful jobs. This is consistent with an account/repository Actions capacity or billing/minutes condition rather than candidate code failure, but the exact account-level cause is not exposed by the available repository API. Treat evaluation as queued, not failed.
