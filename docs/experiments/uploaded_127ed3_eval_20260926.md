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
- exact upload transport: `ci/uploaded_127ed3/part00.b64` ... `part11.b64`; formal workflows reconstruct and SHA-check exact bytes
- final uploaded callable tail: `ig_agent`
- generic Chassis settings: `sell_lead=True`; `front_run=False`, `budget_guard=False`, `room_guard=False`, `dead_stock=False`, `terminal_liquidation=False`
- later wrappers independently implement sale timing, overflow, endgame, inventory rescue and race/copy logic; code presence is not treated as firing evidence

## Formal dev H2H — raw uploaded vs v147

Actions run `36228521905`, seeds `641,350003,101,211,347,509,733,911,1201,1601`, both seats.

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

Summary: **8W/2L/0D**, mean **+688.5**, median **+392**, worst **-520**, best **+3428**, seat0 mean = seat1 mean = **+688.5**, exceptions0, non-DONE0. Candidate max game p99 11.7561 ms; worst observed candidate turn 268.3734 ms.

Raw decision: **KEEP TESTING**. It is tactically strong but fails malformed-observation preflight.

## Safety-v3 robustness layer — PASS

Raw candidate failed five malformed-observation probes (four `KeyError`, one `AttributeError`). Safety-v3 is deliberately separated from tactics: it wraps final `ig_agent`, deletes the stale `agent` binding so the Kaggle-like loader selects the wrapper, and returns legal PASS only on unexpected exception.

- SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- workflow: `.github/workflows/uploaded-127ed3-safe-v3.yml`
- Actions run: `36235154374`
- formal engine/source SHA checks: PASS
- five malformed probes: 5/5 legal PASS-shaped actions
- Kaggle-like selected callable: `agent`
- valid-game equivalence vs raw on seeds 641/350003/733/911, both seats: **8/8 exact final-money ties**
- exceptions0; non-DONE0
- max observed p99 13.8806 ms
- max observed single turn 241.0545 ms

Decision: **PASS as robustness-only layer**. This focused run is not the final dedicated runtime gate.

## Formal safety-v3 dev H2H vs v147 — PASS TO STRESS/RUNTIME

Actions run `36236548782`, job `108389259171`, exact `kaggle-environments==1.32.7`, exact engine-source SHA and exact candidate/champion SHA checks. Same ten already-burned dev seeds as the raw comparison, both seats.

Authoritative job-log values:

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

Summary: **8W/2L/0D**, mean **+688.5**, median **+392**, worst **-520**, best **+3428**, seat0 mean = seat1 mean = **+688.5**, exceptions0, non-DONE0. The tactical results exactly reproduce the raw uploaded candidate on all ten seeds. Malformed probes are all legal.

Runtime observed inside this broad H2H: max candidate p99 **19.7103 ms**, max single candidate turn **442.9083 ms**. The p99 is below the formal 50 ms threshold, but the isolated worst turn exceeds the v147 formal 200 ms threshold. This broad-H2H timing is not treated as the final runtime decision; a dedicated serial benchmark matching the v147 methodology is required.

Decision: **PASS TO BURNED STRESS + DEDICATED RUNTIME; KEEP TESTING overall**. Do not consume sealed seeds until these gates pass.

## Formal diagnostic / replay

Actions run `36230151111`, seeds `641,350003,733,911`, both seats.

### Active vs dormant mechanisms

Candidate seat0 telemetry:

- generic `front_run`: `front_turns=0` on all four — not an explanation of strength
- race/copy machinery: active; clone-like counts 217 / 476 / 282 / 458 and lost-race/escalation evidence nonzero
- `FLOWPX`: direct fires0 on all four because `_FX_FLOW_MIN=999`
- `ADV`: active, units 99 / 31 / 32 / 43
- `MPX`: active, units 68 / 45 / 100 / 56
- queue/order layers: active
- terminal helper: one small fire on seed911

### Item-level candidate-minus-champion net market deltas

