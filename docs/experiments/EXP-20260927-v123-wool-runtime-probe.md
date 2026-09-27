# EXP-20260927 — v123_wool_runtime_probe

## Status

**PROBE SUCCESS — NOT A CANDIDATE — DO NOT PROMOTE**

Formal champion remains `v112_wheat_lead3_lowdemand`.

## Motivation

v122 was rejected because its step-456 order hypothesis came from static `_ACTIONS`, while exact v112 runtime output already had WOOL before WHEAT. v123 therefore traces exact v112 runtime actions directly.

The specific v120b late-window hypothesis at steps 598–600 was already known to be concentrated in seed `309001`; v123 tests whether exact runtime behavior justifies a tactical candidate there and searches the same 560–620 region for stronger repeated states.

## Environment

- workflow run: `36312199550`
- job: `108600190686`
- run head: `b8c55d205f01991f62c05332782ef1c66e3e5263`
- self-hosted runner: CIYOI / Windows X64
- Python: 3.11.9
- engine: `kaggle_environments==1.32.7`
- exact v112 SHA256: `1c6e00ff0bd46b16189b1f6a93ce5e498ff8ffb5b0acb33591cdd247cd8b4771`
- artifact: `v112-v123-wool-runtime-probe`, ID `10929509474`
- artifact digest: `sha256:7df4ebd4d0039a62cad7e04d34a91b2e9def5d8b1f4572c533cd955977bf02be`

Panel:

- seeds: `309001`, `309003`, `309004`;
- opponents: `v49`, `v50`, `metav4_v13`, `k256_h2_q_v1`, `market_rhythm`, `story_of_seasons`, `thomas_router_93`, `tetsutani_dpts_b`, `jaxa_2802`, `ready_stock`;
- both seats;
- 60 games total.

For clean positive WOOL inventory transitions in steps 560–620 where our previous runtime action sold zero WOOL, the probe records exact runtime market actions at the signal and next three turns.

## Findings

### 1. The original 598–600 hypothesis remains seed-concentrated

The exact runtime probe confirms the interesting 598–600 sequence only in seed `309001` for the original three opponents:

- `metav4_v13`: clean signals at 598 and 599;
- `k256_h2_q_v1`: clean signals at 598 and 600;
- `story_of_seasons`: clean signals at 598 and 599;
- both seats in each case.

At step 598 the common state is approximately:

- WOOL price `169`;
- shed WOOL `2`;
- clean inventory increase `+2`;
- no same-turn WOOL SELL;
- exact v112 runtime later sells WOOL 10 at step 600.

This is a real runtime timing opportunity, not a static-tape artifact, but it is confined to one world seed in the audited panel. Under the bronze policy this is insufficient to justify a new tactical candidate by itself.

### 2. Clean WOOL signals occur broadly across all three seeds

The probe found many clean WOOL inventory increases in all three world seeds, so the detector itself is not seed-specific. Examples include:

- seed `309001`: steps 563/565/569/578/584/593/594/596/598/599/600/603 depending on opponent;
- seed `309003`: common step 578 plus opponent-specific later signals;
- seed `309004`: steps 563/565/566/578/579/584/592/593/594/595.

### 3. Stronger follow-up state: step 578 high-price held WOOL

A more interesting repeated runtime state appears in seed `309004`:

- all 10 external opponents;
- both seats;
- clean WOOL signal at step `578`;
- current WOOL price approximately `230`;
- shed WOOL `2`;
- v112 does not SELL WOOL at the signal or in the next three runtime actions.

The same nominal step also appears in other seeds, but with materially different economics:

- seed `309001`: price around `98`, shed `2`;
- seed `309003`: price around `1`, shed `0`;
- seed `309004`: price around `230`, shed `2`.

Therefore a future probe/candidate must gate on observable market state such as price and shed, never on the seed or step alone.

## Decision

- v123 itself is telemetry-only and cannot be promoted.
- Do **not** create a candidate from the 598–600 sequence; the current evidence is too concentrated in seed `309001`.
- Do **not** close WOOL research entirely: step578 in the high-price regime is a stronger observable-state hypothesis than the late 598–600 sequence.
- Before changing actions, trace the exact next runtime WOOL SELL after the high-price step578 state and confirm whether the held 2 WOOL can be shifted without altering eventual total quantity or crossing BUY/premium dependencies.

## Next hypothesis

Action-identical follow-up probe:

`clean WOOL signal + price >= ~220 + shed >= 2 + no current WOOL SELL`

Measure the first subsequent runtime WOOL SELL, elapsed turns, price path, shed path, and intervening BUY/premium dependencies. Only create a tactical candidate if the same observable state reproduces on fresh world seeds or there is an independently robust mechanism.
