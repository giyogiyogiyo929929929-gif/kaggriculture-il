# EXP-20260927 v154 sealed telemetry / runtime follow-up

## Status

**SEALED PASS / TELEMETRY PASS / SELF-HOSTED ABSOLUTE MAX GATE NOISY / DUAL-AGENT RUNTIME SHOWS NO V154-SPECIFIC SPIKE / FINAL QUALIFICATION QUEUED / NOT PROMOTED.**

Formal champion remains exact v147 SHA `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`.
Formal v154 builder output SHA is `7366261d9eb774777b222e69d3ddfabd170f6622dfb68eafa02697e2c4baa23e`.

## Sealed result

Burned sealed seeds 1801-1812, both seats:

- 7W / 0L / 5D
- mean `+18.9167`
- SE `6.3407`
- mean - 2SE `+6.2354`
- worst matched pair `0`
- best `+55`
- candidate/champion exceptions `0`

The sealed range is burned and must not be reused as sealed.

## Sealed telemetry diagnostic

Workflow run `36308744147` completed successfully. It replayed burned sealed seeds 1802, 1806, 1809, and 1810 against exact v147, both seats, and compared each v154 action with a shadow v147 action on the same observation.

### Seed 1802 seat asymmetry

The sealed direct legs were `-24 / +78`, pair `+27`.

- Candidate seat 0: v154 was 78 money behind immediately before the only changed action at step649 (`86878` vs `86956`).
- Shadow v147 leading SELL order at step649 included `MILK, CARROT, WOOL, FERTILIZER, WHEAT, EGG`.
- v154 changed only the dense SELL order to `MILK, CARROT, FERTILIZER, WOOL, WHEAT, EGG` before the later BUY_PRODUCT barrier.
- Candidate seat-0 final leg was `-24`.
- Candidate seat 1: `_V154_REPORT.changed == 0`, `_V154_REPORT.eligible == 0`, and the gate skipped all candidate reorder opportunities while ahead; final leg was `+78`.

Because the seat-1 candidate never changes the parent v147 action, `+78` identifies the pure seat/order advantage for exact-v147 behavior on that trajectory. The corresponding opposite-seat baseline is `-78`. v154 changes the seat-0 result from the inferred baseline `-78` to `-24`, a causal improvement of `+54`. Averaging the seats yields the observed sealed pair `+27`.

Conclusion: seed1802 is **not a v154 regression**. The matched-pair interpretation is correct and telemetry explains the asymmetry.

### Positive controls

- seed1806: changed step649 both seats, final `+43 / +43`.
- seed1809: changed step649 both seats, final `+55 / +55`.
- seed1810: changed step577 both seats, final `+3 / +3`.
- all diagnostic cases: `_V154_REPORT.errors == 0`.

Telemetry verdict: **PASS**.

## First final runtime qualification

Workflow run `36308834324`, exact v147/v154, `kaggle_environments==1.32.7`, GC enabled, sequential single-process, seeds 681/682/689/691/692 both seats:

- calls `7190`
- median `4.75015 ms`
- p95 `10.2987 ms`
- p99 `20.3448 ms`
- max `219.0168 ms`
- errors `0`
- all games DONE
- threshold p99 `< 50 ms`, max `< 200 ms`

Result: **FAIL absolute max gate only**. One seed681 seat0 wall-time sample exceeded 200 ms.

## Instrumented runtime recheck

Run `36310368875` used the same five seeds and both seats and recorded top timing samples by step.

- calls `7190`
- median `4.51955 ms`
- p95 `10.066 ms`
- p99 `19.5894 ms`
- max `803.0121 ms`
- errors `0`
- all games DONE

Over-200 wall-time samples moved between unrelated seeds/steps: seed682 seat0 step350 `301 ms`, seed689 seat0 step315 `457 ms`, seed691 seat0 step599 `803 ms`. They did not concentrate on v154 reorder steps. Result remains **FAIL absolute max gate**.

## Dual-agent same-game runtime diagnostic

Run `36313491258` completed successfully and timed exact v154 and exact v147 in the same games, recording both wall and CPU time.

Key result:

- max v154 wall time: `332.6936 ms`
- max v147 wall time: `669.3171 ms`
- errors `0`
- both agents show isolated large pauses on the self-hosted Windows runner
- per-row p99 values are of similar scale; no evidence that the v154 wrapper introduces the >200 ms phenomenon

