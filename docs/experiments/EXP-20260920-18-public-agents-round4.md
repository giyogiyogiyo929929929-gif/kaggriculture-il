# EXP-20260920-18: 公開ノートブックの4回目の取り込みと v7 との対戦

日付: 2026-09-20
関連 doc: 07_v4_improvement.md §5, 05_evaluation.md §8, EXP-20260919-17（3回目の取り込み）
コミット: （作業中）

## 目的

まだ取り込んでいない公開ノートブックを取り込み、v7（提出済み 56376573）が勝てるかを手元で測る。
9/23 の公開ノートブック締め切りが近く、**最終トーナメントの相手は今の公開エージェントとそのコピーが中心**になるため
（doc 06、doc 08 §2）。

## 方法

1. `kaggle kernels list --competition kaggriculture --sort-by voteCount / dateRun` で一覧を取り、
   `opponents\*\SOURCE.md` に載っていないものを選ぶ（15本）。
2. `kaggle kernels pull` → `scripts\analysis\extract_notebook_agents.py`（**セルは実行しない。ast でリテラルだけ読む**）。
3. `scripts\analysis\audit_agent.py` で、埋め込みソースまで再帰的に危ない import・呼び出しを探す。
4. v9/4 原本（`submissions\thomas_v94\main.py`）と先頭バイトを比べ、既存の相手と SHA-256 が同じものを除く。
5. `scripts\eval.py` で v7 と 10 seed ×席入れ替え＝20試合。

## 結果1：15本のうち、新しい相手は9本だった

| 取り出したもの | サイズ | 判定 |
|---|---|---|
| haideptry/countering-the-big-3-meta | 856,428 | **v9/4 原本と完全一致（コピー）** |
| haideptry/demystifying-2900-meta-reflex-engine-and-bot | 856,428 | **v9/4 原本と完全一致（コピー）** |
| evgendvorkin/kaggriculture | 856,428 | **v9/4 原本と完全一致（コピー）** |
| laveshjadon/kagriculture-winning-notebook | 856,428 | **v9/4 原本と完全一致（コピー）** |
| guruprasaathas111/kaggriculture-master-engine-v4 | 860,103 | 既出（`farming_v2_b` と SHA-256 が同一） |
| ahmedberatozer/kaggriculture-v48-clear-the-queue | 357,742 | 既出（`sunil_v8` と SHA-256 が同一＝あれは V48 だった） |
| leoprovorov/god-s-mode-hacked-stores | 4ファイル | **取り込んだ**（`gods_mode`）。下の「結果3」 |
| 新しい8本 | — | 下の表 |

- **1日で v9/4 の完全なコピーが4本も公開された。** 3回目の取り込み（EXP-17）の時点では master_v3 の1本だけだった。
  コピー対策（v6 の候補A・A2、v7 の候補A3）の価値は上がっている。
- `master-engine-v4` が `farming_v2_b`（Arlene の Farming Score V2）とバイト単位で同じ。作者が違っても中身は同じものが出回っている。

### 取り込んだ8本（`opponents\<名前>\`、SHA-256 は各 SOURCE.md）

| 名前 | ノートブック | サイズ | 系統 |
|---|---|---|---|
| `peak_2950` | haideptry/the-2950-peak-farm | 862,941 | **v9/4 ＋ 別の序盤**（`_ALT_MODE='EarlyCycle'`）。作者の記載は Dmitrii Gluzdov＝`smaller_market_shock` と同じ |
| `yummers` | romantamrazov/kaggriculture-yummers | 859,231 | **v9/4 系 ＋ 独自の ORDERPRI2 層**（相手の売れる在庫の見積りで売り順を決める） |
| `score_2820` | seyitkaangunes/kaggriculture-2820-score | 327,314 | V45/V46 系とみられる別系統 |
| `pipe8` | nathanjacob/kaggriculture-pipe-8-clean-opening | 329,047 | Pipe-8 系の序盤最適化 |
| `ready_stock` | alperen5252525/kaggriculture-ready-stock-earlier-sales | 337,376 | First in Line の作者の別作 |
| `shop_router_v7` | aurax7/kaggriculture-shop-router-reactive-v7 | 347,607 | Shop Router 系 |
| `tetsutani_ms` | tetsutani/market-smart-farming-kaggriculture | 333,999 | tetsutani の Market-Smart 版 |
| `salem_2900` | salemali7/kaggriculture-2900 | 18,499 | 小さめの独自実装 |

