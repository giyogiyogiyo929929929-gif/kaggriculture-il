# uploaded 127ed3 evaluation audit — 2026-09-26 21:47+ JST

## Scope

Audit the uploaded raw candidate and the current safety-v3 / CARROT2 feed2 evaluation path before any promotion decision.

## Champion

- formal champion: `v147_candidate_confirmed_v111_clone.py`
- SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`

## Uploaded raw candidate

- SHA256: `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- size: 501543 bytes
- current upload `main(2).py` was independently re-hashed and is byte-identical to the previously evaluated uploaded candidate.
- syntax / AST: PASS.

## Surviving candidate: safety-v3

- parent: uploaded raw candidate
- SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- change: outer exception-safe final entrypoint only; tactical path remains the uploaded `ig_agent` path.
- formal dev H2H already recorded: 10 matched pairs, both seats, 8W/2L/0D, mean candidate_minus_champion +688.5, median +392, worst -520, best +3428, exceptions 0, non-DONE 0.
- burned stress already recorded: seeds 621-632, 11W/1L/0D, mean +856.6667, mean-2SE +360.1307, worst -946, exceptions 0, non-DONE 0.
- decision remains KEEP TESTING; champion is unchanged.

## Raw-isolation attribution — PASS

Actions run `36242466654`, job `108405426847`, self-hosted Windows X64 runner `CIYOI`.

Compared byte-exact safety-v3 against its byte-exact raw parent on the ten already-burned dev seeds `641, 350003, 101, 211, 347, 509, 733, 911, 1201, 1601`, both seats.

- exact raw SHA256: `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- exact safety-v3 SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- all 20 per-seat deltas: exactly `0`
- matched-pair W/L/D: `0/0/10`
- mean / median / SE / worst / best safety-v3-minus-raw: all `0`
- safety-v3 exceptions: `0`
- raw exceptions: `0`

Conclusion: on this burned dev block the safety-only wrapper is tactically inert. The previously observed improvement versus v147 is attributable to the uploaded raw tactical path, not to the wrapper; safety-v3 retains the raw trajectory while adding the outer exception fallback.

## Sealed seed audit

Two different blocks had been described as sealed:

1. precommitted reservation file `uploaded_127ed3_safety_v3_sealed1_seed_reservation_20260926.md` fixed these 12 seeds before any sealed result was observed:
   `645491, 839835, 927489, 524295, 654541, 709211, 640183, 546018, 709378, 901935, 574041, 685514`.
2. a later workflow used contiguous `409001-409012`.

For auditability, block (1) is the canonical sealed block because it is explicitly precommitted. `409001-409012` must not replace or relabel that reservation.

Created `.github/workflows/uploaded-127ed3-safe-v3-sealed-reserved1.yml` to evaluate the exact precommitted 12 seeds, both seats, exact engine/candidate/champion SHA checks, serial runner, exceptions and short-game gate. At the time of this note the self-hosted job is queued.

Hosted sealed cross-check run `36241495134` failed before any job steps were provisioned (`runner_id=0`, steps empty). This is infrastructure failure, not a candidate loss and not sealed evidence.

## CARROT2 feed2 hypothesis

Trace evidence supports testing a longer FEED reserve horizon before CARROT-for-WHEAT swaps. Existing source uses `_CA_FEED_DAYS = 1`; trace found two-day FEED shortfalls on loss seeds while the one-day guard still passed. The global two-day test uses only already-burned dev seeds.

### Evaluation-runner defect found

The first feed2 workflow had two provenance/execution problems:

- it used a safety wrapper with a different comment string than the exact safety-v3 parent while hardcoding the exact safety-v3 SHA;
- Python commands in Windows PowerShell did not consistently check `$LASTEXITCODE`, so a failed Python `assert` could be followed by later commands and leave the step green;
- the inline `python -` evaluation requested `jobs=2`, which is unsafe for Windows spawn because the stdin `__main__` module is not reliably re-importable.

The failed run `36241085454` therefore is NOT a tactical feed2 result. Its build step completed, but the comparison step failed immediately and produced no valid artifact.

### Corrected exact child

Rebuilt feed2 as exactly one tactical change on the byte-exact safety-v3 parent:

- parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- change: first/only `_CA_FEED_DAYS = 1` -> `2`
- corrected child SHA256: `a2e69e32513280051709bfc921104a3574bc87f484e6a0d1c07466a377e8cc26`
- local exact-byte SHA / AST: PASS
- workflow updated to use the exact parent suffix, explicit Python exit-code checks, and `jobs=1`.
- corrected run is queued on the self-hosted runner.

The previously recorded feed2 SHA `01440baf73114416663588be2a9f44b2873cf77acbf65aaff57791fcb8383fdd` is not the exact safety-v3 child and must not be used for promotion or attribution.

## Environment

Formal workflows target:

- Python 3.11 self-hosted Windows X64
- `kaggle-environments==1.32.7`
- engine source SHA256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`

## Decision

- raw uploaded candidate: promising but not the promotion target; keep as immutable parent/reference.
- safety-v3: raw-isolation PASS and KEEP TESTING pending canonical sealed block and important-opponent regression.
- feed2 exact child: DEV TEST ONLY; no sealed seeds allocated to it.
- champion remains v147.
- no Kaggle submission performed.

## Next action order

1. Run canonical precommitted safety-v3 sealed block and aggregate W/L/D, mean, SE, mean-2SE, worst/best and seat means.
2. If sealed survives, run safety-v3 vs v147 on the exact public regression panel; exact v134 separately when exact bytes are available.
3. Run corrected feed2 only on burned dev seeds. If global feed2 regresses, test the already-identified narrower `day <= 22` two-day reserve as a new child; do not contaminate safety-v3 sealed evaluation.
4. Only after sealed + regression + runtime + mechanism evidence decide PROMOTE / KEEP TESTING / REJECT.