| seed | WHEAT | CARROT | STRAWBERRY | EGG | MILK | WOOL | FERTILIZER | final |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 641 | -1722 | +1691 | +331 | +133 | -353 | -372 | -114 | -406 |
| 350003 | -1008 | +405 | +374 | +306 | -93 | -527 | +23 | -520 |
| 733 | -1472 | +2324 | +996 | 0 | +150 | +1926 | -729 | +3428 |
| 911 | +163 | -6 | +860 | 0 | +425 | -293 | +29 | +1178 |

STRAWBERRY is positive on all four. WOOL is unstable. Universal premium-product lead-sell is not justified.

### WHEAT: quantity, not realized SELL quote

Candidate mean realized WHEAT SELL price is higher than v147 on all four contrast seeds, but it sells fewer units:

| seed | cand avg sell | champ avg sell | cand sell qty | champ sell qty | WHEAT sell revenue delta |
|---:|---:|---:|---:|---:|---:|
| 641 | 38.67 | 37.57 | 229 | 276 | -1513 |
| 350003 | 43.09 | 42.56 | 1665 | 1706 | -852 |
| 733 | 37.02 | 35.93 | 333 | 415 | -2583 |
| 911 | 36.83 | 36.00 | 358 | 380 | -494 |

WHEAT BUY_PRODUCT is generally later / higher-priced in the candidate. Losing WHEAT paths are primarily crop mix / available quantity / purchasing chronology, not a simple one-turn SELL quote problem.

## CARROT2 analysis

`_CA_` / CARROT2 conditionally replaces planned WHEAT plants with CARROT. Telemetry `ca_swaps` on 641/350003/733/911: **46 / 29 / 22 / 0**.

Observed substitutions:
- seed641: material WHEAT→CARROT divergence starts step260; many early substitutions have immediate margin roughly -18 to -6 under `(3*CARROT-20) - (4*WHEAT-10)`
- seed350003: observed substitutions at steps453 and501, margins about -12 and -4
- seed733: material substitutions start step561; despite negative immediate margins, CARROT net revenue +2324 and pair +3428
- seed911: no material later substitution

### Conservative early CARROT2 margin — REJECT

Hypothesis: `_CA_MARGIN=-20` was too permissive early/mid game. Candidate changed only `step < 540` margin to `0`, preserving `-20` from step540 onward.

