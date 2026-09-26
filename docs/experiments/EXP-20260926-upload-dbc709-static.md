# EXP-20260926 uploaded dbc709 candidate — static intake

Status: IN PROGRESS / NOT PROMOTED

## Identity

- uploaded filename: `main(1).py`
- byte size: `841471`
- SHA256: `dbc709febaef6b7b3f77ce8ee7dd2466548be0bd52763aa89905f61940f153b7`
- prior expected upload SHA: `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- identity decision: SHA mismatch, therefore treat as a new candidate
- current formal champion for this experiment: `v147_candidate_confirmed_v111_clone.py`
- formal champion SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- engine target: `kaggle_environments==1.32.7`
- metric convention: `candidate_minus_champion = candidate - champion`

## Static checks completed

- `python -m py_compile`: PASS
- stdlib load with `runpy.run_path`: PASS
- load time in current sandbox: about 0.08 s
- Kaggle-style last-callable inspection: final callable is `agent`, `co_argcount == 2`
- observation containing `step/player` but missing farm state falls back to PASS
- completely empty dict raises `KeyError('player')`; formal malformed-observation parity remains to be checked against the actual Kaggle-like preflight
- no requests/urllib/socket/subprocess/http imports found in the AST import list

## Active architecture identified so far

This is not a single chassis configuration. Later wrappers remain active after the base route/chassis. Explicit parent/wrapper chain includes at least:

`V219 -> R37 -> R85 -> R95 -> COURIER -> CARROT -> HERD -> FERT -> OPENING -> V92-P -> V92-Q -> RACE -> RACEPX -> RACEGATE -> ... -> CA -> ORDERPRI2 -> CAPHARV -> SHEDROOM -> HERD2 -> COWSWAP`

Important late layers:

- `ORDERPRI2`: reorders/sometimes pulls sales using estimated rival sellable stock.
- `CAPHARV`: harvests animal products when overnight capacity/holding would overflow.
- `SHEDROOM`: sells shed goods before end-of-day overflow.
- `HERD2`: goose/cow/sheep choice around the tape's goose purchase.
- `COWSWAP`: at the first cow purchase window (steps 144–191), conditionally substitutes geese for cows; only under a no-milk/no-yarn shop rule and an EV margin gate, then rewrites pasture/coop, pickup/place and credits/sells substituted production.

The earlier chassis `_SETTINGS` switches therefore do not describe the final policy by themselves.

## Provenance/license notes to finish

The source contains multiple public-agent lineage comments and Apache-2.0 notices, including Shop Router, Ahmed Berat Ozer, Dmitrii Gluzdov, thomastschinkel, prvsiyan, lucifer19 and Kaggle-engine-derived helpers. The final submission package must be audited for the referenced `LICENSE.txt` / NOTICE-equivalent and exact source provenance; presence of comments alone is not yet treated as a completed license audit.

## Evaluation state

No game result is recorded yet for this candidate. Sealed seeds 721–732 remain burned and must not be reused. Initial comparison must use burned dev/public seeds, both seats, against formal v147. Fresh sealed seeds will only be declared after the candidate shows promise.