安全確認：`peak_2950` と `yummers` は v9/4 由来の `open(path)`（環境変数 `V92_SELL_LIB` があるときだけ読む開発用の処理）が1件。
ほかの6本は0件。

## 結果2：v7 との対戦（10 seed ×席入れ替え＝20試合）

**合計 172勝 8敗。9本すべてに勝ち越した（`gods_mode` を含む。結果3）。**

| 相手 | v7 | 平均差 | v6（比較） |
|---|---|---|---|
| `peak_2950` | **20勝 0敗** | +1,353 | **0勝 20敗（−50）** |
| `yummers` | **20勝 0敗** | +1,787 | 16勝 4敗（+1,073） |
| `score_2820` | 20勝 0敗 | +3,861 | — |
| `pipe8` | 20勝 0敗 | +3,835 | — |
| `salem_2900` | 20勝 0敗 | +31,816 | — |
| `gods_mode` | 20勝 0敗 | +1,239 | 20勝 0敗（+1,239、20試合すべて所持金が完全一致） |
| `ready_stock` | 18勝 2敗 | +2,749 | — |
| `shop_router_v7` | 18勝 2敗 | +3,225 | — |
| `tetsutani_ms` | 16勝 4敗 | +3,061 | 16勝 4敗（+3,061、**20試合すべて所持金が完全一致**） |

### なぜ勝てたか

1. **`peak_2950` は候補A3 がそのまま効いた例。** `copy_check window` で 96〜167 ステップの農場が一致し、
   **所持金の差は 50 で一定**（＝序盤の小さな上乗せ）。`smaller_market_shock` とまったく同じ形。
   - v6（所持金込みの厳密な判定）は**コピーと認識できず 0勝20敗、しかも毎試合ちょうど −50**。
     ミラーのまま最後まで進み、相手の序盤の +50 だけが残る。
   - v7（所持金を除き、差が一定ならコピー）は**認識できて 20勝0敗（+1,353）**。
   - **A3 は `smaller_market_shock` 専用の対策ではなく、同じ作者の新作にもそのまま効いた。**
2. **`yummers` でも A3 が効いた。** 所持金の差は 0〜2 で一定。v6 は差が 0 の seed では勝てるが、
   **差が出る seed では認識できず 4敗**。v7 は 20勝0敗（20試合中6試合で v6 と結果が変わった）。
3. 別系統（`score_2820`・`pipe8`・`salem_2900` など）には、v9/4 の土台の強さがそのまま出て大差で勝っている。

### なぜ負けたか（8敗）

- **8敗すべてが seed 4（`tetsutani_ms` は seed 5 も）で、差は −47〜−149 と極小。** 席を入れ替えても同じ額。
- **原本の v9/4 も同じ seed で同じ額だけ負ける**（`replay_seed.py` で確認：seed 4 の tetsutani_ms −87、
  ready_stock −149、shop_router_v7 −97 ＝ v7 とまったく同じ）。
  → **この負けは自分たちの層が作ったものではなく、土台から引き継いだもの。**
  実際 `tetsutani_ms` との20試合は v6 と所持金が1ドルも違わない（コピー判定が発動しない相手には v6＝v7）。
- 台帳（`ledger_match.py` → `ledger_report.py`）で seed 4 の負けと seed 9 の勝ちを比べると：
  - seed 4：**d25 で +635 勝っていたのが、最後の5日で逆転されて −87**。内訳は
    **羊毛 −685（同じ 148個でも平均 76 対 81）**と**小麦 −743（相手は 29個多く売った）**。にんじんは +1,023 勝っている。
  - seed 9（勝ち）：いちご +445、卵 +626（88個 対 78個）で d23 以降に引き離した。
  - → **負けの形は既知の「終盤に市場が飽和し、相手のほうが少し早く売る」**（EXP-20260919-16 と同じ）。
    seed 4 はほぼミラーで、最後の一週間の羊毛の売り順だけで 87 ドルの差になっている。

