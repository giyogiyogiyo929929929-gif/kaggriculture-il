# 出典：v38

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `ahmedberatozer/kaggriculture-v38-smarter-feed-stronger-margins` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `bb729e3b189c3f00b51e7c89cf0fd24178a4e0ab4b7c217f5f66ef1d474d9f54` |
| サイズ | 299,349 bytes |
| 系統 | V47 系の前版（V38） |
| 安全確認 | `scripts\analysis\audit_agent.py`：注意0件。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\v38\main.py` を渡す（最後の callable が agent）。
