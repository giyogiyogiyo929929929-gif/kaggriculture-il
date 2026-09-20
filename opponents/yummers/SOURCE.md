# 出典：yummers

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-18

| 項目 | 内容 |
|---|---|
| ノートブック | `romantamrazov/kaggriculture-yummers` |
| 取り出し方 | base64 のリテラルを ast で読んで展開。**セルは実行していない**（`scripts\analysis\extract_notebook_agents.py`） |
| SHA-256 | `2f96c7337019295fc71f3526375078b9364322826e134455048bb3ea4363931f` |
| サイズ | 859,231 bytes |
| 系統 | **v9/4 系＋独自の ORDERPRI2 層**（相手の売れる在庫の見積りで売り順を決める）。原本との共通部分は先頭 808,517 バイト |
| 安全確認 | `scripts\analysis\audit_agent.py` で、埋め込みソースまで再帰的に危ない import・呼び出しを探した。注意は開発用の `open(path)`（環境変数 `V92_SELL_LIB` があるときだけ読む v9/4 由来の処理）の1件のみ |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\yummers\main.py` を渡す（最後の callable が agent）。
