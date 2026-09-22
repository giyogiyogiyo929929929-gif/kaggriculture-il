# 出典：pipe18

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-22
関連: EXP-20260922-48

| 項目 | 内容 |
|---|---|
| ノートブック | `nathanjacob/kaggriculture-pipe18-six-layers`（Kaggriculture Pipe18 Six Layers） |
| 作者 | Nathan Jacob |
| 取得コマンド | Kaggle公式CLIの `kernels pull` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（astでリテラルのみ）。**セルは実行していない** |
| SHA-256 | `a4a563c66ea84746cdb5b18341e78d97677ba5a8cef67e9a157afdaf1d6207d7` |
| サイズ | 1,022,762 bytes |
| ライセンス | Apache License 2.0 の本文・帰属表記をソース内で確認 |
| 系統 | V56相当へ CL、Price Guard、Race Horizon、E402、E410、IG Queue Compaction を積層した派生 |
| 静的監査 | 通常経路でネットワーク・subprocessなし。環境変数 `V92_SELL_LIB` 指定時だけ外部ファイルを読む任意経路を1件検出 |
| 実行確認 | 正常な720 stepは完走、中央値0.91ms・99%点5.52ms・最悪77.83ms。ダミー／壊れた観測では `KeyError('step')` のためpreflight 3項目不合格 |

ノートブック内の `EXPECTED_SHA256` と抽出ファイルのSHA-256は一致した。抽出器は変数名
`EXPECTED_MAIN_SHA256` だけを自動認識するため表示上は「期待値なし」だったが、手動照合済み。

末尾のIG層は、説明文の「冗長注文の統合」より限定的で、step 29の牧草地建設復元と、在庫見込みがない
SELL注文を消して後続SELLを空きへ詰める処理である。

**このファイルは改変しない。** 現状は比較相手専用とし、提出ベース候補にするには壊れた観測への安全化と再preflightが必要。