Notably seed689 candidate-seat1 produced v154 max `280.4288 ms` while v147 in the same game reached `669.3171 ms`.

Interpretation: the strict absolute max gate on this self-hosted Windows machine is currently dominated by runner/OS/GC pauses and no longer discriminates v154 from the promoted champion. This evidence **does not by itself convert the formal runtime gate to PASS**; it removes the hypothesis that v154 uniquely caused the spikes.

## Clean-runner attempt

A GitHub-hosted Ubuntu qualification/preflight workflow was added. Run `36314244424` failed before any workflow steps started, so it provides no candidate runtime or correctness evidence and is treated as infrastructure-only failure.

A self-hosted formal-source export run `36314303526` was also queued, but the single self-hosted runner is occupied by another evaluation. Exact formal v154 bytes were independently reconstructed from the retained v147 final preflight artifact; the reconstructed main SHA matches the formal builder SHA `7366261d...` exactly.

## Loader / package audit

The retained v147 final preflight artifact shows the original promotion loader audit intentionally recorded four malformed-observation cases as successful and `None` as the same legacy `AttributeError` for v115 and v147.

The exact formal v154 source was audited locally with the same five cases:

- `{}`: pass
- `{'player': 0}`: pass
- `{'farms': []}`: pass
- `{'player': 5, 'farms': [{}]}`: pass
- `None`: `AttributeError: 'NoneType' object has no attribute 'get'`

This vector is identical to exact v147, so there is **no loader robustness regression** relative to the promoted champion. Last top-level function / last callable remains `agent`; source compiles and uses no non-stdlib imports.

Formal v154 source size: `1,058,561` bytes. Local final-package tar contains only root `main.py`.

## Final qualification queue

The single self-hosted Windows runner is currently occupied by unrelated project evaluations. Those runs are not cancelled. The following v154 gates are already queued:

### Known-public regression

Run `36314990547`, workflow `v154-v147-known-public-regression.yml`.

Exact v154 is compared with exact v147 on the same six known public opponents used in the v147 promotion check:

- starter
- beat_v48
- bl_v20
- bl_v21
- farming_v2
- frontier_prvsiyan

Seeds 641-644 are burned development seeds. The existing matched evaluator covers both seats. Required interpretation: zero exceptions, no material outcome regression, and inspect worst candidate-minus-champion regression.

### Environment-qualified stable runtime gate

Run `36315261743`, workflow `v154-v147-stable-runtime-gate.yml`.

It performs three sequential trials on seeds 681/682/689/691/692, both seats. In every trial exact v147 is timed first. A trial counts as an objectively stable environment only when exact v147 itself has p99 `<50 ms`, max `<200 ms`, and no errors. Exact v154 must then satisfy the same thresholds in every such stable trial.

- At least one stable v147 trial + v154 passes every stable trial => runtime gate PASS.
- No stable v147 trials => INCONCLUSIVE, not a candidate failure.
- Stable v147 trial where v154 exceeds the threshold => candidate runtime FAIL.

This gate prevents host scheduler/GC noise that also hits the champion from being misclassified as a v154 regression.

### Final submission preflight

Run `36315341047`, workflow `v154-final-submission-preflight.yml`.

Adapted from the formal v147 final submission preflight. It checks:

- official engine version `1.32.7` and source SHA `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- exact v147 and v154 source SHAs
- static import audit
- no new risky audit signatures vs v147
- malformed-observation parity vs v147
- exact v154 engine smoke against starter, both seats
- package root contains only `main.py`
- packaged `main.py` retains exact v154 SHA
- loader resolves last callable `agent`
- packaged file py-compiles

Runtime qualification is intentionally separated into the stable-runtime gate above.

## Decision

- v154 remains the current leading candidate.
- sealed gate: **PASS**.
- telemetry gate: **PASS**.
- hard-opponent regression: **PASS with one small non-outcome regression (-4)**.
- loader/package audit relative to v147: **PASS**.
- dual-agent runtime causality: **PASS (no v154-specific spike)**.
- strict runtime qualification: **PENDING stable-runtime run `36315261743`**.
- known-public regression: **PENDING run `36314990547`**.
- final submission preflight: **PENDING run `36315341047`**.
- champion remains v147.
- no PROMOTE yet.
- no Kaggle submission.
