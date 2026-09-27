# uploaded_127ed3_ca_feed0_d25_carrot_hold_v1 — sealed1 precommit — 2026-09-27

Status: **SEEDS FIXED BEFORE EVALUATION**

## Identity

- candidate: `uploaded_127ed3_ca_feed0_d25_carrot_hold_v1`
- candidate SHA256: `2aab62a693bd3a357ad87649b8ba90a79b512d383a7694b07bbcdbe0deef48c8`
- formal champion / parent: `uploaded_127ed3_ca_feed0`
- champion SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`

## Burned evidence before sealed allocation

Dev 10 seeds: `4W/0L/6D`, mean `+12.2`, worst `0`.
Stress 621-632: `4W/0L/8D`, mean `+4.5833`, worst `0`.
Combined 22 distinct burned seeds: `8W/0L/14D`, mean `+8.0455`, SE `3.1742`, mean-2SE `+1.6970`, worst `0`, best `+55`.

This satisfies the predeclared condition for allocating a fresh sealed block.

## Fresh sealed1 seeds

The following 12 seeds are fixed before any candidate/champion result on them is inspected:

`957488,985781,382781,394323,430506,566548,140231,622742,329503,941134,700022,422167`

Compact-list SHA256:

`4aafd85f727795aecf289fda662b8f2998b910d839b3bf8e026d102e90cc2cf4`

Generation rule: iterated SHA256 of the fixed string
`2aab62a693bd3a357ad87649b8ba90a79b512d383a7694b07bbcdbe0deef48c8|d25-carrot-hold-v1|sealed1|2026-09-27|i`, mapping the first 8 digest bytes into `[100000,999999]`, rejecting duplicates, until 12 seeds were obtained. No gameplay result was consulted in selecting them.

## Planned evaluation

- exact `kaggle-environments==1.32.7`
- exact official Kaggriculture source SHA
- candidate directly versus current champion
- same seed, both seat assignments
- direct final-state `DONE`, 720-turn and exception checks
- report pair W/L/D, mean, SE, mean-2SE, worst/best and seat means

Decision will be made only after the sealed artifact exists. No Kaggle submission is implied.
