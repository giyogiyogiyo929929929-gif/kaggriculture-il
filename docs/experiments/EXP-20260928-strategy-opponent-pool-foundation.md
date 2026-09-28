# EXP-20260928 — public replay strategy clusters and opponent-pool foundation

## Status

Implemented on branch `analysis-strategy-pool-20260928`; formal champion is unchanged.

Formal champion at experiment start: v153, SHA256 `128836e8e945d9b5b8c6776dc68cd45f4c21775713ebd3bd50655cd2f711ebfd` (`EXP-20260927-v153-PROMOTE.md`).

## Goal

Build the first five stages of the proposed training/evaluation pipeline without changing agent behavior:

1. collect public replays;
2. cluster observed agents by strategy;
3. select one representative per strategy cluster for an Opponent Pool;
4. run all representative pairs on a common seed panel with seat swap;
5. emit a Matchup Matrix that can later drive hard/close-opponent oversampling.

## Reused infrastructure

Stage 1 is not reimplemented. `scripts/fetch_replays.py` already:

- fetches leaderboard teams and their public submissions/episodes through Kaggle CLI;
- excludes validation/incomplete episodes;
- resumes through `data/meta/manifest.json`;
- digests each ~33 MB replay to `data/digest/*.json.gz` through `scripts/digest_replay.py`;
- deletes raw replays by default after successful digesting.

The existing `scripts/analysis/round_robin.py` remains useful for the archived-agent exploratory tournament, but its one deterministic seed per pair is not sufficient for the strategy Matchup Matrix because matrix cells should use the same matched seed panel.

## New: `scripts/analysis/strategy_cluster.py`

### Identity

Profiles are grouped by `team_id:submission_id` when the replay manifest contains a submission ID. This avoids intentionally merging different submissions from the same team. If the manifest is incomplete, the fallback is the team identity plus `unknown` submission.

### Features

The clustering deliberately excludes final money / win result so the geometry represents behavior rather than strength. Per-game features include:

- unit-action rates: PLANT, WATER, HARVEST, FERTILIZE, FEED, CARE, COLLECT_FERTILIZER, BUILD_COOP, BUILD_PASTURE, DIG, PASS;
- market-order rates: BUY_SEED, BUY_ANIMAL, BUY_PRODUCT, SELL, HIRE, BUY_LAND;
- total SELL volume (log), first SELL turn, day 25+ liquidation share;
- per-item SELL shares;
- same-turn SELL collision share and 1–2 step reactive SELL share;
- total hires (log), land purchases, first land-unlock day, first animal day;
- final quadrants, crop composition and animal composition (log counts).

Episode features are averaged over the submission profile. Numeric features are z-standardized before clustering.

### Clustering

A deterministic k-means implementation is used so this analysis has no new sklearn dependency. If `--k` is omitted, k=2..`--max-k` is tried and the best mean silhouette score is selected. Each cluster representative is the observed profile closest to the cluster centroid. Cluster output includes the six largest absolute centroid z-features for interpretation.

### Opponent Pool safety gate

A public replay identifies observed behavior, not necessarily the exact local code. Therefore a cluster representative is admitted to the executable Opponent Pool only through an explicit mapping:

```json
{
  "TEAM_ID:SUBMISSION_ID": {
    "path": "opponents/example/main.py",
    "verified": true,
    "sha256": "...",
    "evidence": "fingerprint_exact"
  }
}
```

The path must exist and the SHA must match. Unmapped representatives remain in `unresolved` instead of silently substituting a similarly named agent. This is intended to pair with existing replay fingerprint analysis.

Outputs:

- `data/analysis/strategy_pool/clusters.json`
- `data/analysis/strategy_pool/opponent_pool.json`
- `data/analysis/strategy_pool/summary.md`

Example:

```cmd
.venv\Scripts\python.exe scripts\analysis\strategy_cluster.py --min-games 2 --max-k 8 --agent-map data\analysis\strategy_pool\agent_map.json
```

## New: `scripts/analysis/matchup_matrix.py`

The matrix runner consumes only resolved cluster representatives. Additional champion/checkpoint agents can be included as `--extra-agent NAME=PATH` without changing the pool file.

For every unordered pair:

- the identical seed range is used;
- `scripts/eval.py` supplies the existing same-seed seat swap;
- the result ledger is append-only/resumable;
- every agent source is SHA-checked before evaluation;
- directed cells invert wins/losses and `pair_diff_mean` correctly;
- outputs include win-rate matrix and pair-diff matrix.

`--seed-start` is deliberately required. There is no implicit seed range, so reserved sealed-test seeds cannot be burned accidentally by a default.

Example exploratory run:

```cmd
.venv\Scripts\python.exe scripts\analysis\matchup_matrix.py ^
  --seed-start <EXPLICIT_BURNED_SEED_START> --seeds 8 -j 1 ^
  --extra-agent champion=submissions\<exact-v153-path>\main.py
```

Outputs:

- `manifest.json` — exact agent SHA list and seed panel;
- `results.jsonl` — durable pair ledger;
- `matrix.json` — directed cells plus per-agent mean/worst win rate;
- `win_rate.csv`;
- `pair_diff.csv`.

## Tests

Added:

- `tests/test_strategy_cluster.py`
  - replay feature extraction separates a late WOOL seller from a crop/land-expansion seat;
  - two synthetic strategy clouds separate deterministically;
  - Opponent Pool refuses a bad SHA.
- `tests/test_matchup_matrix.py`
  - matrix direction correctly inverts win rate and pair diff;
  - pair keys are independent of A/B argument order and bind the seed panel;
  - weakness summary uses available matchup cells.

## Decision

KEEP AS ANALYSIS INFRASTRUCTURE. This experiment does not alter or promote the agent.

The next evidence-producing run should be:

1. refresh public replay digests;
2. generate current strategy clusters;
3. fingerprint/resolve cluster representatives to audited local agents;
4. add exact v153 as an extra matrix participant;
5. run one common exploratory seed panel with both seats;
6. identify clusters where v153 is weak or near 50%;
7. only then design a small candidate or sampling policy for IL/RL.

Do not use future sealed seeds for the matrix. Do not treat cluster labels as proof of code identity.
