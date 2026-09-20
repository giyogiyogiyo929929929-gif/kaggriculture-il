# 出典：frontier_prvsiyan

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `prvsiyan/kaggriculture-frontier-the-moon-counts-melons` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `02b1fee4b0e48027d4d3baeeb99518346f4fc5a14724cdb202d09a3425b15a79` |
| サイズ | 89,193 bytes |
| 系統 | prvsiyan の Frontier（`the-soil-remembers-rain` と同一バイト） |
| 安全確認 | `scripts\analysis\audit_agent.py`：注意0件。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\frontier_prvsiyan\main.py` を渡す（最後の callable が agent）。
