# KAGGRICULTURE_CHAT_MODE_v115_r6.md

## 1. Canonical state

- Formal Champion: `v115_champion_same_turn_open_squeeze.py`
- Champion SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- Never use v66.
- Do not substitute old `main.py`, the mirror-day28 v115 branch, v119, v121, or another lineage for the formal Champion.
- Protect v115. Never edit the Champion directly.
- Candidate promotion is the only event that may change the formal Champion.

## 2. Evaluation contract

Use official `kaggle_environments==1.32.7` / `kaggriculture` as the standard environment.

Always normalize reported differences as:

```text
candidate_minus_champion = candidate - champion
```

Evaluation sequence:

```text
hypothesis
-> 1-3 change candidate
-> syntax / runtime
-> matched seeds + both seats
-> telemetry / failure-world analysis
-> fresh validation / stress
-> completely fresh sealed
-> promotion decision
```

Do not promote from averages alone. Check worst regression, seat dependence, seed sensitivity and exceptions. Never relax an acceptance gate after seeing results. Development seeds must not be reused for final sealed.

## 3. Current closed families

### live-herd

v129 sealed 201..280:

```text
0W / 1L / 79T
mean -33.3125
SE 33.3125
worst -2665 seed216
exceptions 0
```

The family is closed. Do not continue ratio/demand threshold tuning.

### dormant execution surfaces

The following candidates were exact-v115 derivatives but their target mechanism did not activate in the tested panels:

- v130 advanced-sale quote ordering
- v136 preguard quote ordering
- v137 courier insertion-order fix

All produced exact ties on direct/public panels and zero relevant activation telemetry. Do not repeat these candidates unless new telemetry proves activation under a materially different opponent family.

## 4. Telemetry-first rule

Before candidateizing another old wrapper/layer, first demonstrate that the target mechanism fires in representative exact-v115 games. This avoids long evaluations of dormant code paths.

Diagnostic seeds 581..584 are development-only and permanently excluded from final sealed use.

Current diagnostic result:

- V92 PREDICT preempt is active in 40/40 tested public-opponent games.
- Multi-item V92 SELL turns occur against all five tested public opponents; maximum 3 items in a turn.
- KIL v52 preempt was inactive in the same diagnostic and should not be pursued now.

## 5. Current candidate

`v138_candidate_v92_quote_order`

Candidate SHA256:
`33d495561774c1379a0f66c6a863b344ae0249fe64e196fc208a15c53188438f`

Builder:
`ci/build_v138_v92_quote_order.py`

Single change:

- preserve V92 item selection, quantity, thresholds, horizon and market-capacity behavior;
- when V92 creates multiple same-turn preempt SELLs, order only that generated block by v115's existing `_r37_quote_priority`;
- leave single-item turns unchanged.

Current targeted run:
`36116242273`

Screen seeds:
- direct v138 vs exact v115: 601..612, both seats
- starter/public matched panel: 601..604, both seats

These are development seeds and cannot be final sealed seeds.

## 6. Immediate continuation logic

When resuming:

1. Read run `36116242273` first.
2. Normalize every result as candidate_minus_champion.
3. Record direct W/L/T, mean, SE, worst/best, seat0/seat1 and exceptions.
4. Record starter and each public-opponent matched delta.
5. Read telemetry: V92 activity, multi-item turns and actual `v138_order_changes`.
6. If any material regression appears, reject v138 and diagnose the first/largest loss world before making another candidate.
7. If order changes occur but all outcomes are ties, classify v138 as no separation; do not threshold-tune.
8. If v138 is clearly positive with no regression, move to new validation seeds not used above. Do not jump directly to promotion.
9. Only after independent validation/stress may a fresh sealed set be allocated.

## 7. Current status summary

```text
FORMAL CHAMPION:
v115_champion_same_turn_open_squeeze.py

CLOSED / REJECT:
v129 live herd
v130 advanced-sale order
v136 preguard order
v137 courier order

DIAGNOSTICALLY ACTIVE TARGET:
V92 PREDICT multi-item preempt SELL block

CURRENT CANDIDATE:
v138 V92 quote-order

CURRENT RUN:
36116242273
```
