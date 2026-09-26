# EXP-20260927 v153 — guarded dense self-impact exposure reorder

## Status

**FOCUSED TEST RUNNING. NOT PROMOTED.** Formal champion remains v147 SHA `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`.

## Parent / identity

- parent/champion: exact v147
- parent SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- candidate: v153
- builder: `ci/build_v153_v147_dense_self_exposure_guarded.py`
- branch: `eval-v153-v147-dense-self-exposure-20260927`
- formal engine: `kaggle_environments==1.32.7`

## Why v153 exists

v152 formal focused run `36250312541` successfully evaluated the tactical mechanism against `score_2820`, seed `520104`, both seats. The overall workflow was marked failure only because the telemetry assertion detected internal wrapper errors after the game evaluation step.

Formal focused result for v152:

- v147 final money against score_2820: `148746` vs `148755` in both seats (margin `-9`)
- v152 final money: `148766` vs `148732` in both seats (margin `+34`)
- `candidate_minus_champion_money`: `+20 / +20`; pair `+20`
- margin improvement: `+43 / +43`
- seat0 mean: `+20`
- seat1 mean: `+20`
- external evaluator exceptions: `0`
- v152 source SHA256 from formal run: `09c9eec44ce3eadf649554a98b367d23c3391e1d457c839b4cb2d29086bed0fc`

This is a clean loss-to-win conversion on the priority hard cell.

## v152 bug found by telemetry

The candidate ledger completed and reported, in each mirrored seat:

- `eligible=3`
- `changed=1`
- `errors=11`

The internal errors were not failures of the self-impact scoring formula. At steps including 474, 569, 573, 670, 671, 677, 686, 687, 688, 689 and 690, the inherited action contained a leading empty market order `[]`. v152 evaluated `orders[0][0]` before checking whether the first order was non-empty, causing `IndexError`. The wrapper caught the exception and returned the parent action, which is why the formal game still completed with external exceptions zero.

## v153 change

v153 keeps the v152 tactical rule unchanged and adds only an empty-leading-order guard:

```python
if not (288 <= step < 694) or not orders or not orders[0] or orders[0][0] != "SELL":
    return action
```

No scoring thresholds, order quantities, BUY barriers, farm actions, opening policy or terminal behavior change relative to v152.

## Supporting counterfactual evidence

The separate v147/v111 counterfactual workflow `36250732794` completed successfully. Existing v111 had no change at source step649, supporting that the FERTILIZER-before-MILK improvement is outside the current v111 reachable region rather than a simple threshold miss.

## Focused gate

Workflow run `36256621802` evaluates v153 against exact v147 on `score_2820`, seed520104, both seats under engine 1.32.7.

Required to continue:

- reproduce `candidate_minus_champion_money = +20/+20` (or otherwise preserve the loss-to-win conversion);
- both seats improve consistently;
- external exceptions `0`;
- `_V153_REPORT.errors == 0` in both seats;
- `_V153_REPORT.changed == 1` in both seats.

If this passes, proceed without sealed seeds to burned direct v147 seeds681..692, both seats, then hard-opponent panel and wash-item net-revenue telemetry before considering fresh sealed seeds.

## Current decision

- v152 tactical mechanism: promising but implementation rejected for internal errors.
- v153: **KEEP TESTING**.
- formal champion remains v147.
- sealed 721–732 remain burned and are not reused.
- no new sealed seeds consumed.
- no Kaggle submission performed.
