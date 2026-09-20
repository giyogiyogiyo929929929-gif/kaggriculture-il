# 出典：pipe8

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-18

| 項目 | 内容 |
|---|---|
| ノートブック | `nathanjacob/kaggriculture-pipe-8-clean-opening` |
| 取り出し方 | base64 のリテラルを ast で読んで展開。**セルは実行していない**（`scripts\analysis\extract_notebook_agents.py`） |
| SHA-256 | `bdebd4ea8aafb727aa025b2ebe7ec19509571d4501759d537da54ec4ab152c6c` |
| サイズ | 329,047 bytes |
| 系統 | 「Pipe-8」系の序盤最適化 |
| 安全確認 | `scripts\analysis\audit_agent.py` で、埋め込みソースまで再帰的に危ない import・呼び出しを探した。0件 |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\pipe8\main.py` を渡す（最後の callable が agent）。
