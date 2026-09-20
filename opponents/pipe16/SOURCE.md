# 出典：pipe16

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20
関連: doc 07 §5, EXP-20260920-28（6回目の取り込み）

| 項目 | 内容 |
|---|---|
| ノートブック | `nathanjacob/kaggriculture-pipe16-idle-workers`（Kaggriculture Pipe16 Idle Workers） |
| 作者 | Nathan Jacob |
| 票数（取得時） | 0 |
| 最終実行（取得時） | 2026-09-20 10:43:53 |
| 取得コマンド | `.venv\Scripts\kaggle.exe kernels pull nathanjacob/kaggriculture-pipe16-idle-workers -p <スクラッチ>` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（ast でリテラルのみ）。**セルは実行していない**（AGENTS.md §5） |
| SHA-256 | `827ddf2997fa442e80baadebc4cc91ffaeedec1ff333c1fa7d872b0f1d448181` |
| サイズ | 1,010,931 bytes |
| 系統 | 同上（pipe15 の次の版） |
| 安全確認 | `scripts\analysis\audit_agent.py` で再帰的に検査 → 注意1件：`open(path)`（同上） |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\pipe16\main.py` を渡す（最後の callable が agent）。
