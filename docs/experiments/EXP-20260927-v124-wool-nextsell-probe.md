# EXP-20260927 — v124_wool_nextsell_probe

## Status

**PROBE RUNNING — NOT A CANDIDATE — DO NOT PROMOTE**

Formal champion remains `v112_wheat_lead3_lowdemand`.

## Motivation

v123 exact-runtime tracing found a more interesting WOOL state than the seed-309001 late window:

- seed `309004`;
- all 10 bronze-panel opponents, both seats;
- clean positive WOOL market-inventory transition around step `578`;
- WOOL price about `229–230`;
- shed WOOL `2`;
- v112 does not SELL WOOL on the signal turn or within the next three traced turns.

The signal turn itself contains `BUY_SEED WHEAT 8` in the known v49/v50 runtime traces, so a tactical mutation must not be created until the eventual WOOL liquidation path and BUY dependencies are known.

## Probe design

No candidate wrapper is used. Exact `v112_wheat_lead3_lowdemand` is traced directly.

Panel:

- seed `309004`;
- all 10 bronze-panel opponents;
- both seats;
- canonical engine `kaggle_environments==1.32.7`.

Trigger:

- clean positive WOOL inventory transition;
- previous runtime action sold zero WOOL;
- current WOOL price >=220;
- current shed WOOL >=2;
- current runtime action sells zero WOOL.

For each trigger, follow exact runtime state until the next WOOL SELL or step 650 and record:

- signal inventory / price / shed / runtime market orders / BUY-like orders;
- minimum and maximum WOOL price before the next SELL;
- maximum shed quantity before the next SELL;
- count of intervening BUY-action turns;
- next WOOL SELL step / price / quantity / shed / exact runtime order list.

## Decision rule

Do not create a tactical candidate unless the probe shows a coherent quantity-preserving move from the high-price signal to an identifiable later WOOL SELL.

Even then, the next candidate must:

1. preserve total WOOL sold by repaying from the identified later runtime SELL;
2. avoid crossing or breaking BUY dependencies;
3. keep premium-to-premium order unchanged unless independently justified;
4. pass fresh same-seed/seat-swap self-H2H and fresh external seeds;
5. not rely on seed `309004` alone for promotion evidence.

If the two WOOL are already sold at an equal or better later price, or if the later SELL cannot be safely identified, close this timing hypothesis.
