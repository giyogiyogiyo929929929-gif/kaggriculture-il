# uploaded_127ed3_ca_feed0_d25_carrot_hold_v1 — pretest — 2026-09-27

Status: **BURNED DEV QUEUED; NOT PROMOTED**

## Formal champion / parent

- champion: `uploaded_127ed3_ca_feed0`
- SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- builder: `ci/build_uploaded_127ed3_ca_feed0.py`
- engine: `kaggle-environments==1.32.7`
- official source SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`

## Candidate

- name: `uploaded_127ed3_ca_feed0_d25_carrot_hold_v1`
- parent: current formal champion `uploaded_127ed3_ca_feed0`
- SHA256: `2aab62a693bd3a357ad87649b8ba90a79b512d383a7694b07bbcdbe0deef48c8`
- builder: `ci/build_uploaded_127ed3_ca_feed0_d25_carrot_hold_v1.py`
- size: `503060` bytes
- local reconstruction from verified feed0 final-preflight `main.py`: parent SHA matched, candidate SHA matched, `py_compile` PASS.

### Single tactical change

At `observation.step == 600` only, remove market orders whose shape is `SELL CARROT` from the action returned by the parent agent. All other farmer, hands, and market actions are preserved. The CARROT remains in shed and the unchanged parent logic may sell it from the next observation onward.

The builder appends the wrapper to the exact parent bytes; it does not normalize line endings or rewrite the parent source.

## Prior evidence (different parent; context only)

The older candidate `uploaded_127ed3_day25_carrot_hold` was built directly on `uploaded_127ed3_safety_v3`, SHA `96bc8be3cd0159c6c3536ee28a6dd19769cb1b0015c1861c6bf0f1841c283459`.

On focal known seeds `[641,350003,733,911]`, both seats, it produced candidate-minus-safety-v3 deltas:

- 641: `+73`
- 350003: `+8`
- 733: `0`
- 911: `0`

Focal summary: `2W/0L/2D`, mean `+20.25`, worst `0`, best `+73`, exceptions `0`, all games 720 turns.

This is **not** evidence versus the current champion because feed0 changes the parent behavior. It only justifies retesting the isolated market-timing idea against feed0.

## Formal burned dev

Run: `36311006300`

Seeds: `[641,350003,101,211,347,509,733,911,1201,1601]`, both seats, candidate directly versus current feed0 champion.

The workflow asserts exact candidate/champion hashes, engine version, official source SHA, `DONE` statuses, 720 turns, and zero exceptions. It reports W/L/D, mean, SE, mean-2SE, worst/best, seat means, and the original focal-four subset separately.

No fresh/sealed seeds are consumed in this stage.

## Decision rule

- If the old focal effect disappears and the 10-seed block is neutral/negative, REJECT without stress/fresh evaluation.
- If the candidate retains useful positive deltas with no concerning worst regression, proceed to the already-burned stress block 621-632 with seat swap before allocating fresh sealed seeds.
- Formal champion remains feed0 until all promotion gates pass.

No Kaggle submission is implied.
