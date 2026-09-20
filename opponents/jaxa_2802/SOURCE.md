# 出典：jaxa_2802

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `jaxa623/2802-two-identical-agents-90-points-apart` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `944aa64c5ae1296a9a17eb7961ed8d5a96d0b80183d41e954389983d73420a56` |
| サイズ | 350,794 bytes |
| 系統 | sdy623（同一エージェントの席差の分析に付属する版） |
| 安全確認 | `scripts\analysis\audit_agent.py`：注意0件。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\jaxa_2802\main.py` を渡す（最後の callable が agent）。
