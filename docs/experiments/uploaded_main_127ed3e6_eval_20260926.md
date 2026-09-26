# Uploaded main.py `127ed3e6` formal evaluation — 2026-09-26

Decision: **REJECT whole-agent candidate**. Formal champion remains exact v147.

## Identity

- Formal champion: `v147_candidate_confirmed_v111_clone.py`
- Champion SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- Uploaded candidate SHA256: `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- Candidate bytes: 501543
- Difference convention: `candidate_minus_champion = candidate - champion`
- Formal engine: `kaggle_environments==1.32.7`
- Wheel SHA256: `2a1bb862ad2d6463080f80f6a766f46d94b53fd57168cfeddb9857fc3dbc4c8f`
- Official `kaggriculture.py` SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- Wheel export Actions run: `36236439116`, artifact id `10904352331`.

## Static / syntax / import

- `py_compile`: PASS.
- Imports are stdlib-only (`__future__`, `base64`, `copy`, `json`, `math`, `zlib`).
- The generic chassis advertises `sell_lead`, `front_run`, `budget_guard`, `room_guard`, `clamp_sells`, `dead_stock`, and `terminal_liquidation`, but actual `_SETTINGS` enables only `sell_lead` among those market layers. The others are false at the chassis setting.
- Later wrappers reintroduce independent mechanisms, including V9 RACE/RACEPX, ready-stock ADV, T62A terminal liquidation, E410, E402, merge and IG queue closure. Therefore the candidate must not be described as simply enabling every chassis switch.

## Preflight

Kaggle-like direct entry audit:

- `{}`: candidate `KeyError('step')`; champion valid fallback.
- `{'player': 0}`: candidate `KeyError('step')`; champion valid fallback.
- `{'farms': []}`: candidate `KeyError('step')`; champion valid fallback.
- `{'player': 5, 'farms': [{}]}`: candidate `KeyError('step')`; champion valid fallback.
- `None`: both candidate and champion fail with `AttributeError`.

Thus the candidate has a malformed-dict robustness regression versus the champion. The out-of-schema `None` case is parity and is not separately counted.

## Matched development gate

Burned development/public seeds 641-644; both seats.

Pair results:

- seed 641: seat0 `-1897`, seat1 `-1897`, pair `-1897`
- seed 642: seat0 `-1373`, seat1 `-28`, pair `-700.5`
- seed 643: seat0 `-1058`, seat1 `-1058`, pair `-1058`
- seed 644: seat0 `+723`, seat1 `+723`, pair `+723`

Aggregate:

- pairs: 4
- W/L/D: **1 / 3 / 0**
- mean candidate_minus_champion: **-733.125**
- worst regression: **-1897**
- best: **+723**
- clear seed dependence; seed642 also shows seat dependence.
- observed game status: DONE; no agent exception in valid-game runs.

This is sufficient to fail the whole-agent promotion gate. No sealed seeds were consumed.

## Runtime observations

Instrumented serial agent-call timings during matched games generally showed candidate median about `0.75-0.98 ms` and p99 about `4.3-6.6 ms`, comfortably below the 50 ms p99 limit. Single-turn worst values were noisy (candidate up to about 259 ms; champion also up to about 266 ms in different seat-swapped games), indicating host scheduling noise rather than a clean candidate-specific worst-turn regression. Since the candidate already fails preflight and strategy gates, no separate final runtime certification was pursued.

## Telemetry / mechanism analysis

Representative candidate telemetry:

| seed | pair tendency | V9 race leads | ADV turns | ADV units | V44Y estimated gain |
| --- | ---: | ---: | ---: | ---: | ---: |
| 641 | -1897 | 110 | 53 | 205 | 809 |
| 642 | loss | 65 | 23 | 74 | 928 |
| 643 | -1058 | 62 | 33 | 106 | 506 |
| 644 | +723 | 26 | 10 | 19 | 588 |

High race/ADV activity correlates with the losing seeds in this small dev sample. V44Y estimated reorder gain does not track the actual outcome and is not accepted as the explanation of strength.

### Seed 641 ledger findings

- Candidate final cash: 63598; champion: 65495; diff -1897.
- By the late game the deficit was already about -1870 at step 697.
- Both sides had zero shed stock before the final acting step, so unsold terminal inventory is not the cause of the loss.
- Endgame liquidation changes only a small remainder of the final difference; the main loss accumulated earlier through market/production scheduling.
- Candidate requested materially different SELL/BUY schedules, including substantially more repeated fertilizer SELL quantity in its action stream and more CARROT seed / WHEAT product purchasing than champion. Raw requested quantities are not treated as executed revenue because engine order/capacity constraints can clamp them.
- Large cash-difference swings occur around late market-order sequences (roughly steps 650-697), confirming that SELL timing/order and inventory timing, not terminal shed residue, dominate this loss.
- Town consumption is explicitly modelled by the V9 race layer: shop drain after every step divisible by 4 and town-centre drain at day boundaries. The losing behavior is therefore not explained by complete absence of Town-consumption modelling; it is an interaction between aggressive sale scheduling/race reservations and the actual market path.

## Isolation experiments

### A. Disable AXIS 2.1 ready-stock ADV

One change: `_ADV_FROM = 719`.
SHA256: `bdb0f327c29c223ea82d7e15374d93fc9a50e0e333c0aafb52fc4cd1d0521c5d`.

Focused seat0 checks:
- seed641: -1555 (improves over whole candidate -1897, still loses badly)
- seed644: +581 (worse than whole candidate +723)

Interpretation: ADV contributes to the seed641 regression but also contributes positive value on seed644. Blanket removal is REJECT.

### B. Disable chassis sell_lead

One change: `_SETTINGS['sell_lead']=False`.
SHA256: `e35a9e93104302485a342f501c6ae211f7e8db086bd59c7d82d41cc52fe759a8`.

Focused seat0 checks:
- seed641: -2016
- seed644: +654

Both are worse than the original candidate on those seeds. Chassis sell_lead is not the primary regression source and appears protective in this route. REJECT.

### C. Enable ADV debt booking

One change: `_ADV_BOOK=True`.
SHA256: `26908c164c1a588ca7413140a070a202c6a2c5b88d71464985d48237946ba30d`.

Focused seat0 checks:
- seed641: -2248
- seed644: +641

The apparent unbooked-ADV issue is not fixed by simply booking debts; both focused results worsen. REJECT.

### D. Gate ADV on cumulative V9 race leads <= 40

One change: apply `_adv_apply` only while `_V9_RACE_REPORT['leads'] <= 40`.
SHA256: `cc5a14c3e616a9ed54cd1c92a57bf5a28ba7c456b98a651a99b84341f302afad`.

Focused seat0 results obtained before stopping:
- seed641: -2001
- seed642: -1483

Both are worse than the original candidate on the same seats. REJECT. Further threshold tuning would overfit the four development seeds.

## Sealed / public-opponent decision

Not run for this whole-agent candidate or its rejected ablations. The candidate fails earlier mandatory gates (preflight robustness and matched champion comparison), so consuming an unused sealed range or running a full known-opponent panel would not be decision-relevant. Seeds 721-732 remain burned from v147 and were not reused.

## Final decision

**REJECT uploaded whole-agent candidate `127ed3e6...c652`. Keep v147 as formal champion.**

The uploaded agent contains useful ideas, but its observed positive result is seed-dependent and cannot be attributed to terminal liquidation, IG queue closure, or a single generic chassis layer. The most promising reusable research direction is a narrower market-timing mechanism derived from the late SELL/race interactions, but it should be transplanted onto v147 as a small 1-3 change candidate rather than switching to this route/tape wholesale.
