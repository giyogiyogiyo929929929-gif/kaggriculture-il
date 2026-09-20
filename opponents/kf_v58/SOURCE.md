# 出典：kf_v58

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `kaitofukami/238-238-known-streams-v58-minimax-closed-loop` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `b041058ec187a8d0a01edc0eab8de068b53deca3e6c1973faf74ace6916ddcb9` |
| サイズ | 315,484 bytes |
| 系統 | Kaito Fukami の v58（既知の乱数列＋minimax） |
| 安全確認 | `scripts\analysis\audit_agent.py`：`import sys` などの標準ライブラリのみ（危ない呼び出しは無し）。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\kf_v58\main.py` を渡す（最後の callable が agent）。
