# 出典：shop_router_v7

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-18

| 項目 | 内容 |
|---|---|
| ノートブック | `aurax7/kaggriculture-shop-router-reactive-v7` |
| 取り出し方 | `%%writefile main.py` のセル本文。**セルは実行していない**（`scripts\analysis\extract_notebook_agents.py`） |
| SHA-256 | `08cddb08d30f94c47c66fd9d3d1828a2286180f6859f048483a122246ab208dd` |
| サイズ | 347,607 bytes |
| 系統 | Shop Router 系（町の店に合わせて売る） |
| 安全確認 | `scripts\analysis\audit_agent.py` で、埋め込みソースまで再帰的に危ない import・呼び出しを探した。0件 |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\shop_router_v7\main.py` を渡す（最後の callable が agent）。
