# EXP-20260926 uploaded dbc709 candidate — static intake

Status: IN PROGRESS / NOT PROMOTED

## Identity

- uploaded filename: `main(1).py`
- byte size: `841471`
- SHA256: `dbc709febaef6b7b3f77ce8ee7dd2466548be0bd52763aa89905f61940f153b7`
- prior expected upload SHA: `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- identity decision: SHA mismatch, therefore treat as a new candidate
- reproducible local copy: `/mnt/data/candidate_dbc709.py`, same SHA
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
- synthetic terminal-planner no-op timing (not a formal runtime result): 0 hands median ~0.17 ms; 8 ~0.59 ms; 16 ~0.90 ms; 31 ~1.50 ms, all with zero simulations. A realistic accepted planner path still requires the formal runtime test.

## Active architecture identified so far

This is not a single chassis configuration. Later wrappers remain active after the base route/chassis. Explicit parent/wrapper chain includes at least:

`V219 -> R37 -> R85 -> R95 -> COURIER -> CARROT -> HERD -> FERT -> OPENING -> V92-P -> V92-Q -> RACE -> RACEPX -> RACEGATE -> CTRTABLE -> OVERFLOW -> ... -> CARROT2 -> ORDERPRI2 -> CAPHARV -> SHEDROOM -> HERD2 -> COWSWAP`

Important late layers:

- `ORDERPRI2`: reorders/sometimes pulls sales using estimated rival sellable stock and market movement.
- `CAPHARV`: harvests animal products when overnight capacity/holding would overflow.
- `SHEDROOM`: sells spare shed goods at hours 22/23 before end-of-day overflow, protecting near-term wheat/fertilizer needs.
- `HERD2`: goose/cow/sheep choice around the tape's goose purchase.
- `COWSWAP`: at the first cow purchase window (steps 144–191), conditionally substitutes geese for cows; only under a no-milk/no-yarn shop rule and an EV margin gate, then rewrites pasture/coop, pickup/place and credits/sells substituted production.
- a separate terminal wrapper is active at step >=718 even though the base chassis `terminal_liquidation` setting is disabled.

The earlier chassis `_SETTINGS` switches therefore do not describe the final policy by themselves.

## Main comparison hypotheses vs v147

1. `ORDERPRI2/RACE*`: highest-priority competitive hypothesis because it directly changes SELL order / pull-forward under the shared order book. This is the closest conceptual competitor to v147's confirmed second v111 reorder.
2. `CAPHARV/SHEDROOM/terminal planner`: potential robustness gain through overflow prevention and endgame cash realization.
3. `CARROT2/HERD2/COWSWAP`: potentially large production gains but likely the most seed/shop-dependent and therefore the most plausible regression source in the full candidate.
4. opponent-specific early `CTRTABLE` is a possible overfit/regression risk outside its two recognized rival fingerprints and should be isolated if the full candidate is competitive.

## Provenance/license audit

- Source explicitly credits Yusuke Hayashi Shop Router, Ahmed Berat Ozer, Dmitrii Gluzdov, Thomas Tschinkel, Kaggle/kaggle-environments contributors and additional public lineages.
- The embedded Kaggle unit-model block declares Apache-2.0 and records the exact official engine SHA `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`.
- Source comments state that `LICENSE.txt` is preserved and that no separate NOTICE was supplied for one upstream package.
- The uploaded standalone `main.py` does **not** contain the full Apache License text; it only references `LICENSE.txt`/`NOTICE.txt` (2/1 textual references found). Therefore a one-file submission package is not yet accepted as provenance-complete. Before any formal submission, package the applicable `LICENSE.txt` and any required NOTICE/attribution material in the submission tar.gz and audit the exact public-source chain.

## Evaluation state / blocker

No formal game result is recorded yet for this candidate. Sealed seeds 721–732 remain burned and must not be reused. Initial comparison must use burned dev/public seeds, both seats, against formal v147. Fresh sealed seeds will only be declared after the candidate shows promise.

The current chat sandbox cannot install `kaggle-environments==1.32.7` because outbound package/DNS access is unavailable. The GitHub self-hosted runner can reconstruct exact v147 and run the pinned engine, but the available GitHub connector exposes text-file writes only and cannot directly transfer the current 841,471-byte conversation attachment into the repository. This is an execution-transport limitation, not an agent failure. The evaluation branch has therefore been prepared, but matched games have not been claimed or fabricated.
