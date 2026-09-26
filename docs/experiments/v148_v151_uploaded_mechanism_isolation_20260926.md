# v148-v151 uploaded-mechanism isolation — 2026-09-26

Formal champion remains exact `v147_candidate_confirmed_v111_clone.py`, SHA256 `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`.

Formal engine for local matched evaluation: `kaggle_environments==1.32.7`; official `kaggriculture.py` SHA256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`. The wheel was restored from Actions artifact `10904352331` and source identity rechecked locally.

Difference convention: `candidate_minus_champion = candidate - champion`.

The whole uploaded `main.py` (`127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`) was already REJECTED in `uploaded_main_127ed3e6_eval_20260926.md`. The candidates below are narrow transplants onto exact v147; no candidate becomes champion by construction.

## v148 — isolated IG queue hole-closure

Parent: exact v147.

Hypothesis: zero-stock SELL placeholders create holes that can unnecessarily leave later cash SELLs behind in the market order queue. Port only the uploaded agent's IG hole-closure: replace non-executable cash-product SELLs with empty slots and pull later executable cash SELLs forward. No route/tape, RACE, ADV, terminal, production, or other strategy change.

Candidate SHA256: `6c91924fdc44e1a58b312953a3e0a384c8f8d988ad7cc027ddec7210b1dd8288`.

Static/preflight:
- `py_compile`: PASS.
- malformed-dict parity with champion: first four repository BROKEN_OBSERVATIONS return valid fallback; `None` raises the same `AttributeError` as v147.
- valid-game exceptions: 0 in evaluated games.

Matched direct v148 vs v147, both seats:
- seed 641: pair `0`; IG changed 14 turns, zeroed 14, pulled 0.
- seed 642: pair `0`; changed 19, zeroed 18, pulled 1 across 6 slots.
- seed 643: pair `0`; changed 17, zeroed 17, pulled 1 across 1 slot.
- seed 644: pair `0`; changed 19, zeroed 19, pulled 0.
- seed 645: pair `0`; changed 9, zeroed 9, pulled 0.
- seed 646: pair `0`; changed 18, zeroed 18, pulled 3 across 3 slots.

Aggregate: 0W / 0L / 6D, mean `0`, worst regression `0`, both seats exact equality.

Interpretation: the mechanism genuinely changes returned market arrays, including pulling SELLs on several seeds, but produces no final-cash effect across six existing dev seeds. This is an implementation-active but strategically inert transplant on v147 in this panel.

Decision: **REJECT / no material effect**. No sealed seeds consumed.

## v149 — broad quote-gated R36 reservation

Parent: exact v147.

Hypothesis: port the uploaded RACEPX principle to v147's R36 extra pre-emptive reservation SELLs: do not create reservation SELLs for CARROT/TOMATO/STRAWBERRY/MELON/EGG/MILK/WOOL when current quote is at or below nominal base price. Route/tape and other layers unchanged.

Candidate SHA256: `3d34408c3a7cb9763e4d722d1719fa369304edad47731051bb9b69068db6428c`.

Matched direct v149 vs v147, both seats, seeds 641-644:
- 641: `+2`
- 642: `+197`
- 643: `-121`
- 644: `-573`

Aggregate: 2W / 2L / 0D by sign, mean `-123.75`, worst regression `-573`, best `+197`; both seats agreed within each seed; valid-game exceptions 0.

Decision: **REJECT**. The broad low-quote abstention is seed-dependent and has an unacceptable worst regression.

## v150 — premium-only quote-gated R36 reservation

Parent: exact v147.

Hypothesis: the broad gate may be suppressing products that the uploaded RACEPX notes describe as normally above base. Restrict the same one mechanism to the four premium products explicitly described there as commonly flooded/below-base: STRAWBERRY, MELON, MILK and WOOL.

Candidate SHA256: `088898986d535e99dda654840d0f61e294579904637965e57a402b37a74ea0ee`.

Matched direct v150 vs v147, both seats, seeds 641-644:
- 641: `-330`
- 642: `+197`
- 643: `-147`
- 644: `-573`

Aggregate: 1W / 3L / 0D, mean `-213.25`, worst regression `-573`, best `+197`; valid-game exceptions 0.

Decision: **REJECT**. Further product/threshold tuning on these four seeds would be overfitting and is intentionally stopped.

## v151 — mirror-like classifier + WHEAT BUY-first ordering

Parent: exact v147.

Hypothesis: isolate the uploaded candidate's early behavior-only mirror classifier and WHEAT BUY_PRODUCT-first market ordering on its target first-two-shop pairs. No other uploaded route/tape or market layer is imported.

Candidate SHA256: `020d8a081290bbce0a1ef6e85be5e5d4007309c51da0d295e5591e6119de96a3`.

Matched checks:
- seeds 641-644, both seats: all pair diffs `0`; classifier ran once/game, `mirror_like=0`, `reordered=0`.
- seed 647 has first-two shops `PIZZA_SHOP / SMOOTHIE_SHOP`, one of the uploaded target pairs, but against v147 the classifier still returns `mirror_like=0`; pair diff `0`, reorder count `0`.

Decision: **REJECT / no activation against champion in tested target context**. No sealed seeds consumed.

## Cross-candidate findings

1. The uploaded whole agent's strength cannot be justified by generic `sell_lead/front_run/budget_guard/room_guard/dead_stock/terminal_liquidation` labels. Its chassis disables most of those switches, while later wrappers independently add different mechanisms.
2. IG queue closure is active but cash-neutral on v147 over six dev seeds.
3. A direct RACEPX-style low-quote gate on v147's R36 reservations regresses materially. The narrower premium-only version does not fix it.
4. The uploaded mirror-like WHEAT BUY-first policy does not identify exact v147 as mirror-like under its simple early-WHEAT classifier and therefore does not provide a useful anti-v147 response.
5. The whole-agent ledger result remains the strongest diagnosis: losses were already accumulated before terminal liquidation, with late SELL/order/inventory timing around roughly steps 650-697 dominating; unsold final shed stock was not the cause.

## Decision / next hypothesis

- **Champion stays v147.**
- v148: REJECT (no material effect).
- v149: REJECT (regression).
- v150: REJECT (regression).
- v151: REJECT (no activation/effect).
- No new sealed seeds were consumed.

Do not tune more quote thresholds or item subsets on seeds 641-644. The remaining reusable direction from the upload is a genuinely narrow late-game market-timing rule tied to observed execution/inventory transitions, not a global quote gate and not a wholesale imported route. Any next candidate should stay at 1-3 changes and be evaluated first on burned development seeds with seat swap.