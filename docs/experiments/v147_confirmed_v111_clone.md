# v147 confirmed-v111 clone experiment

Status: **KEEP TESTING** (public gate passed; final runtime/preflight pending)

## Identity

- Formal champion: `v115_champion_same_turn_open_squeeze.py`
- Champion SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- Candidate: `v147_candidate_confirmed_v111_clone.py`
- Candidate SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- Exact builder: `ci/build_v147_confirmed_v111_clone.py`
- Engine for formal evaluation: `kaggle_environments==1.32.7`
- Difference convention: `candidate_minus_champion = candidate - champion`

## Hypothesis

v146's second v111-style order-book pass was useful against clone-like direct opponents but regressed against `beat_v48`. v147 gates that second pass behind an observed confirmation: after a first-pass v111 change, require equal realized one-turn cash deltas for own and rival farms before considering the opponent a confirmed v111-layer clone. If the deltas disagree, reject the second pass for that episode.

This is intended to retain v146's direct gains while avoiding the public-opponent regression.

## Change

One appended wrapper on exact v115:

1. observe the first inherited `_V111_REPORT.changed_turns` transition as a no-intervention probe;
2. on the next observation compare own/rival realized cash delta;
3. only after equality confirmation allow a second `_v111_reorder` pass, still gated by standard configuration and `_v44y_clone_gate`.

No v115 code is overwritten.

## Development / stress evidence

Existing direct/development + stress aggregate before sealed evaluation:

- 38 wins / 0 losses / 10 ties
- worst regression: 0
- `beat_v48` burned check 661-664: no regression
- starter: no regression
- observed candidate exceptions: 0

v146 is superseded because it regressed against `beat_v48` on 3/4 checked seeds.

## Sealed evaluation

Previously untouched seeds 721-732 are now **burned/used** for v147 and must not be reused as a future sealed set.

Matched pairs, both seats:

`[123, 32, 0, 201, 37, 51, 155, 46, 8, 23, 0, 127]`

Aggregate:

- pairs: 12
- wins / losses / ties: **10 / 0 / 2**
- mean candidate_minus_champion: **+66.9167**
- SE: **19.3948**
- mean - 2*SE: **+28.1271**
- worst regression: **0**
- best improvement: **+201**
- seat0 mean: **+66.9167**
- seat1 mean: **+66.9167**
- exceptions: **0**

Thus the effect reproduces out of development and survives seat swap on this sealed set.

## Telemetry / mechanism check

Representative official-engine replays:

- seed 721: diff +123; probes 1; confirmed 1; second_pass_changed 2; errors 0
- seed 724: diff +201; probes 1; confirmed 1; second_pass_changed 3; errors 0
- seed 727: diff +155; probes 1; confirmed 1; second_pass_changed 4; errors 0
- seed 723: diff 0; probes 1; confirmed 1; second_pass_changed 0; errors 0
- seed 731: diff 0; probes 1; confirmed 1; second_pass_changed 0; errors 0

For the sampled sealed games, the candidate differs only when the gated second pass actually changes the order book; sampled no-change games remain equal. This supports the intended mechanism, though it is not by itself a causal proof for every seed.

## Public-opponent reproducibility gate — PASS

Historical v140 calibration target, seeds 641-644:

- starter: `[190, 5, 0, 26]`
- beat_v48: `[1, -16, -1, 0]`
- bl_v20: `[0, 22, 0, 8]`
- bl_v21: `[0, 22, 0, 8]`
- farming_v2: `[1, -16, -1, 0]`
- frontier_prvsiyan: `[93, 2, -1, 0]`

Pinned opponent blobs at commit `a045f9cec962a1ab23b90c7289808ddca65d7597`:

- beat_v48: git blob `bfde138606ff486372a7d5dccbe03634dac5b88b`
- bl_v20: git blob `43d4f52b8c931e67a535b0ba5794f989bde1c116`
- bl_v21: git blob `474585fc7ae1c922e553830d4ba87952dbda0881`
- farming_v2: git blob `000f64b6b9a4273fc52b8c59a8409d1f5e9c1943`
- frontier_prvsiyan: git blob `55e9af781ac03da062a3601a6d3bafee7cf03b14`

Successful formal run:

- GitHub Actions run: `36143337087`
- run head: `504f55bc5e453a51994d5a25f378588c690f005a`
- artifact: `v147-selfhosted-public-panel`
- artifact id: `10877217590`
- artifact digest: `sha256:15a77cfca7c5bf38a28a4d3fbdf9595ee4f75de1dda4d7f08fbe6abbb6c6b05a`
- engine: `kaggle_environments==1.32.7`
- exact historical v140 calibration: PASS before v147 was counted

v147 vs exact v115 result across six public/starter opponents, seeds 641-644, both seats:

- opponents: starter / beat_v48 / bl_v20 / bl_v21 / farming_v2 / frontier_prvsiyan
- matched pairs: **24**
- wins / losses / ties: **0 / 0 / 24**
- mean candidate_minus_champion: **0.0**
- SE: **0.0**
- worst regression: **0.0**
- best improvement: **0.0**
- candidate exceptions: **0**
- champion exceptions: **0**

Every public/starter matched pair was exact equality. The public-opponent regression gate therefore passes.

## Runtime / preflight

