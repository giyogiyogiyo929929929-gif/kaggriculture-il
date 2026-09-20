# 出典：more_yield

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `ahmedberatozer/more-yield-smarter-labor` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `2443cfe9c46a7a6572d855ea84fb6344b288b4132a93fcfa32891e1c2c365182` |
| サイズ | 285,101 bytes |
| 系統 | V47 系の作者の別作 |
| 安全確認 | `scripts\analysis\audit_agent.py`：注意0件。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\more_yield\main.py` を渡す（最後の callable が agent）。
