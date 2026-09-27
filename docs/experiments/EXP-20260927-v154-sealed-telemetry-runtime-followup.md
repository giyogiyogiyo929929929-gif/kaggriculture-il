# EXP-20260927 v154 sealed telemetry / runtime follow-up

## Status

**SEALED TELEMETRY PASS / FIRST RUNTIME QUALIFICATION FAILS ONLY MAX-SPIKE GATE / INSTRUMENTED RUNTIME RECHECK QUEUED / NOT PROMOTED.**

Formal champion remains exact v147 SHA `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`.
Formal v154 builder output SHA is `7366261d9eb774777b222e69d3ddfabd170f6622dfb68eafa02697e2c4baa23e`.

## Sealed telemetry diagnostic

Workflow run `36308744147` completed successfully. It replayed burned sealed seeds 1802, 1806, 1809, and 1810 against exact v147, both seats, and compared each v154 action with a shadow v147 action on the same observation.

### Seed 1802 seat asymmetry

The sealed direct legs were `-24 / +78`, pair `+27`.

- Candidate seat 0: v154 was 78 money behind immediately before the only changed action at step649 (`86878` vs `86956`).
- Shadow v147 leading SELL order at step649 included `MILK, CARROT, WOOL, FERTILIZER, WHEAT, EGG`.
- v154 changed only the dense SELL order to `MILK, CARROT, FERTILIZER, WOOL, WHEAT, EGG` before the later BUY_PRODUCT barrier.
- Candidate seat-0 final leg was `-24`.
- Candidate seat 1: `_V154_REPORT.changed == 0`, `_V154_REPORT.eligible == 0`, and the gate skipped all candidate reorder opportunities while ahead; final leg was `+78`.

Because the seat-1 candidate never changes the parent v147 action, `+78` identifies the pure seat/order advantage for exact-v147 behavior on that trajectory. The corresponding baseline for the opposite seat is therefore `-78`. v154 changes the seat-0 result from an inferred baseline `-78` to `-24`, a causal improvement of `+54`. Averaging the two seats yields the observed sealed pair `+27`.

Conclusion: seed1802 is **not a v154 regression**. The apparent negative leg is seat-order disadvantage partially recovered by the v154 reorder. The matched-pair interpretation is correct and the telemetry explains the asymmetry.

### Positive controls

- seed1806: changed step649 both seats, final `+43 / +43`. At tied money, v154 moves FERTILIZER ahead of CARROT/WOOL relative to v147.
- seed1809: changed step649 both seats, final `+55 / +55`. At tied money, v154 moves FERTILIZER ahead of WOOL relative to v147.
- seed1810: changed step577 both seats, final `+3 / +3`. At tied money, v154 moves FERTILIZER ahead of WOOL relative to v147.
- all diagnostic cases: `_V154_REPORT.errors == 0`.

Telemetry verdict: **PASS**. The sealed improvement is caused by the intended dense leading-SELL reorder, while the not-ahead gate explains the seat-asymmetric 1802 behavior.

## First final runtime qualification

Workflow run `36308834324` reconstructed exact v147 and formal v154 under `kaggle_environments==1.32.7`, GC enabled, sequential single-process timing, seeds 681/682/689/691/692 both seats.

Result:

- calls: `7190`
- median: `4.75015 ms`
- p95: `10.2987 ms`
- p99: `20.3448 ms`
- max: `219.0168 ms`
- errors: `0`
- all games completed with DONE statuses
- required thresholds: p99 `< 50 ms`, max `< 200 ms`
- qualification result: **FAIL**, solely because one max wall-time sample exceeded 200 ms.

The over-threshold sample occurred in seed681 candidate seat0. That row had median `3.9074 ms`, p99 `20.9127 ms`, max `219.0168 ms`. The opposite seat on the same seed had max `150.5929 ms`; all other rows had max at or below `166.6383 ms`.

This is not accepted as a runtime pass. It is treated as a possible isolated scheduler/GC wall-time spike until reproducibility is checked.

## Runtime recheck

Instrumented workflow `v154-runtime-recheck-instrumented.yml` was added with the same five seeds and both seats. It records the step number and top timing samples for every game while keeping GC enabled and the same p99/max thresholds.

Run: `36310368875`.

Promotion remains blocked until this recheck completes successfully or the >200 ms behavior is otherwise resolved.

## Decision

- v154 remains the current leading candidate.
- sealed telemetry gate: **PASS**.
- runtime gate: **NOT YET PASSED**.
- champion remains v147.
- no PROMOTE yet.
- no Kaggle submission.
