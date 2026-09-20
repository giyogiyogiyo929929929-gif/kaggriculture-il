# EXP-20260920-20: 公開ノートブックの5回目の取り込み（28本追加）と v7 との対戦

日付: 2026-09-20
関連 doc: 07_v4_improvement.md §5, 05_evaluation.md §1.1・§8, EXP-20260920-18（4回目）, EXP-20260920-19（v7 の公開対戦）
コミット: （作業中）

## 目的

コンペの公開ノートブック **305本**のうち、まだ取り込んでいないものから強そうなものを取り込み、v7 と対戦させる。
9/23 の公開ノートブック締め切り後、最終トーナメントの相手はここにあるものとそのコピーが中心になる（doc 08 §2）。

## 方法

1. `kaggle kernels list --competition kaggriculture --sort-by voteCount / dateRun` を4ページずつ取り、重複を除いて 305本の一覧を作る。
   `opponents\*\SOURCE.md`・`submissions\*\SOURCE.md` に載っているものを引くと **274本が未取り込み**。
2. そのうち**エージェントが入っていそうな50本**を選んで `kaggle kernels pull`（分析・可視化だけのノートブックは除く）。
3. `scripts\analysis\extract_notebook_agents.py` で取り出し（**セルは実行しない**）、`audit_agent.py` で監査。
4. SHA-256 で既出・重複を除き、**読み込んで72ステップ動かす選別**（`screen5.py`）で使えないものを外す。
5. `scripts\eval.py` で v7 と 10 seed ×席入れ替え＝20試合。

## 結果1：50本 → 使える新しい相手は28本

