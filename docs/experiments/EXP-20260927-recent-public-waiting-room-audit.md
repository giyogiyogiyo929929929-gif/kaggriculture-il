# EXP-20260927 — recent public waiting-room audit

## Status

STATIC / RUNNER-FREE AUDIT. No game seed consumed. No agent candidate created. No Kaggle submission. Formal champion remains v147; v153 remains KEEP TESTING until the already-precommitted fresh sealed2 finishes.

Checked on 2026-09-27. New public Notebook/Agent research is restricted to material whose Kaggle UI reports publication or update within the previous seven days (cutoff 2026-09-20). Older notebooks are not newly adopted. Historical project audits remain usable only as history/dedup evidence.

## Why this audit exists

The single Windows self-hosted runner is occupied and the v153 fresh sealed2 run is queued. This audit deliberately performs work that does not compete for the runner and does not contaminate the frozen sealed2 seed set.

Existing dedup evidence remains binding:
- guarded four-turn sale reservation is already inherited in the v147 lineage;
- public room guard is HOLD / LOW PRIORITY;
- Sparse Shop Hybrid requires exact audited source before transfer;
- six-sheep / broad production expansion remains HOLD.

## Fresh public sources admitted by the seven-day rule

### 1. prvsiyan — `Kaggriculture Frontier | The Soil Remembers Rain`

Source: https://www.kaggle.com/code/prvsiyan/kaggriculture-frontier-the-soil-remembers-rain

Freshness observed: Kaggle UI reported 2d ago at audit time. Apache-2.0 is shown on the notebook page.

High-value reproducibility evidence visible in the current notebook logs:
- engine 1.32.7;
- exact public source SHA-256 `178ae0f727641cf4b618ebb98ade7aa1a1bed7517281aab9849de82a59d8ed3a`;
- source size 1,046,403 bytes;
- exact-source smoke with zero runtime errors;
- multiple A/B and sweep receipts, including a `Guard31` receipt;
- paired seed-block bootstrap reporting rather than only a leaderboard claim.

Decision: HIGH STATIC PRIORITY, SOURCE ACQUISITION PENDING. The public page/log proves there is an exact artifact worth auditing, but the currently accessible text does not expose enough of the strategy mechanism to justify an inferred transfer. Do not create a candidate from the label `Guard31` or from the reported result alone. Acquire the exact source/notebook output first, verify SHA/license, then decompose market/farm changes and compare them statically against v147/v153.

### 2. Aleksei Provorov — `Kaggricult-Man: Reverse-Engineering`

Source: https://www.kaggle.com/code/leoprovorov/kaggricult-man-reverse-engineering-part-1

Freshness observed: 2d ago. Apache-2.0 shown.

Most useful transferable idea is diagnostic rather than tactical. The author describes tracing realized cash, inventory, projected asset value, market behavior, and the exact point where policies diverge. This matches the project's requirement to explain wins/losses rather than only compare final cash.

Important caveat: a current comment reports a mismatch between the SHA expected by the build notebook and the attached agent dataset; the author acknowledged the publishing/update issue and said an update was forthcoming. Therefore do not import strategy source from this notebook until the exact artifact is reproducible.

Decision: ADOPT THE DIAGNOSTIC CONCEPT, NOT THE AGENT. The local repo already has ledger tooling, so improve post-processing around actual SELL execution rather than copy unreproducible public code.

### 3. Thomas Tschinkel — `The 2945 Farm: 96% vs the Top-10 Public Bots`

Source: https://www.kaggle.com/code/thomastschinkel/the-2945-farm-96-vs-the-top-10-public-bots

Freshness observed: 6d ago. Current log reports generated `main.py` size 856,428 bytes and SHA prefix `bfee70e9daae…`. The notebook depends on `Demand-Preserving Turn Sale Timing`.

Decision: MEDIUM-HIGH STATIC PRIORITY. This is directly adjacent to v153's market/SELL problem, so it is a strong dedup target. However only a SHA prefix and wrapper/log are visible in the current retrieval. Do not infer its sale-timing algorithm from the title. Acquire exact source, record full SHA/license, then check whether it changes SELL timing, SELL ordering, quantities, or reservation horizons already present in v147/v153.

