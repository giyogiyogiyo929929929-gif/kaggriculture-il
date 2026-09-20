# 出典：haodou_db

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20
関連: doc 07 §5, EXP-20260920-28（6回目の取り込み）

| 項目 | 内容 |
|---|---|
| ノートブック | `haodou092/notebookdb6965aa8e`（notebookdb6965aa8e） |
| 作者 | haodou092 |
| 票数（取得時） | 2 |
| 最終実行（取得時） | 2026-09-17 15:00:34 |
| 取得コマンド | `.venv\Scripts\kaggle.exe kernels pull haodou092/notebookdb6965aa8e -p <スクラッチ>` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（ast でリテラルのみ）。**セルは実行していない**（AGENTS.md §5） |
| SHA-256 | `211907f56286c11e679ca156c4f944145cd99da1a862c9252183cb673eeeac2f` |
| サイズ | 337,951 bytes |
| 系統 | haodou092（題名なし） |
| 安全確認 | `scripts\analysis\audit_agent.py` で再帰的に検査 → **注意0件** |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\haodou_db\main.py` を渡す（最後の callable が agent）。
