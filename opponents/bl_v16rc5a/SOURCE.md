# 出典：bl_v16rc5a

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `boatlee/v16-rc5-r5a-high-score-8c-4s-recovery` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `168bb38bdac011d74723edce65d88719cc513c2ea639db4b629aa625d3239bc9` |
| サイズ | 23,913 bytes |
| 系統 | boatlee の v16-RC5 R5a |
| 安全確認 | `scripts\analysis\audit_agent.py`：注意0件。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\bl_v16rc5a\main.py` を渡す（最後の callable が agent）。