Previous local helper timing showed v147 median/p99 essentially equal to v115, but the formal gate remains serial timing on the intended 1.32.7 engine with `p99 < 50 ms`, `worst < 200 ms`, no candidate-specific exceptions/timeouts, and reproducible source identity.

### Official 1.32.7 source / package identity

Pinned identities for the formal runtime path:

- PyPI package: `kaggle-environments==1.32.7`
- PyPI wheel: `kaggle_environments-1.32.7-py3-none-any.whl`
- wheel SHA256: `2a1bb862ad2d6463080f80f6a766f46d94b53fd57168cfeddb9857fc3dbc4c8f`
- Kaggle official repository commit identifying 1.32.7: `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`
- official `kaggle_environments/envs/kaggriculture/kaggriculture.py` SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`

An old engine or reconstructed lookalike is not accepted as formal runtime evidence.

### Historical parity calibration identity

The exact v140 historical calibration candidate is **not** a persisted path such as `submissions/v140_champion_aware_weak_lastresort/main.py`. It is generated from exact v115 by:

- builder: `ci/build_v140_v92_k2_isolated.py`
- builder git blob: `5d9bb6d934a0f0b34934e368eec8bf9878fdda6f`
- exact generated v140 SHA256: `8d96c789bec1b708f38716c96828e366f58fb0cdcc151a1a38c2fc4763a71139`
- original successful calibration run: `36119994714`
- original run engine: `kaggle_environments==1.32.7`

Required historical parity before a newly reconstructed local/runtime path can be trusted:

- seed 641, both seats: v140/v115 = `83887 / 83887`
- seed 642, both seats: v140/v115 = `62145 / 62183`, therefore `candidate_minus_champion = -38`
- seed 643, both seats: v140/v115 = `89373 / 89373`

If these exact cash values do not reproduce, timing from that path is not formal evidence.

### Actions attempts

1. self-hosted run `36163027401` did eventually start. It successfully installed `kaggle-environments==1.32.7`, verified exact v115/v147 construction, and passed loader smoke. It stopped only because the old workflow incorrectly required the `None` member of `BROKEN_OBSERVATIONS` to return a valid action. Since exact v115 and v147 fail `None` identically, this is not a v147 regression.

2. improved self-hosted run `36175051021` also started. It passed official 1.32.7 engine/source identity and exact v115/v147 SHA checks. It then failed before timing because the workflow referenced a nonexistent guessed v140 path. This exposed a calibration-workflow bug, not an agent or engine failure.

3. corrected self-hosted v2 workflow was created at commit `18c148b5fb4da1af039b4dffc8c4cbe8dba0e403`; run `36209345279`, job `108312461572`. It builds v140 through the pinned builder, requires the 641-643 historical parity above, audits broken-observation parity, then measures exact v115/v147 serial runtime on burned seeds 641/642 and both seats. At the latest check the job is still `queued`, `steps=null`, annotations 0: no runner has been assigned and no candidate code has executed.

4. hosted v2 fallback was created at commit `bf5537582cfbb278600fddb2ffb9dc88b02401a2`; run `36209429287`, job `108312706754`. It ended in about two seconds with zero job steps. GitHub's check-run reports `annotations_count=2`, but no executable step or log blob exists. Therefore it is pre-run infrastructure/account evidence, not candidate runtime failure.

No additional sealed seeds were consumed by any runtime attempt.

### Exact local identity reconstruction

On 2026-09-26, the saved `v115_exact.py` was materialized and hashed:

- v115 SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2` — exact match.
- applying the repository's v147 append produced SHA256 `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923` — exact match.
- both sources pass `py_compile`.

The current isolated local container does not have `kaggle_environments`; direct pip/wheel retrieval is blocked by its DNS/network boundary. Official GitHub source retrieval and PyPI release metadata have been independently pinned as above, but a full local `make('kaggriculture')` path has not yet passed the historical cash-parity calibration. Therefore local timing still does **not** replace the formal engine runtime gate.

### Broken-observation gate audit

The repository `scripts/preflight.py` defines:

`BROKEN_OBSERVATIONS = [{}, {"player": 0}, {"farms": []}, {"player": 5, "farms": [{}]}, None]`

Using its Kaggle-like loader/call semantics on the exact v115 and exact v147 sources:

- exported callable: `agent` for both.
- first four broken-observation cases: valid fallback action for both.
- `None`: both exact v115 and exact v147 raise the same `AttributeError` before returning an action.

Therefore a workflow assertion that **all five** broken observations must return a valid action is stricter than the existing formal champion and would reject v115 and v147 equally. `None` is treated as champion-parity/invalid-input audit; actual runtime thresholds remain enforced on valid official observations.

## Decision

**KEEP TESTING. Do not promote yet.**

Completed promotion gates:

1. matched development/stress improvement with worst regression 0;
2. sealed replication on unused seeds 721-732, both seats, mean-2SE > 0, worst regression 0;
3. telemetry mechanism check;
4. exact historical v140 public-panel calibration;
5. v147 vs v115 public/starter panel: 24/24 matched pairs equal, worst regression 0;
6. exact source identity / builder SHA verification.

Remaining promotion gate:

1. final serial runtime on the intended `kaggle_environments==1.32.7` execution environment, requiring `p99 < 50 ms`, `worst < 200 ms`, no candidate-specific exceptions/timeouts, and no material runtime regression versus exact v115.

Do not consume another sealed seed range merely because runtime infrastructure is unavailable. Do not change the formal champion until the runtime gate is complete.