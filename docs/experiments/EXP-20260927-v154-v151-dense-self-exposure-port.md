# EXP-20260927 — v154 exact-v151 dense self-exposure port

## Status

KEEP TESTING. Formal champion remains `v151_none_observation_guard`. No fresh sealed seed spent. No Kaggle submission.

Focused exact-v151 gate passed. Burned/hard qualification is now running as Actions run `36290874071`.

## Parent / champion

- formal champion: `v151_none_observation_guard`
- exact champion SHA256: `54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31`
- lineage: v115 -> v147 -> v150 -> v151
- candidate branch: `eval-v154-v151-dense-self-exposure-port-20260927`
- candidate SHA256: `9643521253a9c3bb41e27d103353f76ac7e805d91cb838559b8227bc93bff593`

## Hypothesis

The v153 dense leading-SELL self-exposure ordering showed a narrowly localized, seat-robust benefit against `score_2820` seed `520104`, but v153 was built on stale formal parent v147. Port exactly that tactical reorder onto exact v151 so that all subsequent evidence is against the current formal champion.

## Changes

One tactical mechanism only:

- steps 288..693, only when the action begins with a contiguous block of at least five distinct SELL items, stable-sort that leading SELL block descending by executable self-impact exposure;
- preserve quantities and never cross the first non-SELL / BUY_PRODUCT barrier.

Compatibility detail: after calling the v151 parent, `observation is None` returns the parent's action unchanged. This preserves v151's existing None-observation safety semantics and is not a new tactical/safety behavior.

Source comparison with the v153 builder confirms the tactical overlay is otherwise the same. The v154 differences are the exact-v151 parent and explicit preservation of v151's `None` guard.

## Historical v153 evidence (not v154 promotion evidence)

v153 was built on exact v147, so these results are hypothesis support only:

- burned direct v153-v147 seeds 681..692: 8W / 0L / 4T, mean +37, worst 0, best +150, exceptions 0;
- hard panel: 8 opponents x seeds 520101..520104 x seat swap = 64 games;
- outcome transitions: W->W 62, L->W 2, regressions 0;
- both L->W are `score_2820`, seed 520104, both seats;
- champion margin -9 -> candidate margin +34; candidate-minus-champion final cash +20 per seat; margin improvement +43;
- runtime stress run 36260008638: v153 5,752 calls, median 2.6585 ms, p99 13.2385 ms, max 199.1765 ms, errors 0. The v147 control in the same run had max 210.2851 ms, consistent with previously observed raw-max/GC noise.

### Causal cell detail from retained v152 focused artifact

The retained precursor artifact from run `36250312541` makes the market-order mechanism concrete. This is historical v152/v153-family evidence, not v154 qualification evidence.

At seed `520104`, step `649`, in both seats:

- before the market action the candidate was behind by 178 cash;
- market inventory included MILK `9888`, with observed MILK price `252`;
- candidate action placed `SELL MILK 9` second in the leading SELL block:
  `FERTILIZER 18 -> MILK 9 -> WOOL 7 -> WHEAT 6 -> EGG 2 -> BUY_PRODUCT FERTILIZER 2 -> ...`;
- `score_2820` used the same relevant sale quantities but delayed `MILK 9` until after `BUY_PRODUCT FERTILIZER 2`:
  `FERTILIZER 18 -> WOOL 7 -> WHEAT 6 -> EGG 2 -> BUY_PRODUCT FERTILIZER 2 -> MILK 9 -> ...`;
- immediately after that market step, the candidate deficit narrowed from `-178` to `-157`, a +21 relative-cash swing in both seats;
- v152 telemetry for this match had `eligible=3`, `changed=1`, with the only changed step being 649 and estimated self-impact delta 57.

This supports a specific interpretation: the useful change is an order-index race on scarce/high-priced MILK, not extra inventory, extra SELL quantity, or a farm-production change. The final v153 hard-cell improvement (+20 candidate cash, margin -9 -> +34) is consistent with that immediate +21 market swing plus later one-dollar cascade/noise. Do not generalize this to every dense block until wider v154 evidence confirms safety.

## v154 focused qualification

Self-hosted run `36284148569`: SUCCESS.

Environment: Python 3.11, `kaggle_environments==1.32.7`, exact v151 reconstructed and SHA asserted before v154 build.

Safety/static:

- v151 SHA matched `54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31`;
- v154 SHA `9643521253a9c3bb41e27d103353f76ac7e805d91cb838559b8227bc93bff593`;
- `py_compile` PASS;
- `observation=None` preserved v151 action exactly: `{'farmer':['PASS'],'hands':[],'market':[]}`;
- v154 telemetry errors after the None test: 0.

Focused `score_2820`, seed `520104`, both seats:

- candidate_minus_champion mean: +20;
- seat0: +20;
- seat1: +20;
- worst: +20;
- best: +20;
- margin improvement mean: +43;
- candidate exceptions: 0;
- champion exceptions: 0;
- v154 telemetry in each seat: `eligible=3`, `changed=1`, `errors=0`.

This is an exact reproduction of the intended v153-family causal cell on the current formal v151 parent. It is still insufficient for PROMOTE by itself.

## v154 evaluation plan

1. Reconstruct exact v151 and assert champion SHA. PASS.
2. Static / syntax check v151 and v154. PASS.
3. Verify `observation=None` preserves v151 PASS action and adds no v154 telemetry error. PASS.
4. Focused `score_2820`, seed 520104, both seats. PASS.
5. Burned direct v154-v151 seeds 681..692 with seat swap. RUNNING.
6. Hard panel seeds 520101..520104 with seat swap; inspect every transition and worst cash regression. QUEUED in same run.
7. Verify internal v154 telemetry errors remain zero on wider evaluation; the current broad workflow gates match exceptions but does not directly aggregate `_V154_REPORT['errors']`, so this must be checked separately before sealed.
8. Runtime/stress on already consumed seeds.
9. Only after the above gates, spend a genuinely unused sealed block.
10. Important-opponent regression plus final formal runtime/preflight before any PROMOTE.

## Orchestration

Focused self-hosted run: `36284148569` — SUCCESS.

Burned/hard run: `36290874071`, triggered by temporary evaluation-only PR #5. Do not merge the trigger PR.

GitHub-hosted fallback run `36284282397` failed before any executable job step was created on both attempt 1 and attempt 2. Attempt 2 again had `runner_id=0`, empty runner name, and `steps=[]`, completing in about two seconds. Treat both as provisioning/infrastructure evidence only, not candidate failure. Do not spend more GitHub-hosted retries unless runner provisioning changes.

Prepared but not triggered before burned/hard passes:

- `.github/workflows/v154-v151-runtime-stress.yml`

## Parallel candidate triage

Run `36283893966` for `v119_multi_premium_race_front` completed successfully as infrastructure, but the candidate itself is REJECT evidence on its own v112 parent:

- validation: 0W / 8L / 4T, mean -156.33, worst -846;
- sealed: 0W / 4L, mean -338.75, worst -1308;
- stress: 0W / 8L, mean -273.625, worst -1233;
- external 40 seed-opponent pairs: no outcome improvements, worst candidate-minus-parent -2.

Do not port v119 to v151.

## Decision rule

Do not PROMOTE from v153 historical evidence or the focused cell alone. Formal baseline is exact v151. Require same-seed seat-swap matched evidence, non-negative worst regression on the qualification panels, zero exceptions/timeouts, zero internal wrapper errors, fresh sealed reproduction, important-opponent regression check, and formal runtime/preflight gates.
