# v94 lineage exact-source manifest

This directory exists only to reproduce the isolated v94 -> v95 evaluation lineage.
It must not be confused with the repository's separate v130+ lineage.

- Formal champion: `champion/v94_adaptive_h14_yarn2_nomilk/main.py`
- Candidate under KEEP TESTING: `candidates/v95_adaptive_h15_yarn2_nomilk/main.py`
- Canonical engine: `kaggle-environments==1.32.7`
- v94 canonical source bytes: 42,987
- v94 source SHA-256: `869b7e9fe727694ca52710716921856fea6511ccae71b0613be26f4e9236baa3`
- v95 source SHA-256: `ba21fe1dcf78113bb5c2531d015f318dbc0af290c608ea5925578b2485ee62cd`

The three `part*.b85` files are the zlib-compressed, Base85-encoded canonical v94
source. The v94 loader reconstructs and hash-checks that source. The v95 loader
applies exactly four audited substitutions and then verifies the v95 hash.

v94 -> v95 audited changes:
1. chase adaptive ceiling: 14 -> 15 when the existing public-state gate allows it.
2. runtime chase ceiling cap: 14 -> 15 under the same gate.
3. MILK exclusion: horizon == 14 -> horizon >= 14.
4. version string only.

Known pre-Actions result: v95 remained KEEP TESTING after fresh 232001..232020,
4W / 0L / 16D, mean +54.45, worst 0, but mean-2SE remained negative because
activation was sparse. Seeds 240001..240040 are reserved as a fresh Actions block.
