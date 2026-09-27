# SEALED RESERVATION — v154 exact-v151

Status: RESERVED, NOT YET CONSUMED.

Candidate: `v154` SHA256 `9643521253a9c3bb41e27d103353f76ac7e805d91cb838559b8227bc93bff593`

Champion: `v151_none_observation_guard` SHA256 `54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31`

Seed selection was preregistered before running the sealed evaluation and without observing outcomes from these seeds.

Deterministic rule:

`start = 700000 + int(candidate_sha256[:8], 16) % 200000`

For v154 this gives `start = 894322`.

Reserved fresh block: `894322..894333` inclusive (12 matched seeds, both seats).

A repository code-search check for the exact start seed `894322` returned zero matches, although GitHub marked that search result `incomplete_results=true`; therefore this is supporting collision evidence, not an exhaustive proof over every historical branch. The high, SHA-derived preregistered range is intended to minimize accidental prior use and eliminate result-driven seed selection.

Do not run this block until burned/hard, internal telemetry/preflight, and runtime/stress gates pass. Creating this reservation does not consume the seeds.

Sealed decision fields to record after first execution: W/L/T, mean, SE, mean-2SE, worst, best, both seat legs, exceptions, internal wrapper errors, activation count, and whether the improvement reproduces rather than merely tying.
