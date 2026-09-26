# uploaded 127ed3 safety-v3 progress — 2026-09-26

## Identity

- parent uploaded candidate SHA256: `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- surviving candidate: safety-v3
- candidate SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- formal champion: `v147_candidate_confirmed_v111_clone.py`
- champion SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- formal engine: `kaggle-environments==1.32.7`
- engine source SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- branch: `eval-uploaded-127ed3-20260926`
- role: candidate only; no champion change is implied by this record

## Hypothesis / changes

Safety-v3 is a robustness-only wrapper over the uploaded candidate's final `ig_agent`. It deletes the stale top-level `agent` binding so the Kaggle-like namespace loader selects the wrapper and converts unexpected exceptions to a legal PASS-shaped action. It is not intended to change valid-game tactics.

Prior focused equivalence established exact final-money equality with raw uploaded tactics on seeds 641 / 350003 / 733 / 911 in both candidate seats, while malformed probes were repaired.

## Formal dev H2H already completed

Actions run `36236548782`, ten burned dev seeds, both seats, exact engine/champion/candidate SHA checks.

- matched pairs: 10
- W/L/D: **8/2/0**
- mean `candidate_minus_champion`: **+688.5**
- median: **+392**
- worst regression: **-520**
- best improvement: **+3428**
- seat0 mean = seat1 mean = **+688.5**
- exceptions: **0**
- non-DONE: **0**

Losses were seed641 `-406` and seed350003 `-520`; large positive seed733 was `+3428`.

## Burned stress — PASS

Actions run `36237376092`, job `108391507181`; seeds **621–632**, both candidate seats, exact `kaggle-environments==1.32.7` and exact source / candidate / champion SHA checks.

`candidate_minus_champion = candidate - champion`.

| seed | pair mean | result |
|---:|---:|:---:|
| 621 | -946 | L |
| 622 | +1039 | W |
| 623 | +787 | W |
| 624 | +1051 | W |
| 625 | +978 | W |
| 626 | +43 | W |
| 627 | +79 | W |
| 628 | +1468 | W |
| 629 | +524 | W |
| 630 | +1885 | W |
| 631 | +2239 | W |
| 632 | +1133 | W |

Summary:

- W/L/D: **11/1/0**
- mean: **+856.6667**
- median: **+1008.5**
- standard error: **248.2680**
- mean - 2SE: **+360.1307**
- worst regression: **-946**
- best improvement: **+2239**
- seat0 mean = seat1 mean = **+856.6667**
- exceptions: **0**
- non-DONE: **0**

This is positive across a broad already-burned block and is not counted as sealed evidence.

## Dedicated runtime gate — PASS

Same Actions run `36237376092`, serial runtime benchmark matching the v147 methodology: starter opponent, seeds **641 / 642**, both seats.

Acceptance thresholds:

- max game p99 < 50 ms
- worst single turn < 200 ms
- exceptions = 0
- non-DONE = 0

Safety-v3 result:

- median of game medians: **2.08895 ms**
- max game p99: **17.2066 ms**
- worst single turn: **169.2014 ms**
- exceptions: **0**
- non-DONE: **0**
- decision: **PASS**

The earlier broad-H2H 442.9 ms outlier did not reproduce under the dedicated formal runtime methodology. In the same run v147 itself showed a 224.4 ms worst-turn outlier, further supporting use of the dedicated candidate gate rather than isolated timing from unrelated broad H2H.

## Sealed block — RESERVED / RUNNING

After the dev, burned-stress and dedicated-runtime gates passed, a fresh block was allocated only then.

- reserved sealed seeds: **409001–409012**
- repository search before allocation found no `4090xx` usage
- matched pairs: 12 planned
- both seats: yes
- candidate: exact safety-v3 SHA above
- champion: exact v147 SHA above
- workflow: `.github/workflows/uploaded-127ed3-safe-v3-sealed-409001.yml`
- Actions run: `36240493207`
- state at this record: **queued; no result counted yet**

No further candidate tuning may use 409001–409012 after this allocation; the block is now burned regardless of the eventual result.

## CARROT2 behavior-identical trace

The first trace run `36238215853` failed before executing games because the instrumentation source replacement expected the wrong exact source fragment (`src.count(...) == 0`). This was a diagnostic-build failure, not an agent/runtime result and is not counted as evidence.

A corrected insertion uses the unique CARROT2 comparison line only, preserving the original action logic and adding telemetry before the existing WHEAT→CARROT assignment.

- contrast seeds: 641 / 350003 losses, 733 / 911 wins
- both seats
- records: step/day, current WHEAT, 1/2/3-day feed demand, expected WHEAT/CARROT units, prices, value edge, spare seed counters
- corrected Actions run: `36240533437`
- state at this record: **queued; no result counted yet**

The prior broad `_CA_MARGIN` tightening remains REJECTED and must not be repeated.

## Known-opponent assets / next gate

The existing formal public panel provides exact repo-resident opponents and runner paths:

- `starter`
- `opponents/beat_v48/main.py`
- `opponents/bl_v20/main.py`
- `opponents/bl_v21/main.py`
- `opponents/farming_v2/main.py`
- `opponents/frontier_prvsiyan/main.py`

The exact Library asset `v134_candidate_center_nonsplit.py` remains fixed at SHA256 `693ca693378f8adae5d57642610ca682e43a03ad636be71141e1615a5e2d1edd`; a different historical builder-derived v134 must not be substituted. Exact `public_main_opponent.py` remains unresolved and must not be silently replaced.

## Decision

Current overall decision: **KEEP TESTING**.

Evidence now supports spending one sealed block: dev signal positive, burned stress strongly positive after seat swap, dedicated runtime passes, malformed-observation robustness passes, and there are no exceptions/timeouts. Promotion is still prohibited until the new sealed block reproduces the improvement and known-opponent regression is checked. Champion remains v147. No Kaggle submission is performed.

## Next hypothesis / action order

1. Complete sealed 409001–409012 and aggregate matched-pair W/L/D, mean, mean-2SE, worst regression and seat dependence.
2. If sealed survives, run the six exact repo-resident public-panel opponents using the existing formal panel runner and compare safety-v3 against v147 under identical seeds.
3. Run exact v134 separately when its exact bytes are available to the formal runner; do not substitute the historical builder version.
4. Inspect corrected CARROT2 trace for a condition that separates loss seeds from win seeds before creating any new CARROT2 candidate.
5. Only after sealed + regression + runtime + mechanism review decide PROMOTE / KEEP TESTING / REJECT.