### 4. haodou092 — `Kaggriculture | Harvest Ledger`

Source: https://www.kaggle.com/code/haodou092/notebookdb6965aa8e

Freshness observed: 1d ago. Version 54 is titled `Productive Idle Workers`; public/best score shown as 2684.2; Apache-2.0 shown.

Decision: SOURCE-REQUIRED / CAUTION. The project has already identified generic productive-WHEAT expansion as a weak hypothesis. Do not implement anything from the title. If exact source shows a narrow scheduling rule that converts otherwise-idle hands without perturbing the production route, it may deserve a focused candidate; if it is simply broader planting/production, close it as duplicate weak evidence.

### 5. Georgy Mamarin — `Kaggriculture | What 2600+ Farms Do Differently`

Source: https://www.kaggle.com/code/georgymamarin/kaggriculture-daily-replays-the-live-meta-report

Freshness observed: 20h ago (scheduled). Apache-2.0 shown. The current table of contents covers ladder state, strategy fingerprints, big-bank separation, shared market behavior, who-beats-whom, luck, and openings.

Decision: ANALYTICS / OPPONENT-SELECTION INPUT, not an agent transfer. Use it to refresh hard-opponent choice or identify repeated market fingerprints once the underlying current replay data can be inspected. Do not derive a tactical candidate from summary headings alone.

### 6. Igor Zharov — `Kaggriculture | Multi-Route Farming Agent`

Source: https://www.kaggle.com/code/flexonafft/kaggriculture-adaptive-replay-agent

Freshness observed: 5–6h ago, version 94; best score shown as 2767.3; Apache-2.0 shown.

Decision: LOW-MEDIUM TRANSFER PRIORITY. Broad route/classifier copying is already disallowed because it destroys causal attribution and can splice incompatible farm states. It can become a current opponent/reference, or a source of one small observable branch if exact code exposes a genuinely new mechanism absent from v147.

## Runner-free deliverable added in this branch

Added `scripts/analysis/sell_sequence_report.py`.

Purpose: consume the existing `ledger_match.py` pickle without rerunning an episode and print, for each selected step/player:
- actual successful SELL unit sequence in `_commit_unit` order;
- units and distinct sold items;
- gross SELL revenue;
- per-item quantity, gross revenue, average unit price;
- first and last realized unit price;
- realized first-to-last price drop.

This is particularly useful for v153 because the candidate's only tactic is reordering a dense leading SELL prefix. It gives a direct post-hoc view of whether changed ordering moved high-self-exposure items earlier and whether the realized unit-price path/gross revenue moved in the expected direction.

Static checks performed outside Actions:
- Python `py_compile`: PASS;
- CLI `--help`: PASS.

No `kaggle-environments` runtime was available in the analysis container, so no new game was run and no seed was consumed. The script is stdlib-only and post-processes existing pickle data.

## Next actions after sealed2 completes

If sealed2 is neutral/positive:
1. identify every seed/seat with nonzero candidate-minus-champion difference;
2. generate/reuse ledger match data only for consumed/known seeds, never spend a new sealed seed for diagnosis;
3. run `sell_sequence_report.py` over the changed steps;
4. attribute cash difference to item/step SELL ordering and realized prices;
5. combine with existing hard-panel and runtime evidence for the v153 promotion decision.

If sealed2 regresses:
1. isolate the regression seed/seat;
2. find first effective SELL-order divergence;
3. inspect the realized price sequence and gross delta at that step;
4. derive at most one gating refinement from the replay (for example a step-window exclusion only if the regression evidence actually supports it);
5. do not jump to an unrelated public transfer.

## Candidate backlog from this audit

No candidate is authorized yet. Priority order for future static acquisition is:
1. exact current `Soil Remembers Rain` source by published SHA;
2. exact `The 2945 Farm` / Demand-Preserving Turn Sale Timing source for v153 dedup;
3. Harvest Ledger V54 exact source to decide whether `Productive Idle Workers` is scheduling or generic production expansion;
4. current meta-report data for hard-opponent/fingerprint refresh;
5. Multi-Route only as opponent/reference unless a single narrow mechanism can be isolated.

This backlog consumes no runner capacity and does not alter the frozen v153 sealed2 evaluation.
