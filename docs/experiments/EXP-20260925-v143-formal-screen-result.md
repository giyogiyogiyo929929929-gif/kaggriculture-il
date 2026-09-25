# EXP-20260925 — v143 formal screen result

## Decision

**HOLD / DO NOT PROMOTE. Do not spend sealed seeds.**

Official champion remains `v115_champion_same_turn_open_squeeze.py` (SHA-256 `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`).

v143 is safe on this screen but has no fresh opponent-rate evidence. Preserve it as a diagnostic result, run telemetry only on already-burned differing seeds, then prioritize other hypotheses.

## Candidate

- parent/champion: exact v115
- candidate: `ci/build_v143_v92_single_weak_vote.py`
- change: primary V92 singleton only; positive quote exposure + exactly one weak replay vote causes abstention
- KIL v52 and all multi-unit paths remain v115
- formal engine: `kaggle_environments==1.32.7`
- metric: `candidate_minus_champion = candidate - champion`
- Actions run: `36131371313`
- artifact: `v143-v115-formal-screen`, artifact id `10863815781`
- artifact digest: `sha256:3c7f2b92cf186b96084d1a2fa803c4d5116c66de51ccb40ce98a6f87be4563a8`

## Focused sanity

Known burned divergences matched the expected behavior:

- seed642: 0 vs v115
- seed649: 0
- seed651: +12
- seed440005: 0
- seed440012: 0

No exception gate failed.

## Burned direct calibration — seeds 641–652, seat swap

12 matched pairs / 24 games:

- W/L/T: **1 / 0 / 11**
- mean candidate-minus-champion: **+1.0**
- worst: **0**
- best: **+12**
- candidate exceptions: 0
- champion exceptions: 0

Only seed651 is non-zero: **+12**. All other seeds are exactly 0 after seat averaging.

This confirms that v143 retained the known seed651 benefit and removed the known v140 negative pair regressions on the burned calibration set.

## Fresh direct — seeds 661–672, seat swap

12 matched pairs / 24 games:

- W/L/T: **0 / 0 / 12**
- mean: **0.0**
- SE: **0.0**
- worst: **0**
- best: **0**
- candidate exceptions: 0
- champion exceptions: 0

Pair averages are all zero. Two seeds contain opposite seat-specific deltas that cancel exactly:

- seed663: `+50 / -50`
- seed669: `+41 / -41`

All other fresh direct games are exactly 0 by seat and pair.

Interpretation: the rule can alter behavior, but the only fresh direct changes seen here are seat-dependent and provide no matched-pair gain.

## Fresh public-opponent panel — seeds 661–664

Opponent panel:

- starter
- beat_v48
- bl_v20
- bl_v21
- farming_v2
- frontier_prvsiyan

24 opponent/seed matched rows total:

- W/L/T: **0 / 0 / 24**
- mean: **0.0**
- SE: **0.0**
- worst: **0**
- best: **0**
- candidate exceptions: 0
- champion exceptions: 0

Every candidate money and margin result is identical to v115 in both seats for every public row in this fresh panel.

## Interpretation

The candidate succeeds at the narrow calibration objective: it preserves the useful burned seed651 skip and removes v140's known broad-K regressions. However, it does not reproduce a rate-oriented benefit on fresh seeds or the representative public panel.

The fresh direct seat cancellation on seeds663/669 is a warning against treating zero pair mean as proof of complete behavioral equivalence. These two already-burned seeds should be diagnosed to identify the first divergent SELL and the replay-vote/exposure state.

## Telemetry follow-up

Added `ci/diagnose_v143_fresh_seat_dependence.py` and workflow `.github/workflows/v143-fresh-seat-telemetry.yml`.

Cases are deliberately limited to already-burned seeds:

- 663 seat0 / seat1
- 669 seat0 / seat1
- 651 seat0 / seat1 as positive control

No unused or sealed seed is consumed.

## Next hypothesis

Do not threshold-sweep v143. Prioritize hypotheses with independent public evidence and wider expected activation:

1. guarded four-turn sale reservation (public V36 mechanism), isolated to the existing R37 horizon;
2. economic expected-value singleton V92 only if four-turn evidence fails or telemetry reveals a concrete expected-value discriminator.

Public room-guard remains lower priority because prior capacity-guard evidence often changes cash/actions without converting outcomes.
