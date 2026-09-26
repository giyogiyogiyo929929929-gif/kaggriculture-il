# uploaded 127ed3 evaluation — 2026-09-26

## Identity

- role: candidate only; never infer champion from this file
- uploaded source: `/mnt/data/main.py`
- uploaded SHA256: `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- formal champion: `v147_candidate_confirmed_v111_clone.py`
- champion SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- formal engine: `kaggle-environments==1.32.7`
- engine source SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- evaluation branch: `eval-uploaded-127ed3-20260926`

## Static / syntax

- local AST parse: PASS
- local `py_compile`: PASS
- exact upload transport: `ci/uploaded_127ed3/part00.b64` ... `part11.b64`; every formal workflow reconstructs and SHA-checks exact bytes
- final uploaded callable tail: `ig_agent`
- generic Chassis settings: `sell_lead=True`; `front_run=False`, `budget_guard=False`, `room_guard=False`, `dead_stock=False`, `terminal_liquidation=False`
- later wrappers independently implement sale timing, overflow, endgame, inventory rescue and race/copy logic; code presence is not treated as firing evidence

## Formal dev H2H — raw uploaded vs v147

Actions run: `36228521905` (`uploaded-127ed3-v147-dev`).

Seeds: `641, 350003, 101, 211, 347, 509, 733, 911, 1201, 1601`, both seats.

`candidate_minus_champion = candidate - champion`:

| seed | pair mean | result |
|---:|---:|:---:|
| 641 | -406 | L |
| 350003 | -520 | L |
| 101 | +467 | W |
| 211 | +593 | W |
| 347 | +317 | W |
| 509 | +292 | W |
| 733 | +3428 | W |
| 911 | +1178 | W |
| 1201 | +1283 | W |
| 1601 | +253 | W |

Summary:

- matched pairs: 10
- W/L/D: **8/2/0**
- mean: **+688.5**
- median: **+392**
- worst regression: **-520**
- best: **+3428**
- seat0 mean = seat1 mean = **+688.5**
- exceptions: 0
- non-DONE games: 0
- max candidate game p99: 11.7561 ms
- worst observed candidate turn: 268.3734 ms

Decision after raw dev H2H: **KEEP TESTING**. No PROMOTE.

## Robustness regression and safety-only candidate

Raw uploaded candidate fails the malformed-observation preflight: four `KeyError` failures plus one `AttributeError`; v147 handled the first four in the same probe. This is a real preflight regression, so raw uploaded bytes are not promotion-eligible.

Safety-v3 is deliberately separated from tactics. It wraps final `ig_agent`, deletes the stale `agent` binding so the Kaggle-like last-callable loader selects the wrapper, and returns legal PASS only on unexpected exception. Expected SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`.

Workflow: `.github/workflows/uploaded-127ed3-safe-v3.yml`, run `36235154374`. As of the latest check it is **queued** on the formal self-hosted Windows runner. Required gate: all malformed probes legal + raw/safe exact final-money equivalence on seeds 641/350003/733/911 both seats. Do not treat queued as passed.

## Formal diagnostic / replay

Actions run: `36230151111`, seeds `641, 350003, 733, 911`, both seats.

### Active vs dormant mechanisms

Candidate seat0 telemetry on the four contrast seeds:

- generic `front_run`: `front_turns=0` on all four — not an explanation of strength
- race/copy machinery: active; clone-like counts are 217 / 476 / 282 / 458 and lost-race/escalation evidence is nonzero
- `FLOWPX`: direct fires 0 on all four because `_FX_FLOW_MIN=999`; observation code exists but action layer is dormant here
- `ADV`: active, units 99 / 31 / 32 / 43
- `MPX`: active, units 68 / 45 / 100 / 56
- queue/order layers: active
- terminal helper: only one small fire on seed911 in this panel

Therefore the current raw agent's race machinery must not be described as dormant, but generic front-run and FLOWPX are not current causal candidates on these games.

### Item-level candidate-minus-champion net market deltas

| seed | WHEAT | CARROT | STRAWBERRY | EGG | MILK | WOOL | FERTILIZER | final |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 641 | -1722 | +1691 | +331 | +133 | -353 | -372 | -114 | -406 |
| 350003 | -1008 | +405 | +374 | +306 | -93 | -527 | +23 | -520 |
| 733 | -1472 | +2324 | +996 | 0 | +150 | +1926 | -729 | +3428 |
| 911 | +163 | -6 | +860 | 0 | +425 | -293 | +29 | +1178 |

STRAWBERRY is consistently positive on all four. WOOL is unstable. A universal premium-product lead-sell rule is not justified.

### WHEAT: quantity, not realized SELL quote, is the main weakness

The candidate's mean realized WHEAT SELL unit price is actually higher than v147 on all four contrast seeds, but it sells fewer units:

| seed | cand avg sell | champ avg sell | cand sell qty | champ sell qty | WHEAT sell revenue delta |
|---:|---:|---:|---:|---:|---:|
| 641 | 38.67 | 37.57 | 229 | 276 | -1513 |
| 350003 | 43.09 | 42.56 | 1665 | 1706 | -852 |
| 733 | 37.02 | 35.93 | 333 | 415 | -2583 |
| 911 | 36.83 | 36.00 | 358 | 380 | -494 |