- parent SHA `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- candidate SHA `bad25166aa91712007af8a010f571dab5cf87873dc75f762f2e83b152849faad`
- builder `ci/build_uploaded_127ed3_ca_early_margin.py`
- workflow `.github/workflows/uploaded-127ed3-ca-early-margin.yml`
- Actions run `36235967167`, exact 1.32.7: SUCCESS

Candidate-minus-raw matched pair results on the ten already-burned dev seeds:

| seed | delta | result |
|---:|---:|:---:|
| 641 | -693 | L |
| 350003 | -222 | L |
| 101 | 0 | D |
| 211 | 0 | D |
| 347 | 0 | D |
| 509 | 0 | D |
| 733 | 0 | D |
| 911 | 0 | D |
| 1201 | -78 | L |
| 1601 | -127 | L |

Summary: **0W/4L/6D**, mean **-112**, median0, worst **-693**, best0, seat0 mean = seat1 mean = -112, exceptions0, non-DONE0. Max p99 13.4867 ms; max observed single turn 293.1944 ms.

Decision: **REJECT**. The stricter immediate-value filter produced no wins and four regressions, including making seed641 materially worse. Do not run direct v147 or sealed for this candidate. Mechanism inference: apparently marginal early CARROT swaps have downstream nonlinear value not captured by the immediate `(CARROT vs WHEAT)` price expression; do not repeat simple immediate-margin tightening.

### Behavior-identical CARROT2 trace — QUEUED

Because the broad immediate-margin guard regressed, the next CARROT2 work is instrumentation only, not another tactical change. Workflow `.github/workflows/uploaded-127ed3-carrot2-trace.yml`, Actions run `36238215853`, self-hosted runner. Contrast seeds 641/350003 (losses) and 733/911 (wins), both candidate seats. For each accepted WHEAT→CARROT swap it records step/day, WHEAT stock, one/two/three-day feed demand, expected WHEAT/CARROT units, prices, edge and spare-crop estimates. This run must not be used as evidence until completed.

## E402 finding

E402 activates late and uses route2 from step648 for WHEAT/CARROT planting demand. Replay does not support E402 as the late planting shortfall cause. Do not prioritize removal.

## Tail IG/MG ablation — no demonstrated effect

Run `36233707730`, exact1.32.7. Full raw, no-IG, and no-MG+IG are identical on 641/350003/733/911: -406, -520, +3428, +1178. Stop focused work here absent new evidence.

## MPX shop-aware town draw — REJECT

Candidate SHA `e2d48abbfff9c885cefe80d6b746ec54870341284117e1f8d5436a3393b7c490`; run `36232817779`, exact1.32.7. Candidate vs raw on 641/350003/733/911 both seats is **0W/0L/4D**, every pair delta0, exceptions0/non-DONE0. No demonstrated effect; no sealed seeds.

## Endgame finding

All four diagnostics finish with zero shed for both agents. There is no simple leftover-inventory liquidation failure. Seed733 is particularly important: v147 sells WOOL/WHEAT/FERTILIZER around 712–714, while raw delays a large WOOL sale until716 and still wins +3428. Blanket earlier liquidation is unsupported; endgame changes must be item/order/market-state-aware.

## Exact known-opponent assets

- exact `v134_candidate_center_nonsplit.py` recovered from the user's Library: SHA256 `693ca693378f8adae5d57642610ca682e43a03ad636be71141e1615a5e2d1edd`. A historical builder-derived v134 with a different SHA is **not** an acceptable substitute.
- `public_main_opponent.py`: exact named file not found in the user's Library search as of this record. Keep this regression slot unresolved rather than silently substituting another file.

## Current pending gates

### Burned stress + dedicated runtime

Workflow `.github/workflows/uploaded-127ed3-safe-v3-stress-runtime.yml`, Actions run `36237376092`, self-hosted Windows X64. Currently queued behind another repository self-hosted evaluation; no result is counted while queued.

- burned stress: seeds 621–632, both seats, safety-v3 vs exact v147
- dedicated runtime: same methodology as the v147 formal runtime benchmark — seeds 641/642, both seats, starter opponent, serial timing
- runtime acceptance thresholds: p99 < 50 ms, worst single turn < 200 ms, exceptions0

The branch does **not** spend a fresh sealed block unless burned stress preserves a multi-seed positive signal and the dedicated runtime gate passes.

## Current decision / next gates

- official champion remains **v147**
- raw uploaded: tactically strong but robustness-regressed
- safety-v3: current surviving uploaded candidate; exact SHA `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- formal safety-v3 dev H2H: **8W/2L/0D, mean +688.5, worst -520, both seats identical, exceptions0**, exact reproduction of raw tactics
- conservative early CARROT2: **REJECT**
- MPX shop-aware: **REJECT**
- IG/MG ablation: no demonstrated effect
- fresh sealed seeds consumed for safety-v3: **none**
- overall decision: **KEEP TESTING**
- no champion change and no Kaggle submission

Next order: (1) finish burned stress and dedicated runtime run `36237376092`; (2) only if both pass, allocate a genuinely unused sealed block and run safety-v3 vs v147 both seats; (3) inspect behavior-identical CARROT2 trace `36238215853` for a loss/win-separating condition before making any new CARROT2 candidate; (4) after sealed survival, run known-opponent regression using exact assets, including exact v134 and the v147 public panel. Keep `public_main_opponent.py` explicitly unresolved until the exact file is found.

After this uploaded-candidate path is resolved, resume the planned ~24-turn h20/h24 counterfactual market study for EGG/MILK/STRAWBERRY/FERTILIZER and related items.