# 出典：wonderful_life

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20
関連: doc 07 §5, EXP-20260920-28（6回目の取り込み）

| 項目 | 内容 |
|---|---|
| ノートブック | `hanifnoerrofiq/a-wonderful-life`（A wonderful Life） |
| 作者 | Hanif Noer Rofiq |
| 票数（取得時） | 1 |
| 最終実行（取得時） | 2026-09-20 02:27:48 |
| 取得コマンド | `.venv\Scripts\kaggle.exe kernels pull hanifnoerrofiq/a-wonderful-life -p <スクラッチ>` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（ast でリテラルのみ）。**セルは実行していない**（AGENTS.md §5） |
| SHA-256 | `caf490d382731dce2ce85b227b407ddef70c5df88f0773ebe017b695226d3e6d` |
| サイズ | 866,704 bytes |
| 系統 | hanifnoerrofiq。v9/4 系（先頭が共通） |
| 安全確認 | `scripts\analysis\audit_agent.py` で再帰的に検査 → 注意1件：`open(path)`（同上） |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\wonderful_life\main.py` を渡す（最後の callable が agent）。
