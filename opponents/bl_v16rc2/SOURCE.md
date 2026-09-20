# 出典：bl_v16rc2

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `boatlee/v16-rc2-high-score-near-mirror-market-relay` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `3c6673db13df26939acfea36010c6e8886e26f8487e0e7bdfcbc2e801a1d9891` |
| サイズ | 29,902 bytes |
| 系統 | boatlee の v16-RC2（`submissions\v16rc5` の前版） |
| 安全確認 | `scripts\analysis\audit_agent.py`：注意0件。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\bl_v16rc2\main.py` を渡す（最後の callable が agent）。
