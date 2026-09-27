# SCORES

## Current formal champion

`v151_none_observation_guard`

SHA256: `54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31`

Promoted 2026-09-27 JST. See `docs/experiments/PROMOTE-20260927-v151.md`.

## Promotion evidence summary

| panel | comparison | result | mean delta | worst | notes |
|---|---|---:|---:|---:|---|
| burned 681..692 | v147 vs v115 | 9W / 0L / 3T | +47.5 | 0 | seat swapped |
| sealed 1701..1712 | v147 vs v115 | 10W / 0L / 2T | +36.6667 | 0 | unobserved holdout |
| burned equivalence | v150 vs v147 | 24/24 identical | 0 semantic delta | 0 | v111 evals -21.85% |
| sealed equivalence | v150 vs v147 | 24/24 identical | 0 semantic delta | 0 | v111 evals -18.47% |
| hard opponents | v150 vs v115 | 0W / 0L / 32T | 0 | 0 | 8 opponents, exceptions 0 |
| public diversity | v150 vs v115 | 0W / 0L / 28T | 0 | 0 | 7 opponents, 56/56 absolute wins |
| v151 equivalence | v151 vs v150 | 48/48 identical | 0 semantic delta | 0 | burned + sealed |

`candidate_minus_champion = candidate - champion`.

## Champion runtime

Formal run `36259995740`:

- calls: 7,190
- median: 4.167 ms
- p95: 9.1638 ms
- p99: 16.8518 ms
- max: 162.0771 ms
- CPU max: 171.875 ms
- >200 ms: 0
- errors: 0
- formal runtime gate: PASS

## Champion packaging/preflight

Run `36259834091`:

- Kaggle-compatible loader: PASS
- malformed observations including `None`: PASS
- 720-turn completion: PASS
- stdlib/local imports only: PASS
- package contains exactly root `main.py`
- source SHA256: `54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31`
- archive SHA256: `4220541594344fab249835fa8e453494709eff4b4f3895d764bb9596687a5ad0`
- archive bytes: 621,369

## Historical controls

- v115 former champion SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- v147 strategic parent SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- v150 runtime parent SHA256: `0a5bfa1b9fa91dd7ebdee1f45640719b23a7b895cbd85cc1f4f17bddebb6387d`

Future promotion tests must use exact v151 as the champion. Historical comparison to v115 alone is insufficient for a new PROMOTE.
