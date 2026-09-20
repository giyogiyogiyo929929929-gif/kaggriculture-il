# 出典：pipe15

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20
関連: doc 07 §5, EXP-20260920-28（6回目の取り込み）

| 項目 | 内容 |
|---|---|
| ノートブック | `nathanjacob/kaggriculture-pipe15-two-layers`（Kaggriculture Pipe15 Two Layers） |
| 作者 | Nathan Jacob |
| 票数（取得時） | 0 |
| 最終実行（取得時） | 2026-09-20 08:48:04 |
| 取得コマンド | `.venv\Scripts\kaggle.exe kernels pull nathanjacob/kaggriculture-pipe15-two-layers -p <スクラッチ>` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（ast でリテラルのみ）。**セルは実行していない**（AGENTS.md §5） |
| SHA-256 | `ce9ec069d8c72e93751521e6344bbcd2421700f66388633a7b718d479501bc09` |
| サイズ | 866,969 bytes |
| 系統 | nathanjacob の pipe 系（既出の `pipe7`・`pipe8` の後継） |
| 安全確認 | `scripts\analysis\audit_agent.py` で再帰的に検査 → 注意1件：`open(path)`（同上） |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\pipe15\main.py` を渡す（最後の callable が agent）。
