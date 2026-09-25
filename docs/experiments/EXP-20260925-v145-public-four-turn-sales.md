# EXP-20260925: v145 public guarded four-turn sales

Status: **INAPPLICABLE / ALREADY PRESENT IN CHAMPION**

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

## Proposed transfer

The proposed builder attempted to change only the existing exact-v115 R37 eligible-sale lookahead:

```text
base horizon = existing _R37_HORIZONS value
if 288 <= step < 696:
    horizon = max(base horizon, 4)
```

It was deliberately fail-closed if exact v115 already contained this public four-turn override.

## Result

Actions run: `36133205261`

Formal reconstruction reached exact Champion SHA:

`c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`

The builder then stopped before candidate creation with:

`exact v115 already appears to contain public four-turn override`

Therefore:

- no tactical candidate was produced;
- runtime/direct/public evaluation steps were correctly skipped;
- this is not a candidate loss or infrastructure failure;
- the strong public V36 mechanism is already part of exact v115;
- do not create another candidate by duplicating it;
- do not threshold-sweep 4/5/6-turn horizons without new telemetry showing a specific deficiency.

## Decision

**CLOSE AS ALREADY PRESENT.**

This public transfer successfully served as an audit: Champion already contains the guarded four-turn-sale idea that public V36 independently validated.

## Next hypothesis

Prioritize mechanisms absent from v115. The current strongest live local lead is the public room-guard candidate, which separated from v115 on direct matched seeds. Evaluate its negative/positive differential seeds with telemetry and then against a hard opponent panel before any sealed test.
