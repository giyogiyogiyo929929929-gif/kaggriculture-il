# 出典：agent_evolution

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20
関連: doc 07 §5, EXP-20260920-28（6回目の取り込み）

| 項目 | 内容 |
|---|---|
| ノートブック | `yeshawang/kaggriculture-agent-evolution-public-notebook`（Kaggriculture Agent Evolution — Public Notebook） |
| 作者 | wadia |
| 票数（取得時） | 1 |
| 最終実行（取得時） | 2026-09-18 00:11:40 |
| 取得コマンド | `.venv\Scripts\kaggle.exe kernels pull yeshawang/kaggriculture-agent-evolution-public-notebook -p <スクラッチ>` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（ast でリテラルのみ）。**セルは実行していない**（AGENTS.md §5） |
| SHA-256 | `c3aea9ca628691a2ceb09825351bbd6362a40ac638b783f673ab11d8bbb503d3` |
| サイズ | 354,289 bytes |
| 系統 | yeshawang |
| 安全確認 | `scripts\analysis\audit_agent.py` で再帰的に検査 → **注意0件** |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\agent_evolution\main.py` を渡す（最後の callable が agent）。
