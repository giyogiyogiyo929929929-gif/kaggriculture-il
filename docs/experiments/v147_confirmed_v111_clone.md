# v147 confirmed-v111 clone experiment

Status: **KEEP TESTING** (public-opponent gate pending)

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

## Public-opponent reproducibility gate

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

`v147-selfhosted-public-panel.yml` first verifies exact v115/v147 SHA and requires exact v140 calibration before running v147. Previous v143 self-hosted failure was traced to a stale auxiliary source-count assertion after successful agent reconstruction; exact v115 reconstruction itself matched the required SHA.

Current v147 self-hosted run `36143337087` is queued because no self-hosted runner is assigned. Hosted Ubuntu fallback run `36143538053` failed before step 1 (`steps=[]`, runner_id=0), so it is infrastructure evidence only and not a candidate failure.

## Runtime

Local timing showed v147 median/p99 essentially equal to v115. Shared large outliers occurred in both agents in the local environment, so the formal runtime gate remains pending on the intended runner/preflight environment.

## Decision

**KEEP TESTING. Do not promote yet.**

Remaining promotion gates:

1. exact historical v140 public-panel calibration;
2. v147 vs v115 on the same six public/starter panels with no unacceptable regression;
3. final runtime/preflight check;
4. update handover/SCORES and create a new champion artifact only if all gates pass.

Do not consume another sealed seed range merely because infrastructure is unavailable.
