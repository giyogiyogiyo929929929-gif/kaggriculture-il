# 出典：reactive_router

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `aurax7/kaggriculture-reactive-router` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `53070a6adfaac7b91914a53e215bf0c521fff1d633db74abdf20bfcd13190175` |
| サイズ | 51,905 bytes |
| 系統 | Yaxon の反応型ルータ |
| 安全確認 | `scripts\analysis\audit_agent.py`：注意0件。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\reactive_router\main.py` を渡す（最後の callable が agent）。
