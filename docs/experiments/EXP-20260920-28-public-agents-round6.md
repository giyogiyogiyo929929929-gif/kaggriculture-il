# EXP-20260920-28: 公開ノートブックの6回目の取り込み（10本追加）と、新しい強敵 v51

日付: 2026-09-20
関連 doc: 07 §5, 05 §1.1・§8, EXP-20260920-20（5回目）, EXP-20260920-23・27（metav4_v13）
コミット: 未コミット（`opponents\` に10本追加）

## 目的

**公開ノートブックの共有は 9/23 23:59 UTC で締め切り**（doc 06）。締め切り後の顔ぶれは、いま公開されているものとそのコピーで固まる。
5回目（EXP-20260920-20、同日午前）のあとに出たものを取り込み、v10（提出中）と対戦させる。

## 方法

1. `kaggle kernels list --competition kaggriculture --sort-by voteCount / dateRun` を5ページずつ、2通りのソートで取る。
   **出力に em dash が含まれると cp932 で落ちる**ので、`PYTHONIOENCODING=utf-8` を付けて実行すること（今回の教訓）。
2. `opponents\*\SOURCE.md`・`submissions\*\SOURCE.md` に載っているものを引いて未取り込みを出す。
3. **2026-09-17 以降**のものに絞り、エージェントが入っていそうな22本を `kernels pull`。
4. `extract_notebook_agents.py` で取り出し（**セルは実行しない**）、`audit_agent.py` で監査、SHA-256 で重複を除く。
5. `eval.py` で v10 と 10ペア＝20試合（seed 241〜250）。

## 結果1：公開ノートブックは565本に増えた（5回目の時点では305本）

| 区分 | 本数 |
|---|---|
| 公開ノートブック（重複を除く） | **565** |
| 取り込み済み | 59 |
| 未取り込み | 506 |
| **2026-09-17 以降の未取り込み** | **28** |
| そのうち取り出しを試した | 22 |

### 取り出した22本の内訳

| 区分 | 本数 | 中身 |
|---|---|---|
| **v9/4 原本の完全コピー** | **6** | `countering-the-big-3-meta`・`demystifying-2900-meta-reflex-engine-and-bot`・`kaggriculture-auto-top1`・`kaggriculture-top-10-public-bots`・`evgendvorkin/kaggriculture`・`kagriculture-winning-notebook`（すべて SHA `bfee70e9…`） |
| **`metav4_v13` の完全コピー** | **2** | `guruprasaathas111/kaggriculture-master-engine-v4`・`anhadmahajan06/kaggriculture-autonomous-ai-farming-agent`（SHA `9d634946…`） |
| 既出と同一 | 2 | `v48-clear-the-queue`＝`sunil_v8`、`k0013-v46-advance6`＝`ready_stock` |
| 取り出せず | 1 | `flyfarmer-connectome`（候補が見つからない。`TODO(要確認)`） |
| 複数ファイル構成のため見送り | 1 | `2476-8-peak-lightgbm-xgboost`（`importlib` で隣のファイルを読む形。`gods_mode` と同じ方式だが、主張スコアが 2476 と中位なので今回は取らない） |
| **新しく取り込んだ** | **10** | 下の表 |

- **`metav4_v13` は 9/20 公開で、その翌日にはもうコピーが2本ある。** 広まる速さの目安になる。
- 「上位3強への対策（countering-the-big-3-meta）」は、**中身が v9/4 原本そのもの**だった。

## 結果2：取り込んだ10本と v10 の対戦（seed 241〜250、各20試合）

| 名前 | 元のノートブック | v10 の成績 | ペア差 |
|---|---|---|---|
| **`v51`** | ahmedberatozer/kaggriculture-v51-lean-flock | **3勝7敗** | **−827** |
| `pipe16` | nathanjacob/kaggriculture-pipe16-idle-workers | 5勝5敗 | +278 |
| `beat_v48` | shiiin9/beat-v48-100-0-your-herd-is-decided-on-day-6 | 5勝5敗 | +794 |
| `agent_evolution` | yeshawang/kaggriculture-agent-evolution-public-notebook | 5勝5敗 | +904 |
| `zihen_best` | zihengedie/best-version | 6勝4敗 | +911 |
| `haodou_db` | haodou092/notebookdb6965aa8e | 6勝4敗 | +1,266 |
| `dz_more_wheat` | dmitriigluzdov/kaggriculture-more-wheat-smarter-sales | 10勝0敗 | +1,340 |
| `pipe15` | nathanjacob/kaggriculture-pipe15-two-layers | 10勝0敗 | +1,368 |
| `wonderful_life` | hanifnoerrofiq/a-wonderful-life | 10勝0敗 | +1,368 |
| `jaxa_2780` | jaxa623/2780-beyond-48-0-128-128-worlds-with-95-cis | 10勝0敗 | +3,205 |
| **合計** | | **70勝30敗** | |

例外は全対戦で0件。

## 結果3：`v51` は V47 系の明確な上位互換

| 対戦 | 結果 |
|---|---|
| `v50` 対 `v51` | **1勝9敗（−225）** |
| v7 対 `v51` | 3勝7敗（−1,018） |
| v9（候補E 単体）対 `v51` | 3勝7敗（−827） |
| **v10 対 `v51`** | **3勝7敗（−827）** |
| **`metav4_v13` 対 `v51`** | **5勝5敗（−496）** |

- **`v51` は `v50` を 9-1 で圧倒**。`v47`/`v49`/`v50` と先頭 243,448 バイトまで共通で、そこから分岐した後継。
  末尾に `_SL_*`（作業員の動線を詰める層）・`_V13V`（トマトの要求を止める層）などが積んである。
- **v10 は v7 から退行していない**（どちらも 3勝7敗。金額は −1,018 → −827 と +191 改善）。
- **`metav4_v13` のほうが `v51` に強い**（5勝5敗）。v10 は 3勝7敗。

## 分かったこと

1. **手元で v10 が負け越す相手は2本になった**：`metav4_v13`（seed 1〜20 で 8勝12敗）と **`v51`（3勝7敗）**。
   どちらも 9/20 公開。**締め切り直前に強いものが出てくる流れが続いている。**
2. **`v51` は v49/v50 の系統の正常進化**で、こちらの候補D・Eでは埋まらない（v7 → v9 → v10 で金額は +191 しか動かない）。
   負け方の中身はまだ見ていない（次の実験）。
3. **コピーの広まりは速い。** v9/4 は6本、`metav4_v13` は公開翌日で2本。
   最終トーナメントでは「強い公開エージェントのコピー」が相手の中心になる（doc 06）という前提が、改めて裏づけられた。

## 次にやること

- [ ] **`v51` に負ける理由を分解する**（EXP-20260920-19・23 と同じ手順：日ごとの所持金差、生産量、売り方）
- [ ] 9/23 の締め切りまで、新しい公開ノートブックの取り込みを続ける（残りは分析系が中心だが、上位作者の新作は追う）
- [ ] v10 の本番の公開対戦を分析する（試合が溜まってから）
