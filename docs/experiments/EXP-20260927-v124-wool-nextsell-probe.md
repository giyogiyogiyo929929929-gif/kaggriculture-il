# AUXILIARY — WOOL next-sell probe (historically named v124)

## Status

**PROBE COMPLETE — HYPOTHESIS CLOSED — NOT A CANDIDATE — DO NOT PROMOTE**

This branch used the label `v124` before the already-existing formal `v124_external_econ_gap_probe` lineage was rediscovered. It is therefore **auxiliary only** and must not be treated as the formal v124 experiment or used for later version sequencing.

Formal champion remains `v112_wheat_lead3_lowdemand`.

## Run

- workflow run: `36314184123`
- job: `108605652673`
- canonical engine: `kaggle_environments==1.32.7`
- panel: seed `309004`, 10 bronze-panel opponents, both seats = 20 games

## Finding

A clean WOOL signal occurs around step 578 with shed WOOL `2` and a high public price. The v112 signal-turn action includes `BUY_SEED WHEAT 8` and does not sell WOOL immediately.

Across all 20 games, the next exact runtime WOOL sale is step 600, quantity `10`. The step-600 price is equal to or slightly **higher** than the signal price:

- `v49` / `v50`: 229 -> 231
- `metav4_v13` / `k256_h2_q_v1` / `story_of_seasons`: 230 -> 231
- `market_rhythm`: 228 -> 231
- `thomas_router_93`: 238 -> 239
- `tetsutani_dpts_b`: 229 -> 231
- `jaxa_2802` / `ready_stock`: 236 -> 237

There are also four BUY-action turns between the signal and the later sale in every captured trajectory.

## Decision

Do **not** front-load the two WOOL from step 578. The observed later sale receives an equal or better price and batches the inventory safely. This WOOL timing hypothesis is closed.

The formal active research priority is the official v124/v125/v126 day-10 external-economic/MELON track, not this auxiliary branch.
