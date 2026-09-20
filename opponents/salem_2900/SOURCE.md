# 出典：salem_2900

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-18

| 項目 | 内容 |
|---|---|
| ノートブック | `salemali7/kaggriculture-2900` |
| 取り出し方 | `%%writefile main.py` のセル本文。**セルは実行していない**（`scripts\analysis\extract_notebook_agents.py`） |
| SHA-256 | `01f0cd470f669f86d4b53eb5b014614d3b383970d0755f119de14153fd77c1eb` |
| サイズ | 18,499 bytes |
| 系統 | 小さめの独自実装（18,499 バイト） |
| 安全確認 | `scripts\analysis\audit_agent.py` で、埋め込みソースまで再帰的に危ない import・呼び出しを探した。0件 |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\salem_2900\main.py` を渡す（最後の callable が agent）。
