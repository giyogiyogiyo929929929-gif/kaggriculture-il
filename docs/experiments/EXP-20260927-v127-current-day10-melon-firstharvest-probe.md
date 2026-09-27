# EXP-20260927 — v127_current_day10_melon_firstharvest_probe

## Status

**PROBE RUNNING — NOT A CANDIDATE — DO NOT PROMOTE**

Formal champion remains `v112_wheat_lead3_lowdemand`.

`v127_current` is used deliberately because an unrelated historical/separate-lineage v127 exists. This experiment belongs only to the current v112 lineage.

## Parent evidence

v126 established that v112 already carries 30 MELON at steps 249–250 but delays return to shed. A representative hand carries 6 MELON near the farm, performs another WATER/HARVEST/PLANT cycle to reach 12, then returns and executes `DROP + SELL MELON 12` at step 256. The next question is where the first six MELON become available and where a minimal route diversion should begin.

## Probe design

No action mutation. Trace exact v112 and two representative important external opponents:

- `thomas_router_93`
- `metav4_v13`

Seeds `309001`, `309004`, both seats: 8 games total.

Engine: `kaggle_environments==1.32.7`.

Watch steps 238–250. For every hand, identify the first observation where carried MELON changes from below 6 to at least 6 and record:

- hand index;
- first visible step;
- quantity;
- position;
- Manhattan distance to the observed shed/deposit coordinate `[4,4]`;
- previous-turn hand action, which should reveal the acquisition HARVEST;
- current action;
- public MELON price.

Full traces for the window are retained in the artifact.

## Decision rule

The probe should locate a stable state-based intervention point, not merely a hard-coded seed/step.

If a consistent hand obtains its first six MELON while only a short safe path from shed and then starts another local cycle, the next sibling candidate may redirect one such hand toward shed during the high-price day-10 window. The candidate must remain narrow and must not change the other hands' farm macro.

If acquisition locations/routes vary materially across seeds/opponents or the earliest return would disrupt critical farm sequencing, do not build a blind route override; instrument the relevant dependency first.
