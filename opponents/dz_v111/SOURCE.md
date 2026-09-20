# 出典：dz_v111

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `denizeryilmaz/v111-8c4s-economic-core-premium-lead` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `7048e89548f182dfe70da1414fb43f9b3c2c1ca1a6d5e28bb8d6ebea9be1d5a7` |
| サイズ | 18,947 bytes |
| 系統 | 8C4S 系（v16rc5 と同じ型） |
| 安全確認 | `scripts\analysis\audit_agent.py`：注意0件。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\dz_v111\main.py` を渡す（最後の callable が agent）。
