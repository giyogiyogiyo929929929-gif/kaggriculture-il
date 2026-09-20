# 出典：pipe7

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `nathanjacob/kaggriculture-pipe-7-wheat-microstructure` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `6150b7f9a953fc54d17a0f762a4c6ba5d2afe25a1851876eeb7681719d34a200` |
| サイズ | 329,111 bytes |
| 系統 | Pipe-7（`pipe8` の前版） |
| 安全確認 | `scripts\analysis\audit_agent.py`：注意0件。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\pipe7\main.py` を渡す（最後の callable が agent）。