WHEAT BUY_PRODUCT is also generally later / higher-priced in the candidate. Thus the losing WHEAT paths should be investigated as crop mix / available quantity / purchasing chronology, not as a simple one-turn quote problem.

## CARROT2 analysis

`_CA_` / CARROT2 conditionally replaces planned WHEAT plants with CARROT. Telemetry `ca_swaps` on seeds 641/350003/733/911 is **46 / 29 / 22 / 0**.

Observed candidate-v147 PLANT substitutions show:

- seed641: material WHEAT→CARROT divergence starts step260; many early substitutions have immediate value margin roughly -18 to -6 under `(3*CARROT-20) - (4*WHEAT-10)`
- seed350003: two observed substitutions at steps453 and501, margins about -12 and -4
- seed733: material substitutions start step561; despite negative immediate margins, CARROT net revenue is +2324 and the pair wins +3428
- seed911: no material later substitution

Consequently, deleting CARROT2 is not supported. It would remove a mechanism participating in seed733's large win.

### New focused candidate: conservative early CARROT2 margin

Hypothesis: the global `_CA_MARGIN=-20` is too permissive in the early/mid game. Constrain only `step < 540` to margin `0`, while preserving the existing `-20` behavior from step540 onward. This is one tactical change and intentionally preserves seed733's step561+ substitution regime.

- parent SHA: `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- candidate SHA: `bad25166aa91712007af8a010f571dab5cf87873dc75f762f2e83b152849faad`
- builder: `ci/build_uploaded_127ed3_ca_early_margin.py`
- byte-preserving local build: PASS
- local `py_compile`: PASS
- workflow: `.github/workflows/uploaded-127ed3-ca-early-margin.yml`
- first panel: the ten already-burned raw-v147 dev seeds, both seats, candidate vs raw parent
- run `36235967167`: **queued** at latest check

If it does not improve the two losing seeds without damaging the former wins, REJECT it. If it is positive vs raw, next gate is direct candidate-v147 matched H2H; do not infer transitivity.

## E402 finding

E402 activates late and uses route 2 from step648 for WHEAT/CARROT planting demand. Replay shows no late planting shortfall attributable to E402: seed641 divergence begins much earlier, seed350003 has only limited crop substitutions, seed733 divergence begins before E402, and seed911 is nearly identical. E402 removal is not the current priority.

## Tail IG/MG ablation — completed

Formal run `36233707730`, exact 1.32.7, seeds `641,350003,733,911`, both seats.

Compared full raw vs variants ending at `mg_agent` (no IG) and `e402_agent` (no MG+IG). All three variants produced the same matched results:

- 641: -406
- 350003: -520
- 733: +3428
- 911: +1178

Each variant: 2W/2L, mean +920, median +386, worst -520, best +3428, exceptions0. IG/MG are not causal for these selected outcome differences. Stop spending focused experiments on them unless new evidence appears.

## MPX shop-aware town draw — REJECT

Candidate SHA: `e2d48abbfff9c885cefe80d6b746ec54870341284117e1f8d5436a3393b7c490`.

Formal run `36232817779` succeeded under exact 1.32.7. On burned diagnostic seeds `641,350003,733,911`, both seats, candidate vs raw parent was **0W/0L/4D**, mean/median/worst/best all 0, exceptions0, non-DONE0. The proposed shop-aware MPX draw yielded no final-money effect on the intended contrast panel. **REJECT / no demonstrated effect; do not spend sealed seeds.**

## Endgame finding

All four diagnostic games finish with candidate and champion shed at zero; there is no simple leftover-inventory liquidation failure. Seed733 is especially important: v147 sells WOOL/WHEAT/FERTILIZER around steps712–714, while the raw candidate delays a large WOOL sale until step716 and still wins the pair by +3428. Therefore a blanket earlier-liquidation rule is not supported. Endgame work should remain item-, order-, and market-state-aware.

## Decision / next gates

- official champion remains **v147**
- raw uploaded candidate: **KEEP TESTING**, not promotable because malformed-input safety regressed and worst dev pair is -520
- safety-v3: **TESTING / queued**
- MPX shop-aware candidate: **REJECT — no demonstrated effect**
- IG/MG tail ablation: **no demonstrated causal effect on selected panel**
- CARROT2 early-margin candidate: **TESTING / queued**
- no fresh sealed seeds consumed for the uploaded-candidate branch yet
- no Kaggle submission performed

After safety-v3 and CARROT2 focused results: direct champion H2H for any surviving candidate, then fresh sealed seeds, known-opponent regression including `public_main_opponent.py`, `v134_candidate_center_nonsplit.py`, starter/beat_v48/bl_v20/bl_v21/farming_v2/frontier_prvsiyan, and dedicated runtime. Only then consider PROMOTE.

After this uploaded-candidate path is resolved, resume the planned ~24-turn h20/h24 counterfactual market study for EGG/MILK/STRAWBERRY/FERTILIZER and related items.
