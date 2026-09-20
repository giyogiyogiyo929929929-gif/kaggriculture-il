# 出典：thomas_router_74

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `thomastschinkel/kaggriculture-public-state-router-74-5-win-rate` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `e50d3c7b54c051b880fd7b68ed2aa8f954331d6f892b8fb5dca788223b27c24c` |
| サイズ | 44,954 bytes |
| 系統 | **v9/4 の作者の旧版**（公開状態ルータ 74.5%） |
| 安全確認 | `scripts\analysis\audit_agent.py`：注意0件。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\thomas_router_74\main.py` を渡す（最後の callable が agent）。
