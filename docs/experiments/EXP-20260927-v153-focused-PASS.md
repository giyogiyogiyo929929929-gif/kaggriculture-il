# EXP-20260927 v153 focused PASS

## Decision

**FOCUSED GATE PASS. KEEP TESTING. DO NOT PROMOTE YET.**

Formal champion remains exact v147:

- source: `v147_candidate_confirmed_v111_clone.py`
- SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- engine: `kaggle_environments==1.32.7`

## v153 identity

Candidate mechanism: v152 dense leading-SELL self-impact exposure ordering plus the empty-leading-order guard only.

Formal Windows build from run `36256621802`:

- v153 SHA256: `26c756e5a1acc78bae124775da4d79239ed2b8c755a39cdada55d9aca551d2d4`
- v147 SHA256 assertion: PASS
- `py_compile`: PASS

The previously recorded local LF build SHA `41fcaf176fc379ee42034bd98e853e1d6e6d03f7201a0d05a964a789b84e1c22` is the same source text with LF line endings. Converting that file to CRLF produces exactly the formal SHA `26c756e5...`; therefore the identity difference is line-ending-only, not a tactical/source-text difference. All subsequent formal Windows workflows must pin `26c756e5...`.

## Formal focused result

Run: `36256621802`
Opponent: `score_2820`
Seed: `520104`
Seats: both

Result relative to v147:

- candidate-minus-champion money: `+20 / +20`
- matched pair: `+20`
- candidate margin: `+34 / +34`
- champion margin: `-9 / -9`
- margin improvement: `+43 / +43`
- seat0 mean: `+20`
- seat1 mean: `+20`
- candidate external exceptions: `0`
- champion external exceptions: `0`

The priority hard loss is converted to a win in both seats.

## v153 telemetry

Both mirrored games report:

- `eligible = 3`
- `changed = 1`
- `errors = 0`

This verifies that the v152 internal `IndexError` issue is removed without changing the source-cell intervention count.

## Causal interpretation

The previously established formal ledger attribution remains valid: only step649 changes, and the final +43 relative margin is fully explained by SELL-order competition:

- FERTILIZER relative effect: `+57`
- WOOL tradeoff: `-14`
- net relative effect: `+43`
- candidate cash effect: `+20`
- opponent cash effect: `-23`
- BUY_PRODUCT FERTILIZER barrier/cost unchanged
- no later action cascade

## Next gate

Burned development seeds `681–692`, both seats, exact v153 vs exact v147. This range is already burned and does not consume sealed information.

Formal direct workflow created after this PASS:

- `.github/workflows/v153-v147-burned-direct-formal.yml`
- run when triggered: formal SHA must be `26c756e5a1acc78bae124775da4d79239ed2b8c755a39cdada55d9aca551d2d4`

Fresh sealed seeds are not used until direct, hard/public regression, telemetry, and runtime gates pass.

No Kaggle submission performed.
