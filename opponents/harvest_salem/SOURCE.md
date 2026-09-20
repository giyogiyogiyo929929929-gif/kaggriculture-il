# 出典：harvest_salem

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `salemali7/harvest-kaggriculture` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `d39dba50793d9777c990347443bf0c481c78adaea86055f6f6b0600dcfcd9f2e` |
| サイズ | 61,980 bytes |
| 系統 | Salem Ali（indarkarhana/rank-top10 と同一バイト） |
| 安全確認 | `scripts\analysis\audit_agent.py`：注意0件。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\harvest_salem\main.py` を渡す（最後の callable が agent）。
