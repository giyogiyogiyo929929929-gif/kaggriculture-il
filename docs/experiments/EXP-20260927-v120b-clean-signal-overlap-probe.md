# EXP-20260927 — v120b_clean_signal_overlap_probe

## Status

**PROBE COMPLETE — ACTIONABLE WINDOWS FOUND — NOT PROMOTION ELIGIBLE**

Formal champion remains `v112_wheat_lead3_lowdemand`.

v120 established that `clean positive` premium market-inventory events separate v112-clone self-play from all 10 external opponents. v120b is action-identical to v112 and measures whether those signals overlap executable and safe SELL opportunities.

## Hypothesis

A clean signal is useful only if the current v112 state can actually respond. For a clean signal at step `t`, measure:

- positive same-item quantity in private shed;
- a v112 parent SELL at `t`;
- a native/static same-item SELL at `t+1`, `t+2`, or `t+3`;
- current BUY/cash dependency;
- current price state.

The purpose is to avoid repeating v119's harmful blind premium reordering and v114's zero-activation MELON lead.

## Changes

Telemetry-only wrapper over exact v112. It returns the exact parent action object unchanged.

Tracked items: `STRAWBERRY`, `MELON`, `MILK`, `WOOL`.

For each clean signal (`inventory_delta > 0` and our previous-turn SELL quantity for that item is zero), the probe records current shed quantity, actual same-turn parent SELL, static same-item SELL at +1/+2/+3, current BUY presence, and market inventory/price.

## Environment

- branch: `eval/v112-v120b-overlap-probe-20260927`
- canonical engine: `kaggle_environments==1.32.7`
- champion: `v112_wheat_lead3_lowdemand`
- probe: `v120b_clean_signal_overlap_probe`
- self-hosted runner: `CIYOI`, Windows X64
- workflow run: `36295388838`
- job: `108553169251`
- workflow commit: `cfa444c11b62ba054cd04581b70883c5e942331b`
- v120b built SHA256: `a3a9bfc16793d959ae58151d219a4429240396ddc347b72c19acfb7d7c4fabac`
- exact v112 SHA256: `1c6e00ff0bd46b16189b1f6a93ce5e498ff8ffb5b0acb33591cdd247cd8b4771`

Artifact:

- name: `v112-v120b-clean-signal-overlap-probe`
- artifact ID: `10924253932`
- artifact ZIP SHA256: `6618d5e092ef57c087fa0ce72c3b26638ab2cecbb1af85676748689b6c1728eb`

## Canonical execution

Synthetic/source reconstruction/py_compile all passed.

### Clone semantic gate

Seeds 308001–308004, v120b vs v112, both seats.

Pair diffs:

- 308001: 0.0
- 308002: 0.0
- 308003: 0.0
- 308004: 0.0

Telemetry errors: 0.

Decision: **PASS**. v120b remained action-identical to v112.

### External overlap panel

Seeds 309001–309004, both seats, against:

- v49
- v50
- metav4_v13
- k256_h2_q_v1
- market_rhythm
- story_of_seasons
- thomas_router_93
- tetsutani_dpts_b
- jaxa_2802
- ready_stock

Across 80 external games, aggregate clean/overlap counts were:

| metric | STRAWBERRY | MELON | MILK | WOOL |
|---|---:|---:|---:|---:|
| clean events | 2298 | 480 | 2292 | 2054 |
| shed > 0 | 838 | 0 | 428 | 152 |
| same-item SELL now | 220 | 80 | 124 | 52 |
| future SELL h1 | 178 | 0 | 122 | 28 |
| future SELL h2 | 334 | 160 | 202 | 40 |
| future SELL h3 | 230 | 160 | 268 | 102 |
| any SELL h0..h3 | 702 | 240 | 484 | 192 |
| shed > 0 and SELL h0..h3 | 226 | 0 | 102 | 40 |
| price >= nominal base | 798 | 80 | 388 | 720 |
| price >= 75% nominal base | 932 | 480 | 658 | 1260 |

All clean events in this panel were current-turn BUY-free, so BUY/cash dependency was not the limiting factor.

Using the conservative feasibility filter:

`clean signal + shed>0 + same-item SELL within h0..h3 + no BUY + price>=75% nominal base`

there were 70 events:

- STRAWBERRY: 32
- MELON: 0
- MILK: 4
- WOOL: 34

First SELL distance among these feasible events:

