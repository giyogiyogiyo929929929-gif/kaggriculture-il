# 出典：most_powerfull

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `flexonafft/kaggriculture-most-powerfull-route` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `e676617138b476ecf9685cb47abf7badae9bcd6e5359fcd733c3ab8f8c3e53e5` |
| サイズ | 267,231 bytes |
| 系統 | Igor Zharov の巡回型 |
| 安全確認 | `scripts\analysis\audit_agent.py`：注意0件。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\most_powerfull\main.py` を渡す（最後の callable が agent）。
