# 出典：kf_v48

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `kaitofukami/40-40-early-floor-39-46-top-10-v48-fast-routes` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `dadee25a9840313218384208c53b2c4752f82c3209cc654632e0b96c65e2664a` |
| サイズ | 107,008 bytes |
| 系統 | Kaito Fukami の v48（序盤の底値・速い巡回） |
| 安全確認 | `scripts\analysis\audit_agent.py`：`import sys` などの標準ライブラリのみ（危ない呼び出しは無し）。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\kf_v48\main.py` を渡す（最後の callable が agent）。
