# EXP-20260926 — v123 step649 realized-order telemetry

## Status

**DIAGNOSTIC READY / EXACT-ENGINE RUN BLOCKED BY OFFLINE SELF-HOSTED RUNNER. Not a promotion candidate.**

## Parent / champion

- formal champion: `v122_champion_step649_wheat_after_fert.py`
- parent SHA256: `ae4c0f5a9afabf2e6d668cf0571b41bfe9a52a9179b499a71aeb6b7508ace8f1`
- rollback v104 SHA256: `78519fbec9086be2c78ef9ac0a10d2f39edc19fd17748286131242b9adcc1a9e`
- exact v104 was independently recovered from exact v122 by removing the final v122 overlay plus its preceding newline; recovered bytes hash exactly to the recorded rollback SHA
- generated diagnostic SHA256: `a489de893be614667d1700ee92882990200f13bbae0c3eb1a59c9857ca844eca`

## Purpose

Before changing any additional step-649 order slot, capture the final v122 market action and relevant state at step 649. The v122 handover explicitly requires realized execution-ledger evidence before modifying other step-649 slots.

## Changes

Behavior-preserving diagnostic wrapper only. At step 649 it records:

- final market orders after v122
- initial contiguous SELL block
- SELL item sequence / quantities
- whether v122 fired on the current call
- market inventory / prices
- own and rival public cash
- own shed
- unlocked shops

The parent action is returned unchanged.

## Static / synthetic

- exact parent SHA gate: PASS
- `py_compile`: PASS
- AST parse: PASS
- SELL-block helper synthetic test: PASS
- stubbed-parent identity/equality test: PASS; diagnostic returned the exact same action object

## Evaluation plan

When exact `kaggle_environments==1.32.7` execution is available:

1. recover telemetry on known diagnostic controls 401001/401002/401003 and the 402001..402012 v122 validation block, with both seats where applicable;
2. compare positive cases against the known 401002 WHEAT/EGG-swap negative control;
3. identify a structural separator based on realized execution rather than gross planned SELL order;
4. create a separate one-change tactical candidate on exact v122;
5. use fresh/sealed seeds for adoption evidence rather than retuning on these diagnostic seeds.

## Decision

Observation-only diagnostic. **Formal champion remains exact v122.**
