# 出典：bl_v20

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `boatlee/v20-adaptive-r1-multi-route-agent` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `8ac34abce129cf5c9456776c90edf7d2233b3a280bbdcf7622628825ef3669a0` |
| サイズ | 148,200 bytes |
| 系統 | boatlee の v20（複数巡回） |
| 安全確認 | `scripts\analysis\audit_agent.py`：注意0件。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\bl_v20\main.py` を渡す（最後の callable が agent）。
