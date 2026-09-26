# Handover — uploaded 127ed3 evaluation — 2026-09-26

This file is the current handover for branch `eval-uploaded-127ed3-20260926`. The older `docs/handover.md` contains historical v12–v25-era context and must not be used to override the newer champion record.

## Current formal champion

- `v147_candidate_confirmed_v111_clone.py`
- SHA256 `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- engine `kaggle-environments==1.32.7`
- engine source SHA256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- promotion record: `docs/experiments/v147_PROMOTE_20260926.md`

Do not infer champion from version numbers or the uploaded candidate.

## Uploaded candidate

- source `/mnt/data/main.py`
- SHA256 `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- exact GitHub transport `ci/uploaded_127ed3/part00.b64` ... `part11.b64`
- role: candidate only
- static AST / py_compile: PASS
- raw formal dev H2H vs v147, 10 burned seeds both seats: **8W/2L/0D, mean +688.5, median +392, worst -520, best +3428, seat means equal, exceptions0**
- losing seeds: 641 (-406), 350003 (-520)
- large positive seed: 733 (+3428)
- raw malformed-observation preflight regresses vs v147, so raw bytes are not promotion-eligible

## Mechanism findings

- generic Chassis `sell_lead=True`
- generic `front_run`, `budget_guard`, `room_guard`, `dead_stock`, `terminal_liquidation` are disabled
- generic front-run telemetry is zero on the four diagnostic contrast seeds
- current race/copy machinery is active; do not reuse the old claim that race is dormant
- FLOWPX direct action fires are zero on the four diagnostic seeds
- STRAWBERRY net market contribution is positive on all four contrast seeds
- WHEAT weakness is mostly quantity / crop-mix / purchasing chronology, not worse average SELL price; candidate realizes a higher mean WHEAT SELL unit price but sells fewer units
- CARROT2 swaps: 46 / 29 / 22 / 0 on seeds 641 / 350003 / 733 / 911
- CARROT2 cannot simply be removed: seed733 has CARROT +2324 and total +3428
- all four diagnostic games finish with zero shed for both agents; no simple endgame leftover-inventory bug
- seed733 shows that delaying WOOL liquidation can be favorable, so endgame changes must be item/order-aware

## Completed focused experiments

### IG/MG tail ablation

Run `36233707730`, formal 1.32.7. Full raw, no-IG, and no-MG+IG are identical on seeds 641/350003/733/911: -406, -520, +3428, +1178. Stop spending experiments here without new evidence.

### MPX shop-aware town draw

Candidate SHA `e2d48abbfff9c885cefe80d6b746ec54870341284117e1f8d5436a3393b7c490`; run `36232817779`, formal 1.32.7. Candidate vs raw on four diagnostic seeds both seats is 0W/0L/4D, all pair deltas 0, exceptions0. **REJECT / no demonstrated effect.** No sealed seeds consumed.

## Active candidates

### safety-v3

- expected SHA `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- tactical logic unchanged; final `ig_agent` wrapped with legal PASS fallback on unexpected exception
- workflow `.github/workflows/uploaded-127ed3-safe-v3.yml`
- run `36235154374`
- latest observed state: queued
- required result: malformed probes all legal and raw/safe exact valid-game equivalence on 641/350003/733/911 both seats

### CARROT2 conservative early margin

Hypothesis: `_CA_MARGIN=-20` permits economically marginal early WHEAT→CARROT substitutions. Preserve the later seed733 regime while making only step<540 conservative.

- change: step<540 margin 0; step>=540 retains -20
- parent SHA `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- candidate SHA `bad25166aa91712007af8a010f571dab5cf87873dc75f762f2e83b152849faad`
- builder `ci/build_uploaded_127ed3_ca_early_margin.py`
- local byte-preserving build + py_compile PASS
- workflow `.github/workflows/uploaded-127ed3-ca-early-margin.yml`
- run `36235967167`
- latest observed state: queued
- first test uses the ten already-burned dev seeds, candidate vs raw, both seats

## Promotion gates still missing

For any surviving uploaded-candidate variant: direct v147 same-seed both-seat H2H, acceptable worst regression, fresh sealed seeds, known-opponent regression, dedicated runtime, exceptions/timeouts check, and mechanism explanation. Required opponent panel includes `public_main_opponent.py`, `v134_candidate_center_nonsplit.py`, plus starter, beat_v48, bl_v20, bl_v21, farming_v2, and frontier_prvsiyan.

No uploaded-candidate variant is champion. No Kaggle submission has been performed.

## Next work

1. Consume safety-v3 and CARROT2 focused results when the formal runner executes them.
2. REJECT CARROT2 early-margin if it damages prior winning seeds or fails to improve the losing path; if positive vs raw, run direct candidate-v147 H2H rather than assuming transitivity.
3. If safety-v3 is valid-game equivalent, use it as the robustness base for any tactical survivor.
4. Only then run sealed / known-opponent / runtime promotion gates.
5. After the uploaded-candidate path is resolved, resume the ~24-turn h20/h24 counterfactual market simulation for EGG/MILK/STRAWBERRY/FERTILIZER and related items.

Detailed evidence is in `docs/experiments/uploaded_127ed3_eval_20260926.md`.
