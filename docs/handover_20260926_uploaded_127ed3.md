# Handover — uploaded 127ed3 evaluation — 2026-09-26

This is the current handover for branch `eval-uploaded-127ed3-20260926`. The older `docs/handover.md` is historical v12–v25 context and must not override newer champion records.

## Current formal champion

- `v147_candidate_confirmed_v111_clone.py`
- SHA256 `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- formal engine `kaggle-environments==1.32.7`
- engine source SHA256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- promotion record `docs/experiments/v147_PROMOTE_20260926.md`

Do not infer champion from version numbers or the uploaded candidate.

## Uploaded raw candidate

- source `/mnt/data/main.py`
- SHA256 `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- exact GitHub transport `ci/uploaded_127ed3/part00.b64` ... `part11.b64`
- static AST / py_compile PASS
- formal dev H2H vs v147, 10 burned seeds, both seats: **8W/2L/0D, mean +688.5, median +392, worst -520, best +3428, seat means equal, exceptions0**
- losses: seed641 -406, seed350003 -520
- raw malformed-observation preflight fails, so raw bytes are not promotion-eligible

## Mechanism findings

- generic Chassis: `sell_lead=True`; `front_run=False`, `budget_guard=False`, `room_guard=False`, `dead_stock=False`, `terminal_liquidation=False`
- generic front-run telemetry is zero on the four diagnostic contrast seeds
- current race/copy machinery is active; do not reuse the historical claim that race is dormant
- FLOWPX direct action fires are zero on the four diagnostic seeds
- STRAWBERRY net market contribution is positive on all four contrast seeds
- WHEAT weakness is quantity / crop-mix / purchase chronology rather than realized SELL quote; candidate gets higher average WHEAT SELL price but sells fewer units
- CARROT2 swaps on 641/350003/733/911: 46 / 29 / 22 / 0
- global CARROT2 deletion is unsupported because seed733 gets CARROT +2324 and total +3428
- all four diagnostics end with zero shed for both agents; no simple liquidation omission
- seed733 shows later WOOL liquidation can be favorable, so endgame changes must remain item/order/market-state-aware

## Completed focused experiments

### Safety-v3 — PASS as robustness layer

- SHA256 `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- run `36235154374`, formal1.32.7: SUCCESS
- all five malformed-observation probes return legal PASS-shaped actions
- Kaggle-like loader selects `agent`
- raw vs safety-v3 exact final-money ties on 641/350003/733/911 both seats: 8/8 ties
- exceptions0, non-DONE0
- max p99 13.8806 ms; max single turn 241.0545 ms
- focused validation is not the final dedicated runtime gate

This fixes the raw robustness regression without demonstrated valid-game tactical change. Safety-v3 is the current surviving uploaded candidate base.

### Conservative early CARROT2 margin — REJECT

- candidate SHA `bad25166aa91712007af8a010f571dab5cf87873dc75f762f2e83b152849faad`
- change: step<540 margin 0 instead of -20; step>=540 unchanged
- run `36235967167`, formal1.32.7: SUCCESS
- candidate-minus-raw on ten burned dev seeds: 641 -693, 350003 -222, 101 0, 211 0, 347 0, 509 0, 733 0, 911 0, 1201 -78, 1601 -127
- **0W/4L/6D, mean -112, median0, worst -693, best0, seat means both -112, exceptions0**
- decision: **REJECT**; no direct v147 and no sealed test

Immediate-value CARROT-vs-WHEAT margin is not an adequate proxy for downstream value. Do not repeat simple early margin tightening without a richer counterfactual.

### IG/MG tail ablation

Run `36233707730`, formal1.32.7. Full raw, no-IG, and no-MG+IG are identical on 641/350003/733/911: -406, -520, +3428, +1178. No demonstrated causal effect on this panel.

### MPX shop-aware town draw — REJECT

Candidate SHA `e2d48abbfff9c885cefe80d6b746ec54870341284117e1f8d5436a3393b7c490`; run `36232817779`, formal1.32.7. Candidate vs raw on 641/350003/733/911 both seats is 0W/0L/4D, every pair delta0, exceptions0. No demonstrated effect; no sealed seeds.

## Promotion gates still missing

For safety-v3: direct v147 same-seed both-seat H2H over all ten burned dev seeds, acceptable worst regression, fresh sealed seeds, known-opponent regression, dedicated runtime, exceptions/timeouts check, and mechanism explanation. Required opponent panel includes `public_main_opponent.py`, `v134_candidate_center_nonsplit.py`, plus starter, beat_v48, bl_v20, bl_v21, farming_v2, and frontier_prvsiyan. The two specifically named files are not yet resolved at ordinary paths on this eval branch; locate their exact historical/branch source before use rather than substituting a similarly named file.

No uploaded variant is champion. No Kaggle submission has been performed.

## Next work

1. Run safety-v3 directly against v147 on the full ten burned dev seeds, both seats.
2. If that direct test remains strong, allocate genuinely fresh sealed seeds and evaluate both seats.
3. Only a sealed survivor proceeds to exact historical opponent recovery, known-opponent regression, and dedicated runtime.
4. If safety-v3 fails promotion gates, champion remains v147.
5. After this path is resolved, resume the ~24-turn h20/h24 counterfactual market simulation for EGG/MILK/STRAWBERRY/FERTILIZER and related items.

Detailed evidence: `docs/experiments/uploaded_127ed3_eval_20260926.md`.