- STRAWBERRY: h0=20, h1=8, h2=4
- MILK: h0=4
- WOOL: h0=28, h2=6

## Findings

### MELON: reject immediate-response axis

MELON generated 480 external clean events, but `shed>0` occurred **zero times**. This directly explains why the earlier shed-only MELON lead candidate v114 did not activate.

Do not repeat a simple MELON immediate SELL/lead experiment without a different stock-generation mechanism.

### Correction to the provisional MILK@358 hypothesis

The pre-probe v120 audit suggested `MILK@358 -> SELL@360` as a possible two-turn reactive lead. v120b invalidates that direct hypothesis:

- v49/v50/tetsutani cases at step 358 had no executable MILK shed stock;
- comparable jaxa cases also lacked stock before the later SELL;
- cases with six MILK available were already at the native same-turn SELL state.

Therefore do **not** create a MILK@358 lead candidate.

### Strong overlap but no timing room: WOOL@432

A recurring hotspot is WOOL around step 432:

- observed across multiple independent opponents and both seats;
- shed approximately 24;
- price roughly 200–232, median around 227;
- parent already sells the same 24 WOOL in the same turn;
- no BUY dependency.

This is evidence that the race detector is economically meaningful, but it does not expose a safe timing lead because v112 is already liquidating the available stock. Reordering the same-turn premium SELL is not preferred because v119 showed that blind premium reordering can be strongly harmful.

### Best next tactical window: STRAWBERRY around step 577

The clearest under-liquidated high-price window found in the overlap telemetry is STRAWBERRY around step 577:

- clean external race signal;
- observed in a narrower subset of external opponents/seeds rather than clone self-play;
- shed about 32;
- current parent SELL about 8;
- price about 153, well above nominal base 120;
- no BUY dependency;
- no same-item static SELL within the immediate +1..+3 window in the observed cases.

Unlike WOOL@432, v112 has materially more executable stock than it currently sells. This makes the state suitable for a narrowly gated quantity/timing experiment.

Before changing total lifetime quantity, inspect the later STRAWBERRY schedule beyond h3. Prefer moving a bounded amount from a later known SELL into the clean-signal turn, then subtracting exactly that amount from the later SELL. This preserves total sold quantity and isolates timing as the causal change.

### Secondary narrow window: WOOL around step 598

A smaller secondary window exists around WOOL@598:

- shed about 2;
- price around 169 (~84.5% of nominal base);
- a larger native WOOL SELL appears roughly two turns later in the observed cases.

A two-unit lead with exact repayment is technically testable, but it is lower priority because it appears in fewer opponents and has small economic magnitude.

## External-strength context

Because v120b is action-identical to v112, its external scores are still the champion's external scores. The 40 matched seed-opponent pairs remained all losses, consistent with v120. The probe therefore does not improve performance itself; it identifies states for a later opponent-reactive candidate.

## Next experiment

Before creating v121:

1. inspect the static/later STRAWBERRY SELL schedule after the step-577 window;
2. identify the nearest later SELL from which 4–8 units can be borrowed without colliding with existing premium-preemption repayment;
3. build one narrow sibling candidate on exact v112:
   - trigger only on the clean public-market signal;
   - require executable STRAWBERRY shed stock above the current parent SELL;
   - require a strong price floor, preferably `price >= nominal base` or tighter;
   - require no current BUY dependency;
   - advance only a bounded quantity from a known later STRAWBERRY SELL and repay exactly;
   - preserve order of all other market orders.

Do not combine this with WOOL or MILK changes in the same candidate.

## Public-reference cross-check

Current public research also contains a reactive-sales line evaluated against independent strong/reacting opponents. It is treated only as directional support. No public code is copied into this lineage; any tactical v121 must be justified by the local v120/v120b telemetry and canonical evaluation.

## Files

- `experiments/v112_v116_milk_micro/v120b_suffix.pyfrag`
- `experiments/v112_v116_milk_micro/test_v120b_probe_synthetic.py`
- `experiments/v112_v116_milk_micro/build_v120b.py`
- `experiments/v112_v116_milk_micro/run_v120b_probe.py`
- `.github/workflows/v112-v120b-overlap-probe-selfhosted.yml`

## Decision

**PROBE SUCCESS. ACTIONABLE WINDOWS FOUND. v120b itself is not promotion eligible. Formal champion remains `v112_wheat_lead3_lowdemand`. Next step is a schedule audit for a narrowly gated STRAWBERRY reactive lead candidate.**
