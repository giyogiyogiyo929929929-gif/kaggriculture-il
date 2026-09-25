# KAGGRICULTURE_CHAT_MODE_v115_r7.md

## 1. Canonical state

- Formal Champion: `v115_champion_same_turn_open_squeeze.py`
- Champion SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- Never use v66.
- Do not substitute mirror-day28 v115, v119, v121, old `main.py`, or another lineage.
- Never edit the Champion directly. Only a fully gated PROMOTE may change it.

## 2. Evaluation contract

Formal engine: `kaggle_environments==1.32.7`.

Normalize all comparisons as:

`candidate_minus_champion = candidate - champion`

Use same seed + seat swap + matched pairs. mini-runner is not a formal evaluator. Do not promote from one seed or averages alone. Check worst regression, seat dependence, seed dependence, exceptions/timeouts, fresh stress, sealed seeds, key-opponent regression and runtime.

## 3. Closed / low-priority families

Do not restart these without new activation telemetry:

- v129 live-herd threshold family: closed after sealed catastrophic seed regression.
- v130 advanced-sale quote ordering: dormant in tested panels.
- v136 preguard quote ordering: dormant.
- v137 courier insertion order: dormant.
- v138 V92 multi-item ordering: activated but exact-v115 NO SEPARATION; closed.
- global V92 K=2 as in v139: REJECT due strong direct regression.
- KIL v52 retuning: low priority; representative diagnostics showed KIL inactive while primary V92 was active.

## 4. Key V92 findings

### v139

Global `_V92_P_K: 1 -> 2` affected primary V92 and KIL v52.

Direct exact-v115 seeds 621-632:

- 3W / 6L / 3T
- mean -107
- SE 58.37
- worst seed628 -662
- exceptions 0

REJECT.

### v140

Primary V92 K=2 only; KIL remains v115 K=1.

Direct exact-v115 seeds 641-652:

- 5W / 1L / 6T
- mean -0.5
- SE 3.644
- worst seed642 -38
- best seed651 +12
- exceptions 0

Do not promote; diagnostic value only.

Interpretation: the catastrophic v139 effect mostly came from changing the shared K and therefore KIL behavior. Primary V92 can be changed independently, but broad K=2 is not robust.

## 5. Telemetry discriminator

Successful v140 contrast artifact: Actions run `36120770640`.

Important cases:

- seed642: multi-unit WOOL, votes `[2,2,2]`, qty2, quote exposure16, regression -38.
- seed649: singleton MILK, votes `[1,1,2]`, quote exposure0, small regression.
- seed651: singleton MILK, votes `[0,0,1]`, qty1, quote exposure29; skipping the preempt is beneficial; full historical direct pair +12.
- seed440005 / 440012: multi-unit unanimous forecasts; broad K=2 changes are harmful.

Therefore the useful discriminator is prediction agreement + singleton quantity + quote/price exposure, not a global K threshold.

## 6. Current priority candidate: v143

Builder: `ci/build_v143_v92_single_weak_vote.py`.

v143 changes primary V92 only:

- keep v115 K=1 activation;
- only inspect singleton preempt (`amount == 1`);
- require exactly one positive top-replay vote;
- use predicted quantity and price/quote exposure to decide whether to skip the singleton SELL;
- leave multi-unit and KIL v52 exactly on the v115 path.

This directly targets the seed651 pattern and avoids the known v140 multi-unit regressions.

Experiment log:
`docs/experiments/EXP-20260925-v143-rate-oriented-singleton-confidence.md`

## 7. Formal v143 evaluation

Workflow:
`.github/workflows/v143-v115-formal-screen.yml`

Actions run:
`36131371313`

Sequence encoded in the workflow:

1. reconstruct exact v115 and SHA-check;
2. build + py_compile v143;
3. focused known-divergence sanity;
4. burned direct 641-652, both seats;
5. only if burned set has no losing pair and retains positive calibration effect, continue;
6. fresh direct 661-672, both seats;
7. fresh public panel 661-664 vs starter / beat_v48 / bl_v20 / bl_v21 / farming_v2 / frontier_prvsiyan;
8. aggregate candidate-minus-champion, seat effects, worst/best and exceptions.

Do not allocate sealed seeds until these gates are read.

Current infrastructure state at creation:

- GitHub-hosted runner retry `36130490523`: pre-start failure, `steps=[]`, `runner_id=0`; not candidate evidence.
- self-hosted formal run `36131371313`: accepted but queued waiting for a `self-hosted / Windows / X64` runner.
- earlier v141/v142 pre-start failures are infrastructure failures, not REJECT evidence.

## 8. Rate-oriented decision rule

Direct exact-v115 comparison is a safety gate, not the only optimization target. Kaggle rating gains require winning more of the opponent distribution.

For a narrow opponent-sensitive candidate like v143:

- Direct fresh neutrality can be acceptable if worst regression is safe and exceptions are zero.
- Public-opponent matched rows must show negative rows becoming ties/wins without destroying positive rows.
- Prefer stable loss-to-win conversion over increasing already-large cash margins.
- Public-panel evidence is development evidence only; sealed/unseen validation is still required for PROMOTE.

Historical v140 public calibration seeds 641-644:

- starter: `[+190, +5, 0, +26]`
- beat_v48: `[+1, -16, -1, 0]`
- bl_v20: `[0, +22, 0, +8]`
- bl_v21: `[0, +22, 0, +8]`
- farming_v2: `[+1, -16, -1, 0]`
- frontier_prvsiyan: `[+93, +2, -1, 0]`

The goal is not to preserve every v140 delta. v143 should keep only improvements supported by its singleton-confidence condition while reverting unjustified divergences toward v115.

## 9. Next candidate if v143 fails

Do not threshold-sweep the existing `0.06` price-exposure constant.

Candidate v144 should use a single economic expected-value decision for primary V92 singleton preemption:

`expected_ordering_gain - expected_quote_exposure_cost`

Inputs should come from existing state only:

- replay prediction agreement / confidence;
- predicted future quantity;
- current/hypothetical quote price;
- competitor last sale / exposure;
- whether the single slot is likely to gain priority before forecast demand arrives.

Keep KIL v52 and multi-unit paths exactly v115. Use telemetry-first synthetic cases before formal evaluation.

## 10. Next independent rate axis after V92

Do not jump back to dormant wrappers. Existing public analyses show a recurring close-family weakness is sale timing/pricing, especially MILK / WOOL / STRAWBERRY after midgame, while more distant families can differ in EGG / MELON / STRAWBERRY production.

Priority after V92:

1. sale-timing expected value for the close-copy family;
2. endgame cash realization only where telemetry shows unsold valuable inventory or avoidable late purchases;
3. production/farm branching only when replay telemetry proves a repeatable opponent-family loss, because broad production changes have historically created severe regressions.

Any such candidate remains 1-3 major changes and must first prove the target mechanism fires under exact v115.

## 11. Current decision

```text
FORMAL CHAMPION:
v115_champion_same_turn_open_squeeze.py

CURRENT PRIORITY:
v143 single-weak-vote + quote-exposure singleton V92 guard

STATUS:
KEEP TESTING
NO PROMOTE

NEXT IF v143 FAILS:
v144 economic expected-value singleton preempt
```
