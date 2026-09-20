# 出典：v46

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `ahmedberatozer/kaggriculture-v46-first-turn-microstructure-and-s` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `735c370383b70d3bf3aac792f2c147e0afc99166fc9f253ede10e8a030acedb6` |
| サイズ | 333,658 bytes |
| 系統 | V47 系の前版（V46、初手の微調整） |
| 安全確認 | `scripts\analysis\audit_agent.py`：注意0件。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\v46\main.py` を渡す（最後の callable が agent）。
