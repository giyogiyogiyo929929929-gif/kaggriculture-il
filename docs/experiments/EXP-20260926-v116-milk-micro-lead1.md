# EXP-20260926 — v116_milk_micro_lead1

## Status

**KEEP TESTING — DO NOT PROMOTE**

Formal champion remains `v112_wheat_lead3_lowdemand`.

This experiment belongs to the current v90→…→v112 lineage only. It must not be interpreted as part of the separate v130+ lineage, and v66 is not a comparison target.

## Parent / champion

- candidate: `v116_milk_micro_lead1`
- parent / formal champion: `v112_wheat_lead3_lowdemand`
- canonical engine target: `kaggle_environments==1.32.7`
- sign convention: `candidate_minus_champion = candidate - champion`

The reproducible source builder is `experiments/v112_v116_milk_micro/build_sources.py`. It reconstructs v112 with SHA-256 `1c6e00ff0bd46b16189b1f6a93ce5e498ff8ffb5b0acb33591cdd247cd8b4771` and v116 with SHA-256 `7a040533a8086b19435a9a0df592d5189d301c3fb457410adf7291314577fc1c`.

## Hypothesis

Existing premium preemption intentionally targets larger premium batches. Native MILK micro-sales below `_PREEMPT_MIN_FUTURE_QUANTITY` can still lose a race to a classified / near-clone opponent while being too small to enter that layer.

Advance only these native MILK micro-sales by one turn when public state says doing so does not sacrifice an immediate Town-consumption benefit.

## Changes

One market-timing mechanism only:

1. detect a native next-turn MILK SELL with `0 < q < _PREEMPT_MIN_FUTURE_QUANTITY`;
2. in classified / near-clone mode, move exactly the available quantity one turn earlier;
3. do not cross a deterministic MILK Town-demand tick;
4. require a free market-order slot, positive market price above floor, and enough projected shed stock;
5. repay exactly at the original native SELL step so total intended quantity is conserved.

The candidate inserts the early MILK SELL before non-SELL market orders and leaves the existing premium-preemption logic intact. It records overlap with any live parent repayment as telemetry rather than changing parent behavior.

## Telemetry

`agent.telemetry["milk_micro_lead1"]` records:

- `shifts`
- `units`
- `demand_blocks`
- `fallback_blocks`
- `stock_blocks`
- `slot_blocks`
- `parent_due_overlap`
- `errors`
- up to 64 activation `steps`

This is sufficient to distinguish no-activation, public-state blocking, inventory blocking, order-slot blocking, and interaction with existing premium preemption.

## Static / focused checks

- decoded v116 suffix compiles successfully with Python `compile(..., "exec")`;
- source builder contains fixed SHA assertions for v110b, v112 and v116;
- Actions workflow runs `py_compile` on reconstructed `v110b_wheat_late_batch_lead2.py`, `v112_wheat_lead3_lowdemand.py`, `v116_milk_micro_lead1.py`, and the exact evaluator before H2H.

## Planned exact evaluation

`run_initial_eval.py` defines same-seed + seat-swap pairs and the required sign convention.

Planned blocks:

- v112 reconstruction check vs v110b: validation `287001–287012`, sealed `288001–288004`, stress `289001–289008`;
- v116 vs v112 validation: `293001–293012`;
- v116 vs v112 sealed: `294001–294004`;
- v116 vs v112 stress: `295001–295008`;
- starter seeds `1–5` for both v116 and v112;
- runtime sample with median / p99 / max / exception count;
- activation telemetry aggregated separately for validation / sealed / stress.

## Execution result / infrastructure block

GitHub Actions run `36241871674` (`v112-v116-current-lineage-initial`) failed before any workflow step executed. A retry was requested; the retried job again completed with failure and exposed no steps. This is an infrastructure/runner-allocation failure, not evidence that the candidate or evaluator failed.

The local sandbox cannot currently provide the canonical fallback because `kaggle_environments` is not installed and outbound package/network resolution is unavailable. Therefore no H2H numbers are claimed here.

## Decision

**KEEP TESTING.**

Do not promote v116 until the planned exact H2H actually runs and confirms:

- positive matched-pair result after seat swap;
- acceptable worst regression;
- nontrivial telemetry activation (avoid repeating the v113/v114 no-activation failure mode);
- sealed and stress reproduction;
- no clear external-opponent regression;
- runtime below project limits;
- zero exceptions / timeouts.

If validation shows zero `shifts`, reject as no activation. If activation is concentrated only in one seed or interacts adversely with parent premium repayments, reject or tighten the gate rather than broadening the lead horizon.
