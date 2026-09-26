# EXP-20260926 — v117_wheat_post_town_delay1

## Status

**KEEP TESTING — DO NOT PROMOTE**

Formal champion remains `v112_wheat_lead3_lowdemand`.

This is a sibling candidate of `v116_milk_micro_lead1`, built directly on v112. The two unpromoted mechanisms are intentionally not stacked. This experiment belongs only to the current v90→…→v112 lineage; do not mix it with the separate v130+ lineage and do not use v66 as a target.

## Parent / candidate

- champion / parent: `v112_wheat_lead3_lowdemand`
- candidate: `v117_wheat_post_town_delay1`
- canonical engine target: `kaggle_environments==1.32.7`
- sign: `candidate_minus_champion = candidate - champion`
- v112 SHA-256 assertion: `1c6e00ff0bd46b16189b1f6a93ce5e498ff8ffb5b0acb33591cdd247cd8b4771`
- v117 full-source SHA-256: pending successful builder execution; the builder prints it deterministically.

## Motivation

`v111` showed a concrete failure mode for overly aggressive WHEAT leading: in high-WHEAT-demand worlds, waiting through a Town-consumption tick can be better than selling one turn earlier. `v112` therefore kept lead3 only when the unlocked WHEAT-demanding shop count is at most 3.

v117 tests the reverse direction instead of widening the lead horizon again: in the high-demand regime where v112 refuses lead3, delay an untouched native WHEAT SELL by exactly one turn so deterministic Town consumption can reduce existing market inventory first and the delayed batch can sell in the post-consumption state.

This is consistent with the game processing order: market orders are processed before Town consumption, and price follows market inventory. It is also deliberately different from the already-successful same-turn Order Book Layer D; v117 changes the turn, not just the ordering of orders inside one turn.

## One main change

A native late-batch WHEAT SELL is delayed by one turn only when all of the following hold:

1. `step >= 300` and a next step exists;
2. the current static schedule contains a native WHEAT SELL and the post-v112 action contains exactly the same WHEAT SELL quantity;
3. no v112 WHEAT lead repayment is currently active into a future step;
4. unlocked WHEAT-demanding shop count is at least 4;
5. the current step is a deterministic WHEAT Town-demand tick;
6. current public WHEAT market inventory is positive, so Town has existing inventory to consume without relying on our delayed sale;
7. the current market action contains only SELL orders, avoiding same-turn cash-dependency changes;
8. the next static market action has at most 7 orders, leaving headroom for repayment;
9. there is no native WHEAT SELL at `step+2`, `step+3`, or `step+4`, preventing v112's lead1/2/3 logic from using the same held stock on the repayment turn.

On activation, v117 removes exactly the native WHEAT quantity from the current action and repays the same quantity at `step+1`. Repayment merges into an existing WHEAT SELL when possible; otherwise it inserts a WHEAT SELL before the first non-SELL order.

Any repayment shortfall is telemetry-visible and is a rejection condition.

## Observation-schema recheck

The public observation layout was rechecked against an existing agent whose engine notes were verified against `kaggle_environments==1.32.7`. It documents:

- `observation["market"] = {"inventory": {...}, "prices": {...}}`
- `observation["town"] = {"unlocked_shops": [...]}`

Therefore v117's `market.inventory.WHEAT` and Town-shop accesses are structurally consistent with the canonical observation schema. This check matters because a schema mismatch would otherwise look like a false no-activation via `market_empty_blocks`.

## Telemetry

`agent.telemetry["wheat_post_town_delay1"]` records:

- `shifts`
- `units`
- `market_empty_blocks`
- `low_demand_blocks`
- `cash_blocks`
- `next_slot_blocks`
- `parent_shift_blocks`
- `future_wheat_blocks`
- `repay_merges`
- `repay_inserts`
- `repay_shortfalls`
- `errors`
- up to 64 activation `steps`

## Static / focused checks

The suffix is stored as reviewable plaintext at:

`experiments/v112_v116_milk_micro/v117_suffix.pyfrag`

A focused dependency-free test is stored at:

`experiments/v112_v116_milk_micro/test_v117_suffix_synthetic.py`

The exact test was also run locally against the same suffix logic and passed the following cases:

- normal high-demand Town-tick delay → next-turn insert;
- repayment merge into an existing WHEAT SELL;
- low-demand world block;
- zero market-inventory block;
- same-turn BUY/cash-dependency block;
- next-turn market-slot pressure block;
- active parent WHEAT lead-state block;
- near-future native WHEAT block.

Result: `v117 synthetic checks: PASS`, with zero synthetic errors and no repayment shortfall in the activation cases.

