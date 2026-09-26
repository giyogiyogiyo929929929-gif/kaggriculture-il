# EXP-20260927 v153 — guarded dense self-impact exposure reorder

## Status

**FOCUSED TEST QUEUED. NOT PROMOTED.** Formal champion remains v147 SHA `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`.

## Parent / identity

- parent/champion: exact v147
- parent SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- candidate: v153
- builder: `ci/build_v153_v147_dense_self_exposure_guarded.py`
- branch: `eval-v153-v147-dense-self-exposure-20260927`
- formal engine: `kaggle_environments==1.32.7`
- locally reconstructed v153 SHA256 from exact final-preflight v147 source: `41fcaf176fc379ee42034bd98e853e1d6e6d03f7201a0d05a964a789b84e1c22`
- local `py_compile`: PASS
- local import: PASS

The formal workflow must reproduce the same v153 SHA before its game result is accepted.

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

## Exact causal / ledger attribution

Comparing the original formal v147 ledger with the formal v152 candidate ledger shows an unusually clean intervention:

- both seats have exactly **one action difference in the entire game**, at step649;
- the only action difference is the order of the same leading SELL multiset;
- from step650 onward the candidate has `+20` cash relative to the original v147 trajectory and score_2820 has `-23` cash relative to its original trajectory;
- relative margin is therefore `+43` and remains fixed through the end of the game;
- no later candidate action differs from the original v147 trajectory, so there is no policy-cascade explanation needed.

Item-level market accounting explains the full `+43` margin change:

1. **FERTILIZER**: moving candidate FERTILIZER into the same leading slot as score_2820 changes it from a delayed sale to simultaneous same-item competition. Candidate revenue changes by `+30`; opponent revenue changes by `-27`; relative effect `+57`.
2. **WOOL**: as the tradeoff, candidate WOOL moves from simultaneous competition to one slot after the opponent WOOL. Candidate revenue changes by `-10`; opponent revenue changes by `+4`; relative effect `-14`.
3. Net: candidate `+30-10 = +20`; opponent `-27+4 = -23`; relative margin `+57-14 = +43`.

The later `BUY_PRODUCT FERTILIZER 2` barrier remains in the same position and the amount of FERTILIZER sold before that barrier is unchanged, so this is not a gross-sales artifact caused by a changed repurchase cost.

This exactly reconciles the formal final-money result and provides a reproducible causal explanation for the loss-to-win conversion.

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

Functional diff audit between v152 and v153: apart from identifier/report renaming, the only behavior change is `not orders[0]` in the early guard.

## Focused synthetic checks

Using the exact v147 source recovered from formal final-preflight run `36216080495`:

1. leading empty market order `[[], ...]` returns the parent action unchanged and leaves `_V153_REPORT.errors == 0`;
2. a synthetic dense five-item SELL block is reordered by descending self-impact exposure;
3. the later BUY barrier retains its exact position relative to the leading SELL block;
4. telemetry on the synthetic changed case is `eligible=1`, `changed=1`, `errors=0`.

Synthetic result: **PASS**.

A local microbenchmark of the dense five-item exposure calculation plus stable sort at the source step649 state measured about `0.043 ms` median and `0.116 ms` p99 for the added core computation. This is only an overhead sanity check; formal runtime limits must still be tested later.

## Supporting counterfactual evidence

The separate v147/v111 counterfactual workflow `36250732794` completed successfully. Existing v111 had no change at source step649, supporting that the FERTILIZER-before-MILK improvement is outside the current v111 reachable region rather than a simple threshold miss.

## Focused gate

Workflow run `36256621802` evaluates v153 against exact v147 on `score_2820`, seed520104, both seats under engine 1.32.7.

At latest check the run is queued because self-hosted runner `CIYOI` is occupied by an unrelated v150 hard-opponent regression run. The queued state is not evaluation evidence and the other run is not interrupted.

Required to continue:

- formal v153 SHA equals `41fcaf176fc379ee42034bd98e853e1d6e6d03f7201a0d05a964a789b84e1c22`;
- reproduce `candidate_minus_champion_money = +20/+20` (or otherwise preserve the loss-to-win conversion);
- both seats improve consistently;
- external exceptions `0`;
- `_V153_REPORT.errors == 0` in both seats;
- `_V153_REPORT.changed == 1` in both seats.

If this passes, proceed without sealed seeds to burned direct v147 seeds681..692, both seats, then hard-opponent panel and wash-item net-revenue telemetry before considering fresh sealed seeds.

The next burned-direct workflow is already prepared as `.github/workflows/v153-v147-burned-direct.yml`, but its trigger file has deliberately not been created before the focused gate passes.

## Current decision

- v152 tactical mechanism: promising but implementation rejected for internal errors.
- v153: **KEEP TESTING**.
- formal champion remains v147.
- sealed 721–732 remain burned and are not reused.
- no new sealed seeds consumed.
- no Kaggle submission performed.