| 区分 | 本数 | 中身 |
|---|---|---|
| 取り出せた | 38 | — |
| 取り出せなかった | 11 | 候補が複数あって決められない（Hamburger・Structured Economic Policy・Breaking the Tie・Dmitrii の LB2700/2800 など）。`TODO(要確認)` |
| 重複・既出 | 5 | Cloning Agent＝Dynamic Route＝Multi-Route＝**既出の `v45`**、Frontier 2本が同一、Harvest＝rank-top10 |
| **使えない** | 5 | 下の「native な5本」 |
| **取り込んだ** | **28** | `opponents\` に追加（各 SOURCE.md に SHA-256） |

### 使えなかった5本（native ライブラリ方式）

`kaggriculture-apex-v7-god-emperor`・`kaggriculture-adaptive-farm-intelligence`・`three-day-shop-router`・
`shop-router-0908`・`shape-the-shop-work-the-pasture-top-10`。

- 方策の本体が **C++ を別データセットで配る形**（`ctypes` で共有ライブラリを読む）。ノートブックには入っていない。
- **読み込んだだけで C++ コンパイラ（cc1plus）が走った。** ソースが無いので失敗し、以後は市場注文を1件も出さない。
- → **教訓：「セルを実行しない」だけでは足りない。エージェントを読み込むとモジュール直下のコードが走る。**
  `audit_agent.py` が `ctypes` を注意として出していたので気づけた。**監査で `ctypes`・`importlib` が出たら、読み込む前に中身を見る。**

### 取り込んだ28本

`kf_v43` `kf_v48` `kf_v58`（Kaito Fukami）、`bl_v16rc2` `bl_v16rc5a` `bl_v20` `bl_v21` `bl_v29`（boatlee）、
`v38` `v43` `v46` `more_yield`（V47 系の前版）、`thomas_router_74` `thomas_router_93` `thomas_router_95`（**v9/4 の作者の旧版**）、
`fs_math` `fs_v3` `fs_v4`（Arlene）、`tetsutani_adaptive` `tetsutani_shop`、`pipe7`、`reactive_router`、`shop_router_v5`、
`frontier_prvsiyan`、`most_powerfull`、`harvest_salem`、`dz_v111`、`jaxa_2802`。

## 結果2：v7 は 28本すべてに勝ち越し（554勝6敗）

負けたのは2本だけ。

| 相手 | v7 | 平均差 |
|---|---|---|
| `jaxa_2802` | 18勝 2敗 | +3,225 |
| `v46` | 16勝 4敗 | +3,061 |
| `v43` | 20勝 0敗 | +3,953 |
| `pipe7` | 20勝 0敗 | +3,818 |
| `fs_v4` | 20勝 0敗 | +5,290 |
| `shop_router_v5` | 20勝 0敗 | +5,886 |
| `v38` | 20勝 0敗 | +6,294 |
| `more_yield` | 20勝 0敗 | +7,620 |
| `most_powerfull` | 20勝 0敗 | +8,394 |
| `frontier_prvsiyan` | 20勝 0敗 | +9,424 |
| `reactive_router` 〜 `harvest_salem`（17本） | 20勝 0敗 | +16,342 〜 +39,400 |

- **`jaxa_2802` の 18勝2敗・`v46` の 16勝4敗は、`shop_router_v7`・`tetsutani_ms` と同じ数字**（EXP-20260920-18）。
  seed 4 付近の僅差の負けで、**原本の v9/4 も同じ額だけ負ける**既知のもの。新しい弱点ではない。
- **v9/4 の作者（thomastschinkel）の旧版にも大差で勝つ**（74.5% 版 +21,240、93.8% 版 +37,964、95.5% 版 +31,293）。
  v9/4 がその後どれだけ強くなったかがわかる。

### 公開エージェントは互いのコピーが多い

**ファイルが違うのに20試合すべて所持金が1ドルも違わない**組が4組あった。中身を比べると：

| 組 | 類似度 | 違い |
|---|---|---|
| `bl_v20` と `tetsutani_adaptive` | 99.9% | 先頭の docstring だけ |
| `v46` と `tetsutani_ms` | 99.9% | 「相手と所持金が同じときだけ小麦を8個買う」分岐（v7 相手には発動しない） |
| `fs_math` と `tetsutani_shop` | 98.2% | 最終日の売り切り関数の有無 |
| `bl_v16rc5a` と `dz_v111` | — | 同じ 8C4S 系 |

→ **公開エージェントの「本数」は多様さを表さない。** 最終トーナメントの相手は、少数の系統とそのコピーに集中すると考えてよい。

## 結果3：`scripts\eval.py` のエントリ選びの不具合を直した（重要）

- **症状**：`v38`・`v43` との対戦で、相手の最終所持金が**毎試合ちょうど 3,000（初期値のまま）**、平均差 +172,180 になった。
  手元で直接動かすと `v38` は普通に戦う（148,493 対 こちら 150,665）。
- **原因**：`eval.py` は **ast で「最後に def された関数」**をエントリにしていた。
  Kaggle が使うのは**「名前空間の中で最後に現れた callable な値」**（doc 06「仕様」、`preflight.load_like_kaggle` と同じ）。
  `v38` は最後の def が補助関数 `_r86_next_feed`、`v43` は `_r149_deepcopy` で、**そちらを呼ぶと何もしないまま試合が終わる**。
- **影響範囲の確認**：手元の全エージェント（`opponents\*` と `submissions\*` の58本）で両方の規則を比べ、
  **食い違うのは `v38` と `v43` の2本だけ**だった。→ **これまでの評価結果はすべて有効。**
- **直したあと**：`v38` 20勝0敗（+6,294）、`v43` 20勝0敗（+3,953）。
- 回帰テスト：`tests\test_eval.py::test_entry_is_last_callable_value_not_last_def`。
  あわせて EXP-20260920-18 で直した「複数ファイルのエージェント」にもテストを追加
  （`test_multi_file_agent_can_import_sibling`）。**テストは 187件すべて通る。**

## 分かったこと

1. **v7 は手元の公開エージェント58本に 1,126勝74敗。** 勝ち越せない相手は無い。
   負けが残るのは `v50`・`v49`・`tetsutani_dpts_b`（各8敗）＝ **V47/V50 系**と、seed 4 付近の僅差だけ。
2. **native ライブラリ方式のエージェントは手元で評価できない**（本番では動く）。5本は対象外。
3. **読み込むだけで外部コマンドが走ることがある。** 取り込み手順に「監査 → 読み込み」の順を守る理由が増えた。
4. 公開エージェントは互いのコピー・派生が多く、**系統は本数よりずっと少ない**。

## 次にやること

1. 取り出せなかった11本のうち、Dmitrii（`smaller_market_shock`・`peak_2950` の作者）の2本は形が特殊なので、
   必要なら手で復元する（`TODO`）。
2. 残る弱点は **V47/V50 系**と**終盤の牛乳・いちご**（doc 07 候補D、Draft）。どちらも未着手。
