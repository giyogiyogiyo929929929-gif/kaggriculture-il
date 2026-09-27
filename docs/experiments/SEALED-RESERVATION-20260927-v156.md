# SEALED RESERVATION — v156 exact-v151

Status: RESERVED, NOT YET CONSUMED.

Candidate: `v156` SHA256 `14f142f9ca933a208150895e60fa3ee5838d6230782e7fa7807707280b26bcdb`

Champion: `v151_none_observation_guard` SHA256 `54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31`

Seed selection is preregistered before running the sealed evaluation and without observing outcomes from these seeds.

Deterministic rule:

`start = 700000 + int(candidate_sha256[:8], 16) % 200000`

For v156 this gives `start = 855641`.

Reserved fresh block: `855641..855652` inclusive (12 matched seeds, both seats).

A repository code-search check for the exact start seed `855641` returned zero matches. This is supporting collision evidence rather than an exhaustive proof over every historical branch. The high SHA-derived preregistered range is intended to minimize accidental prior use and eliminate result-driven seed selection.

Prerequisite gates completed before this reservation:

- exact-v151 identity/static/focused qualification — PASS;
- strict burned `681..692` seat-swapped gate — PASS;
- strict 8-opponent hard panel — PASS;
- Kaggle loader/malformed-observation preflight and internal telemetry — PASS, errors `0`;
- preregistered repeated runtime characterization — PASS its stated gate: zero errors and v156 wall p99 `<50 ms` in all three repetitions.

Runtime characterization does **not** waive the formal final raw-max threshold. v156 raw max was `194.2144 / 206.0014 / 221.6913 ms` while v151 control was `280.1249 / 344.5302 / 307.7933 ms`; a later strict final runtime gate remains required before PROMOTE.

Creating this reservation does not consume the seeds. The first execution of any seed in `855641..855652` is the sealed evaluation and must be recorded as such.

Sealed decision fields to record after first execution: W/L/T, matched candidate-minus-champion cash deltas, mean, SE, mean-2SE, worst, best, both seat legs, outcome transitions/regressions/improvements, exceptions, internal wrapper errors/telemetry, and whether improvement reproduces rather than merely tying.