## 結果3：`gods_mode`（God's Mode: Hacked Stores）の取り込みと対戦

最初は取り出せなかった。原因は**梱包の形**で、危険なものではなかった。

- セル45 の `PAYLOAD_B85` は **b85 → lzma → 独自の連結形式**（[ファイル数][名前長][名前][サイズ8][中身]…）。
  `extract_notebook_agents.py` は b64/b85 → tar・gzip・zlib しか試さないので外れていた。
  **ast で定数を読み、同じ手順で復元**（セルは実行していない）。ノートブック内の `EXPECTED_SHA256` と**6ファイルすべて一致**。
- 中身：`main.py`(358) ＋ `base_agent.py`(860,103) ＋ `shop_predictor.py`(11,585) ＋ `shop_overlay.py`(13,773)。
  **`base_agent.py` は `farming_v2_b`（＝ Master Engine V4）とバイト単位で同一**で、その上に店の抽選を狙う層が乗っている。
- 主張：店の抽選は `Random((seed*1,000,003) XOR day)` で、**空きマスの数が乱数の消費位置を変える**。
  1マスの `DIG` で次の店が変わったのが 128回中 98回（76.6%）。seed は見えないので**雑草の出方から seed を絞る**。
  狙った店を実際に出せるのは試合の 10〜18%。**著者自身が「店を操れても勝てるとは限らない」と書いている**
  （PET_CAFE を狙った版は元の版より margin が下がった）。
- 安全確認：main.py・shop_predictor.py・shop_overlay.py はいずれも注意0件。

**対戦結果：v7 は 20勝0敗（+1,239）。v6 も同じ 20勝0敗で、所持金は20試合すべて完全一致。**
`copy_check window` では 96〜167 ステップの農場が一致し**所持金の差は 0**。
つまり v6 の厳密な判定でもコピーと分かる相手で、ここは A3 の有無で差が出ない。
→ **「店を操る」路線は、少なくともこの実装では v9/4 系のコピー対策の前に崩れる。** 自分たちが追う価値は低い。

### `scripts\eval.py` の不具合を1つ直した

`gods_mode` は**複数ファイル**のエージェントで、`main.py` が隣の `base_agent.py` を import する。
`eval.py` の `resolve_agent` は**そのフォルダを `sys.path` に入れていなかった**ため `ModuleNotFoundError` になった。
Kaggle 本体と `preflight.load_like_kaggle` は入れている（doc 06「仕様」）。`eval.py` も同じにした（doc 05 §1.1）。
**手元のエージェントは全部1ファイルだったので、今まで表に出ていなかった。** 185件のテストは修正後も全部通る。

## 分かったこと

1. **v9/4 のコピーが急増している。** 1日で完全コピーが4本。コピー対策（v6・v7）の価値は上がった。
2. **v7 の候補A3 は「コピー＋序盤の上乗せ」全般に効く。** 新作 `peak_2950` に対して v6 が 0勝20敗、v7 が 20勝0敗。
   **v7 を提出した判断は正しかった。**
3. **残る負けは土台（v9/4）由来の、終盤の売り順の僅差。** 取り込んだ18本＋9本のうち、勝ち越せない相手は今のところ無い。
4. `master-engine-v4` = `farming_v2_b`、`v48` = `sunil_v8` のように、**別名で同じバイト列が出回っている**。
   取り込み時は SHA-256 で既出かどうかを必ず確かめる。

## 次にやること

1. v7 の公開対戦がたまったら、勝ち負け両方を分析する（`scripts\analysis\live_summary.py`）。
2. **終盤の売り順**（seed 4 の羊毛のような僅差の負け）と **v50 系に約59%** が、残った改善の候補。
   どちらも土台の挙動なので、doc 07 に候補として書いてから着手する。
3. 取り込みの手順に **b85 → lzma → 独自形式** も加える（`extract_notebook_agents.py` は未対応のまま。
   必要になったら足す。`TODO`）。
