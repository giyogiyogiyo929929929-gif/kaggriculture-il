# 出典：shop_router_v5

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `aurax7/kaggriculture-shop-router-reactive-v5` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `c8d4efda1bae0d73e14022328a8fcda93aee7dff2cd0fc608712972649162bec` |
| サイズ | 339,138 bytes |
| 系統 | Yaxon の Shop Router v5（`shop_router_v7` の前版） |
| 安全確認 | `scripts\analysis\audit_agent.py`：注意0件。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\shop_router_v5\main.py` を渡す（最後の callable が agent）。
