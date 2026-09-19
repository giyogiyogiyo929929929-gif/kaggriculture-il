# EXP-20260919-17: 新しい公開エージェントを取り込み、v6 と対戦させる

日付: 2026-09-19（UTC、夜）
関連 doc: 07_v4_improvement.md §5, EXP-20260919-13, EXP-20260919-16
コミット: （git 未使用）

## 目的

v6 の公開対戦で、手元に無い相手に負けていた（EXP-20260919-16）。公開ノートブックは更新が続いているので、
スコア上位・最近更新されたものを取り込み、v6 が負けないかを手元で確かめる。

## 取り込み（セルは実行していない）

`kaggle kernels list --competition kaggriculture --sort-by scoreDescending` と `--sort-by dateRun` から、手元に無いもの・更新されたものを選んだ。
取り出しはスクラッチパッド `extract_batch3.py`（ast でリテラルだけ読む。`SOURCE_BYTES = b''.join(...)`、base64 の tar、`%%writefile`）。
ノートブックに `EXPECTED_MAIN_SHA256` があるものは全部一致した。安全確認（再帰的な ast 検査）は、v9/4 由来の開発用 `open(path)`
（環境変数 `V92_SELL_LIB` があるときだけ）の2件以外 0件。`opponents\<名前>\`（`main.py` ＋ `SOURCE.md`）に置いた。

| 名前 | ノートブック | 系統 |
|---|---|---|
| v50 | ahmedberatozer/kaggriculture-v50-early-yarn-commit | V47 系の後継 |
| v49 | ahmedberatozer/kaggriculture-v49-funded-sale-timing-and-worker（game-theoretic-master と同一） | V47 系の後継 |
| v45 | ahmedberatozer/kaggriculture-v45-first-turn-wheat-round-trip | V47 系 |
| market_rhythm | alperen5252525/kaggriculture-market-rhythm-sale-policy | First in Line の作者の新作 |
| tetsutani_dpts_b | tetsutani/demand-preserving-turn-sale-timing（15:49 更新版） | V47 系 |
| farming_v2_b | lynnsakurai/farming-score-v2-a-better-approach（12:05 更新版） | **v9/4 系** |
| smaller_market_shock | dmitriigluzdov/kaggriculture-a-smaller-market-shock | **v9/4 ＋ 序盤の小麦1回分** |
| melon_squeeze | goodpjw2008/kaggriculture-melon-threshold-squeeze-2749 | V45 の改変 |

（nusrati/2715-6 は main.py が複数ファイルに分かれていて取り出せず、除外。）

## 結果1：v6 対 新しい8本（各10ペア＝20試合、seed 1〜10）

| 相手 | v6 | 備考 |
|---|---|---|
| **smaller_market_shock** | **0-20-0** | **すべて −50** |
| v50 / v49 / tetsutani_dpts_b | 各 12-8-0 | 負けは seed 4・5・7・8（V47 は 4・5・7） |
| market_rhythm | 14-6-0 | 負けは seed 4・5・7 |
| v45・farming_v2_b・melon_squeeze | 各 20-0-0 | |

- v4 対 farming_v2_b は **0-18-2**（v6 は 20-0）。farming_v2_b は v9/4 に勝つ改変版で、v6 のコピー対策はそれに勝つ。
- v4 対 smaller_market_shock は **0-20-0（すべて −50）**。

## 結果2：smaller_market_shock が v6 に必ず勝つ仕組み

ノートブックの説明：「The 2945 Farm（v9/4）を土台に、序盤に空いている作業員で (2, 4) に小麦を1回育ててから牧草地に戻す。
後の農場と市場の判断は元のまま」。作者の手元では v9/4 に 10勝0敗、差はすべて +50。

v6 と対戦させて、雑草を除いた農場を毎ステップ比べた（seed 3）：

| ステップ | 違い |
|---|---|
| 0 | 一致 |
| 1〜79 | 所持金、タイル (2, 4)、作業員の位置 |
| **80〜最後** | **所持金（−50）だけ** |

→ **80ステップ以降は「所持金が 50 多い v9/4 のコピー」**。v6 のコピー判定は「0〜167 ステップで所持金も含めて完全一致」なので発動せず、
両者は同じ v9/4 のまま打ち、序盤の +50 がそのまま残って負ける。コピーが増えると、このような「コピー＋小さな上乗せ」も増えると考えられる。

## 結果3（探索）：コピー判定をゆるめる

判定を「**96〜167 ステップで、雑草と所持金を除いた農場が一致し続けたらコピー**」に変えた版（スクラッチパッド `build_relax.py`、rx96）。

- **rx96 対 smaller_market_shock：20-0-0（差の平均 +1,353、最小 +330）**。v6 は 0-20。
- **副作用：rx96 は強い公開エージェントの多くにも発動した**（V47 系・v31〜v41・v50・market_rhythm・melon_squeeze で、所持金が v6 と一致したのは 2〜8/20 試合）。
  強い相手は農場の計画がほぼ同じで、96〜167 ステップの農場（所持金を除く）が v9/4 と一致するため（EXP-20260919-16 の「本人の行動 93〜100% 一致」と同じ理由）。
  - seed 1〜10：V47 16-4（v6 14-6）、tetsutani 18-2（同 14-6）、ほかは v6 と同じ成績。v4 相手 seed 71〜90 は v6 と完全一致。
  - seed 11〜40：v47 58-2（v6 58-2）、v50 36-24（同 35-25）、first_in_line 58-2（同 58-2）、**market_rhythm 55-5（v6 59-1）** → **v6 より 4敗多い**。
  → 「強い相手をすべてコピー扱いする」のは損をする相手がある。

## 結果4：コピー＋上乗せと別系統を分ける目印（所持金の差が一定か）

v6 と各相手を 96〜167 ステップまで対戦させ（seed 1〜5）、農場（雑草・所持金を除く）の一致と、所持金の差を見た（スクラッチパッド `money_gap.py`）。

| 相手 | 農場の一致 | 所持金の差の最大 | 差の種類（ステップごと） |
|---|---|---|---|
| **smaller_market_shock** | 5/5 | 50 | **5 seed すべて一定（50）** |
| v47・v50・market_rhythm・melon_squeeze | 4/5 | 40〜1,052（seed 2 は 40〜55） | 3〜17種（一定は 0） |
| v31 | 3/5 | 41〜1,051 | 3〜17種 |
| farming_v2_b・v4 | 5/5 | 0 | 一定（0） |

- **所持金の差の大きさ**では分けられない（seed 2 では V47 系も 40〜55 で、smaller_market_shock の 50 と重なる）。
- **所持金の差が一定かどうか**ではっきり分かれる。コピー（＋上乗せ）は同じ手を打つので差が動かず、別系統は売り買いが違うので差が動く。
- → 判定を「**96〜167 ステップで、雑草と所持金を除いた農場が一致し、かつ所持金の差が一定**」にした版（rx96c）を評価した。

## 結果5：rx96c（所持金の差が一定の条件つき）

| 相手 | rx96c | v6 | 試合ごとの所持金が v6 と完全一致 |
|---|---|---|---|
| **smaller_market_shock**（seed 1〜10） | **20-0-0（平均 +1,353、最小 +330）** | 0-20-0 | — |
| v4（seed 71〜90） | 35-5-0 | 35-5-0 | 40/40 |
| market_rhythm（seed 11〜40） | 59-1-0 | 59-1-0 | 60/60 |
| 手元の公開エージェント 18本（seed 1〜10、各20試合） | v6 と同じ | — | **すべて 20/20** |

→ **smaller_market_shock にだけ発動し、ほかの相手では v6 と1試合残らず同じ。** rx96 の副作用（market_rhythm に4敗多い）は消えた。

## 結果6：v7（候補A3）の受け入れ確認（2026-09-20）

実装 `submissions\v7_relax\main.py`（探索版 rx96c と、定数の名前以外は同じ）。

| 確認 | v7 | 比較 |
|---|---|---|
| smaller_market_shock、**seed 91〜110（どこにも使っていない、40試合）** | **40-0-0（平均 +1,023）** | v6 は seed 1〜10 で 0-20 |
| v4、seed 91〜110（40試合） | 40-0-0（平均 +1,074） | v6 40-0-0（平均 +1,074） |
| 手元の公開エージェント19本（master_v3 を含む、各20試合） | v6 と同じ成績 | **380/380 試合で所持金が v6 と完全一致** |

- preflight 全項目 OK（最悪 49.29ms・99%点 11.14ms）。コピーモード（smaller_market_shock 相手、1プロセス 2試合）：99%点 10.39ms・最悪 130.85ms。例外 0。
- テスト `tests\test_v7_relax.py` 13件、全体 185件が通る。

## 補足：v50 は v6 にとって手強い

v6 対 v50：seed 1〜10 で 12-8、seed 11〜40 で 35-25（合計 47勝33敗、**約 59%**）。V47（約 90%）よりはっきり強い。
v49・tetsutani_dpts_b も seed 1〜10 で 12-8。**別の課題**として記録する（コピー対策とは別の話）。

## 次のアクション

1. v7 を提出する（ユーザー）。有効な2枠は v6・v7 になる。~~v4 が外れる~~ → 訂正（2026-09-20、チーム結成）：
   外れるのはチームメイトの 56357787（v4 は既に有効枠外。doc 06）。
2. v50 系に 59% しか勝てない原因を分析する（勝った試合も負けた試合も）。
