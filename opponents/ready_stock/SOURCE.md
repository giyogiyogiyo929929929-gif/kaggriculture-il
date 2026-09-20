# 出典：ready_stock

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-18

| 項目 | 内容 |
|---|---|
| ノートブック | `alperen5252525/kaggriculture-ready-stock-earlier-sales` |
| 取り出し方 | base64 のリテラルを ast で読んで展開。**セルは実行していない**（`scripts\analysis\extract_notebook_agents.py`） |
| SHA-256 | `45628c719dc967f81655c19f70e579c55a5758b9fe75a5fcdad9193eebf6a017` |
| サイズ | 337,376 bytes |
| 系統 | First in Line / Market Rhythm の作者の別作 |
| 安全確認 | `scripts\analysis\audit_agent.py` で、埋め込みソースまで再帰的に危ない import・呼び出しを探した。0件 |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\ready_stock\main.py` を渡す（最後の callable が agent）。
