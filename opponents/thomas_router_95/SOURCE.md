# 出典：thomas_router_95

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `thomastschinkel/kaggriculture-95-5-win-rate-via-replay-routing` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `739cef2fee7e37d6b48611ba2fcd05869795a47556143755946c3dbbb6a219ea` |
| サイズ | 65,129 bytes |
| 系統 | **v9/4 の作者の旧版**（リプレイ routing 95.5%） |
| 安全確認 | `scripts\analysis\audit_agent.py`：`import sys` などの標準ライブラリのみ（危ない呼び出しは無し）。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\thomas_router_95\main.py` を渡す（最後の callable が agent）。