During builder editing, a manual transcription error in the v112 SHA assertion was detected by review and corrected before any successful canonical run. It was a builder-check typo, not a candidate-code result. The exact v112 SHA assertion has been restored.

## Evaluator compatibility correction

Before any v117 result is accepted, both `run_v117_eval.py` and `run_v117_external_eval.py` were corrected to follow the project/Kaggle loader contract rather than assuming a symbol literally named `agent`:

- put the candidate/opponent file directory on `sys.path` while loading so sibling imports work;
- select the last callable value in the executed module namespace;
- retain Kaggle-compatible argument-count handling for timed calls;
- read telemetry from the resolved candidate callable.

The external runner also preflights all 10 opponent entrypoints with this loader before starting games. These are evaluator-infrastructure corrections only; v117 tactical logic is unchanged.

## Planned exact evaluation

`run_v117_eval.py` uses same-seed + seat-swap matched pairs and the project sign convention.

- validation: seeds `296001–296012`
- sealed: `297001–297004`
- stress: `298001–298008`
- starter: seeds `1–5`, both v117 and v112
- runtime pair: seed `800501`
- telemetry aggregated separately for validation / sealed / stress

The first decision gate is activation/safety, before score interpretation:

- `shifts == 0` → REJECT as no activation;
- `repay_shortfalls > 0` → REJECT;
- `errors > 0` → REJECT;
- otherwise inspect matched-pair W/L/D, mean, worst regression and activation concentration.

## Bronze external regression panel

`run_v117_external_eval.py` is prepared to compare v112 and v117 against the same 10 heterogeneous historical regression sentinels:

- `v49`
- `v50`
- `metav4_v13`
- `k256_h2_q_v1`
- `market_rhythm`
- `story_of_seasons`
- `thomas_router_93`
- `tetsutani_dpts_b`
- `jaxa_2802`
- `ready_stock`

Each agent/opponent comparison uses seeds `299001–299004` with seat swap. The report compares candidate and champion external pair differences on exactly the same opponent/seed, and explicitly counts W/D/L outcome regressions and improvements. This panel is retained because a previous broad-base candidate looked perfect against six top representatives yet regressed badly on this heterogeneous set, including a fatal JAXA regression.

The 2026-09-25 public-replay analysis adds a second bronze-specific interpretation rule: independent opponents that diverge within three turns, especially seat 1, are a local regression focus. It is not treated as causal evidence because the public matchup selection is confounded. New candidates are still judged with controlled same-seed seat-swapped evaluation.

Under the bronze-medal policy, even a positive v112 self-H2H is insufficient for promotion. A surviving candidate must pass this heterogeneous external panel without meaningful outcome regression, then receive any additional independent-style focused regression warranted by activation telemetry.

## Execution infrastructure

Canonical Linux workflow: `.github/workflows/v112-v117-current.yml`.

GitHub Actions run `36243943015` and the later current-candidate run `36244053506` both failed before any workflow step was created (`steps=null`). Earlier v116 Linux runs showed the same behavior on both `ubuntu-latest` and `ubuntu-22.04`.

A separate Windows hosted-runner diagnostic was created to distinguish Linux-image problems from wider Actions allocation problems. Run `36244088913` also failed before any step was created (`steps=null`). Therefore the hosted-runner block is wider than one OS image and is not evidence against v117.

A current-lineage self-hosted workflow, `.github/workflows/v112-v117-selfhosted.yml`, was then added using only the runner/environment pattern from the separate self-hosted experiment lineage; no v130+/v147 agent code or results are mixed into this lineage. It uses `[self-hosted, Windows, X64]`, Python 3.11 and verifies `kaggle_environments==1.32.7`. Its sequence is focused test → source reconstruction / py_compile → exact v117-v112 H2H → activation/safety gate → bronze external panel → artifact summary.

The workflow now has a dedicated concurrency group with `cancel-in-progress: true` so future pushes do not accumulate stale v117 evaluations after the runner resumes. Earlier queued runs created before that concurrency rule may still remain in the repository queue.

Latest self-hosted run for the concurrency-enabled workflow: `36245417246`, currently queued with no executed evaluation steps. This is not evaluation evidence and does not change the champion.

The local sandbox still does not contain `kaggle_environments`, and external package resolution is unavailable, so no canonical engine H2H numbers are fabricated or inferred.

## Decision

**KEEP TESTING. Formal champion remains v112.**

v117 is implementation-ready, focused-test clean, schema-checked, evaluator-compatible, and has a fixed exact + bronze external evaluation path. It cannot be promoted without real engine activation and matched-pair evidence. If it survives v112 H2H, external outcome stability is the next priority because the project is explicitly optimizing for robust bronze-medal performance rather than small self-play money gains.
