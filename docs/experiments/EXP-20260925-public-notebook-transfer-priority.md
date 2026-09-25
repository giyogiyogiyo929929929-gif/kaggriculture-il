# EXP-20260925 — Public notebook transfer priorities

## Canonical baseline

- official Champion: `v115_champion_same_turn_open_squeeze.py`
- SHA-256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- formal engine: `kaggle_environments==1.32.7`
- never use v66
- transfer rule: do not copy a full public agent; isolate one mechanism and test it against exact v115

## Priority 1 — guarded four-turn sale reservation

Source lineage:

- Tetsutani — `market-smart-farming-kaggriculture`
- Ahmed Berat Ozer — `kaggriculture-v36-guarded-four-turn-sales`
- public V36 source SHA-256: `7eb5ab6c48581c82906ab6fa6b2cc5c9607513249ef59b2c45fcd6176e8653dd`
- Apache-2.0 public notebook lineage

Mechanism retained for transfer:

- only the existing sale-reservation horizon changes
- for steps 288..695, eligible physically available stock may satisfy a scheduled sale up to four turns early
- future sale quantities, purchase barriers, stock obligations, shop/block boundary and terminal protections remain active

Public independent evidence reported by V36:

- 512 strong recorded opponents: V36 272/240 vs V35 249/263
- paired outcome-point delta +4.492188pp
- paired margin delta +447.205078
- better/worse outcomes 23/0
- 1,856 reacting public-policy games: V36 1784/72 vs V35 1683/117/56
- paired outcome-point delta +3.933190pp
- paired margin delta +446.059267
- better/worse outcomes 101/0

Local candidate:

- builder: `ci/build_v145_public_four_turn_sales.py`
- branch: `eval-v115-v145-public-four-turn-sales-20260925`
- Actions run: `36133205261`
- current decision: KEEP TESTING; no promotion before exact-v115 direct safety plus a genuinely hard public panel

## Priority 2 — hard-opponent evaluation panel

The old six-opponent panel is now considered too easy for rate-oriented selection. In v143 fresh evaluation, exact v115 won all 48 games across:

- starter
- beat_v48
- bl_v20
- bl_v21
- farming_v2
- frontier_prvsiyan

Candidate-minus-Champion was therefore exactly zero in all 24 matched opponent/seed rows and supplied no rating discrimination.

A Champion-only development selection workflow was added:

- workflow: `.github/workflows/v115-hard-panel-selection.yml`
- commit: `566312355c8a4e254cde7a3f0cfd9634884cbc4a`
- run: `36136334727`
- seeds: 520001..520004, both seats; development-only, never final sealed evidence
- candidates: `peak_2950`, `salem_2900`, `score_2820`, `jaxa_2802`, `thomas_router_95`, `tetsutani_ms`, `melon_squeeze`, `shop_router_v7`
- keep an opponent when v115 has any loss/tie or worst seat margin < 5000

Future candidate panels should emphasize selected hard cells and loss-to-tie/win conversions, while keeping direct v115 comparison as a safety gate.

## Lower priority — public room guard

Source:

- Tetsutani — `shape-the-shop-work-the-pasture-kaggriculture`
- acquired decoded source SHA-256: `2b97e2c653018ac4aeffb8463ec91c8f26b097b4cef81289acc25ccdbc68f916`

Mechanism:

- hour 23 only
- estimate shed after carried inventory/current action/buys/fillable sells
- reserve one slot, target 99/100
- add only overflow-avoiding SELLs

Local candidate:

- filename/builder uses version label v144, but `KAGGRICULTURE_CHAT_MODE_v115_r7.md` had already reserved the conceptual v144 label for a later EV-V92 idea; therefore track this candidate by mechanism name `public-room-guard`, not number
- run: `36132699144`
- current decision: KEEP TESTING but lower priority than four-turn sales

Reason for lower priority: capacity guards are safety mechanisms and frequently change actions/cash without converting outcomes. Do not spend sealed seeds unless direct/focused evidence shows meaningful outcome potential.

## HOLD — v143 singleton weak-vote abstention

Formal run `36131371313` succeeded technically.

- burned 641..652: 1W/0L/11T, mean +1, worst 0, only seed651 +12
- fresh 661..672: 0W/0L/12T, mean 0
- fresh public easy panel: 0W/0L/24T candidate-minus-Champion
- candidate/champion exceptions: 0
- fresh seat-specific cancellations: seed663 +50/-50, seed669 +41/-41

Decision: HOLD / DO NOT PROMOTE / DO NOT SPEND SEALED.

Telemetry is limited to already-burned 663/669 plus positive control 651. Do not threshold-sweep this family.

## Interesting but not yet transferable — Sparse Shop Hybrid

Source:

- Kaito Fukami — `103-128-fresh-public-v43-sparse-shop-hybrid`
- Apache-2.0 public notebook
- published main.py SHA-256: `69f06a802b62aa08f28705dab5728eb924bb6a7c23ffe0164f65b104cc3dadf3`

Reported mechanism:

- no opponent-family classifier
- fixed default continuation
- if first public shop is `YARN_STORE`, switch only after step 88
- if second public shop is `YARN_STORE`, switch only after step 153
- child planners stay synchronized every turn
- routes are required to match before their validated branch boundary

Reported same-seed ablation:

- fixed default 20/32
- sparse YARN 30/32

Reported untouched executable panel:

- frozen v42 84/128
- frozen sparse v43 103/128
- worst-opponent cell improved 12.5% -> 50.0%
- zero agent failures

Decision: STATIC AUDIT ONLY for now. v115 already contains shop-dependent lineage, so first prove an equivalent YARN observable branch is absent and that compatible internal continuations exist. Do not import public medoid routes wholesale.

## Rejected / closed public transfers

### Melon Threshold Squeeze opening quantity 10

Public 2749.4 family advocates a smaller opening undercutter and other market-race changes. However this project already tested the opening quantity family; 15 was slightly stronger than 10 in prior matched screens. Do not repeat opening 10 without new causal evidence.

### Broad route/classifier copying

`Breaking the Tie` and similar multi-route policies are useful external references, but broad route import obscures causality and can splice incompatible farm states. Prefer one observable branch or one market rule at a time.

### Six-sheep expansion

Public V35 reports the selected six-sheep candidate added four better and one worse outcome versus its cash-probe parent on 320 consumed strong records. This is materially less clean than the four-turn-sale evidence and changes production state. Keep lower priority until market-only candidates are exhausted or local telemetry identifies a repeatable production deficit.

## Next order

1. Finish `public-room-guard` screen and stop it if effect is negligible/regressive.
2. Run guarded four-turn sales against exact v115.
3. Finish Champion-only hard-panel selection.
4. If four-turn sales is direct-safe and active, evaluate candidate vs Champion on the selected hard opponents with same seeds and both seats.
5. Telemetry only on rows with outcome/margin differences.
6. Only after hard-panel benefit and no important regression: fresh stress, then unused sealed, then runtime final.
7. If guarded four-turn sales fails, return to the EV singleton idea using existing `_r37_quote_priority` exposure, replay confidence and future predicted quantity rather than a raw threshold sweep.
