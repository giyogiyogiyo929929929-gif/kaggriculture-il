# 出典: haodou_db_latest

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-21

| 項目 | 内容 |
|---|---|
| ノートブック | `haodou092/notebookdb6965aa8e` |
| URL | https://www.kaggle.com/code/haodou092/notebookdb6965aa8e |
| 作者 | haodou092 |
| 取得方法 | `.venv\Scripts\python.exe -m kaggle kernels pull haodou092/notebookdb6965aa8e -m` |
| 抽出方法 | `scripts/analysis/extract_notebook_agents.py`（セルは実行せず AST とリテラルだけを読む） |
| SHA-256 | `fd39dffa68e2171fe6fc016b79804b52b862dc5c2af3427e9ca4c54e9fb410d8` |
| サイズ | 1,018,142 bytes |
| ライセンス | Apache-2.0（ソース内の原文と帰属を保持） |
| 系統 | Pipe16 HybridOpening 系。既存 `opponents/haodou_db` の取得後に公開内容が更新されたため別フォルダで保持 |
| 静的監査 | `audit_agent.py` で注意1件。`open(path)` は `path = None` に固定された到達不能な外部ライブラリ読込部 |

公開ノートに期待 SHA は記載されていない。取得したノートから抽出した内容を改変せず保存する。
