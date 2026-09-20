# 出典：tetsutani_adaptive

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `tetsutani/adaptive-farming-strategy-for-kaggriculture` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `c26402b67a0d04a46348353069645b1a49c3cb3df6df69d7fa35d8adbbdbeae4` |
| サイズ | 148,034 bytes |
| 系統 | tetsutani の適応型 |
| 安全確認 | `scripts\analysis\audit_agent.py`：注意0件。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\tetsutani_adaptive\main.py` を渡す（最後の callable が agent）。
