# 出典：v10_de（v7 ＋ 候補D ＋ 候補E）

状態: 提出候補（doc 07 §9 の受け入れ条件をすべて満たした。**まだ提出していない**）
作成日: 2026-09-20
関連: doc 07 §9・§3 候補D・候補E, EXP-20260920-21（D の探索）・24（E）・25（D+E）, doc 06（提出の運用）

| 項目 | 内容 |
|---|---|
| 元 | `submissions\v8_lategate\main.py`（＝`v7_relax` ＋ 候補D）の末尾に候補E の層を足したもの |
| いちばん下の土台 | `submissions\thomas_v94\main.py`（thomastschinkel「The 2945 Farm」v9/4、Apache-2.0） |
| 作り方 | `.venv\Scripts\python.exe scripts\build_v8_lategate.py` → `.venv\Scripts\python.exe scripts\build_v10_de.py` |
| 改変 | **先頭 867,019 バイトは v8_lategate と、そのまた先頭 864,304 バイトは v7 と、856,428 バイトは v9/4 原本と完全に一致**（`tests\test_v10_de.py` で確認） |
| SHA-256（main.py） | `74e52c041ab062f0a3392e0b7d816fa6c91bbc57bf8685aebe5304ba4d7bbbd3`（874,488 bytes） |
| SHA-256（submission.tar.gz） | `c7a825b7bfc74c1911bfa344356df2e21171d41f005e2e3d2429205a9c17f5ef`（530,349 bytes、中身は main.py のみ） |
| エントリ | `_kil_e_agent(observation, configuration=None)`（最後の callable） |
| ライセンス | Apache-2.0 の派生（原本の表示を保持）。候補E の機構は `thomastschinkel/the-metav4-farm-submission-v13`（Apache-2.0）の `_v44y_reorder` に倣った |

## v7 からの違い

- **候補D**（`_kil_d_agent`）：終盤（day 20 以降）だけ、牛乳といちごの RACEGATE 基準価格を一時的に 0 にして
  v9/4 自身の予約を通す。価格30未満では何もしない。**コピーと確定した試合では何もしない。**
- **候補E**（`_kil_e_agent`）：step 216 以降、同じターンに出す SELL のかたまり（2〜6件）を、
  市場の約定ルール（doc 07 §3 E.1b）どおりに手取りを見積もって**順序だけ**並べ替える。
  注文の品目と数量は変えない。探索は 25ms で打ち切る。

## 成績（doc 07 §9.3、EXP-20260920-25）

| 物差し | v7（提出中） | **v10** |
|---|---|---|
| 手元26本（seed 241〜250、各20試合） | 189勝71敗 | **202勝58敗**（勝ちが減った相手は0本） |
| `v49`・`v50`・`tetsutani_dpts_b`（**未使用 seed 251〜280**、各60試合） | 52勝38敗 | **63勝27敗** |
| コピー3本 | 10勝0敗 | 10勝0敗（金額は +1,407〜+1,456 と上積み） |
| `metav4_v13` seed 1〜20 / 241〜250 | 5勝15敗 / 5勝5敗 | **8勝12敗 / 5勝5敗** |

- preflight 全項目 OK。1ターンの推論は中央値 0.61ms / 99%点 5.16ms / 最悪 44.83ms（NFR-1）。
- テスト：`tests\test_v10_de.py`（8件）、`tests\test_v9_reorder.py`（13件）、`tests\test_v8_lategate.py`。リポジトリ全体で210件合格。

## 提出コマンド（**ユーザーが実行**）

**出す前にチームで合わせること。** 有効な2枠は v7（56376573）と k256net の 56384238 で、
**新しく出すと古いほうの v7 が外れる**（doc 06）。

```cmd
.venv\Scripts\kaggle.exe competitions submit kaggriculture -f submissions\v10_de\submission.tar.gz -m "v10: v7 + late RACEGATE (milk/strawberry) + same-turn SELL reordering; 26 bots 202-58 (v7 189-71), vs v49/v50/dpts_b 63-27 on unused seeds"
```
