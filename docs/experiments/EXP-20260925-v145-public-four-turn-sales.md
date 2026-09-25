# EXP-20260925: v145 public guarded four-turn sales

Status: EVALUATING

## Canonical state

- Formal Champion: `v115_champion_same_turn_open_squeeze.py`
- Champion SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- Never use v66.
- Formal engine: `kaggle_environments==1.32.7`.
- Metric: `candidate_minus_champion = candidate - champion`.

## Public source and evidence

Primary evidence source:

- Public notebook: `Kaggriculture V36 — Guarded Four-Turn Sales` by Ahmed Berat Ozer.
- Frozen tested source SHA256 reported by the notebook: `7eb5ab6c48581c82906ab6fa6b2cc5c9607513249ef59b2c45fcd6176e8653dd`.
- Frozen timestamp reported by the notebook: `2026-09-11T16:17:45.051569+00:00`.
- Archived public source: `5thDimension-Sean/kaggriculture-master/evidence/agents/ahmedberatozer__kaggriculture-v36-guarded-four-turn-sales.py`.
- The source distribution retains Apache-2.0 attribution/history for its public parents and Kaggle engine-derived semantics.

The V36 notebook states a single market-policy change relative to V35: from steps 288–695, physically available stock may satisfy an eligible scheduled sale up to four turns early while future-sale deductions, pickup protection, purchase barriers, shop/block boundaries and terminal protections remain.

Reported independent V36-vs-V35 evidence:

- 512 strong recorded opponents: V36 272/240 vs V35 249/263; paired outcome +4.492188pp; paired margin +447.205078; better/worse outcomes 23/0.
- 1,856 games against reacting public policies: V36 1784/72 vs V35 1683/117/56; paired outcome +3.933190pp; paired margin +446.059267; better/worse outcomes 101/0.
- The notebook states the source was frozen before qualification evaluation and no post-result threshold change or failed-game exclusion was used.

This evidence is not assumed to transfer to v115; it only justifies testing the mechanism.

## Candidate

- Candidate: `v145_candidate_public_four_turn_sales`
- Parent: exact formal v115
- Builder: `ci/build_v145_public_four_turn_sales.py`
- Major changes: 1

Instead of copying V36, modify only the existing exact-v115 R37 eligible-sale lookahead expression:

```text
base horizon = existing _R37_HORIZONS value
if 288 <= step < 696:
    horizon = max(base horizon, 4)
```

Then keep the existing R37 end caps and all surrounding exact-v115 guards unchanged.

Fail-closed conditions:

- exact v115 must contain exactly one audited R37 horizon expression;
- exact v115 must not already contain the public 288..695 four-turn override;
- otherwise candidate build aborts and this experiment is classified INAPPLICABLE rather than REJECT.

## Hypothesis

A four-turn horizon can move a scheduled SELL ahead of near-term competing supply while keeping inventory/purchase constraints intact. The public V36 evidence suggests this converts some losses without introducing observed outcome regressions in its own lineage. Because v115 already has market/race layers, interaction risk is material; direct and public matched panels are required.

Primary failure modes:

- selling one turn too early before favorable demand/price movement;
- interacting with V92 preemption and changing stock available to later wrappers;
- seed-specific gain with poor worst regression;
- changing only cash magnitude without flipping outcomes.

## Evaluation plan

1. Reconstruct exact v115 and verify SHA256.
2. Build v145; fail closed if R37 surface differs or mechanism already exists.
3. `py_compile` and byte-level verify that the only candidate source change is the local R37 horizon expression replacement.
4. Runtime/preflight smoke on seed 510013 with `-j 1`.
5. Direct v145 vs exact v115: seeds 510001..510012, both seats, 12 pairs / 24 games.
6. Public matched panel: seeds 510001..510004, both seats against starter, beat_v48, bl_v20, bl_v21, farming_v2 and frontier_prvsiyan.
7. If separation occurs, inspect every changed SELL: step, item, qty, original scheduled step, quote/price, market inventory before/after, gross revenue and downstream stock.
8. Give priority to loss->tie/win conversions, not large positive cash deltas in already-won games.
9. If no separation, do not horizon-threshold sweep. Close this transfer for v115 unless a new opponent family proves activation.
10. If positive without material regression, use a fresh unused stress set and only then allocate sealed seeds.

Seeds 510001..510013 become development-only once executed and may not be used for final sealed promotion evidence.

## Promotion rule

No automatic promotion from this screen. PROMOTE still requires independent fresh/stress/sealed matched evidence, both seats, acceptable worst regression, public-opponent safety, runtime acceptance, zero exceptions/timeouts and telemetry explaining the gain.
