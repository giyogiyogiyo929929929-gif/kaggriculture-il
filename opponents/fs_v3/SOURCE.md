# 出典：fs_v3

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `lynnsakurai/farming-score-v3-replay-revised` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `d36ae976ad4a6316e6c1a27a5d04e9cc8e30300f21bdd31e749127c67a9311c4` |
| サイズ | 32,456 bytes |
| 系統 | Arlene の Farming Score V3 |
| 安全確認 | `scripts\analysis\audit_agent.py`：注意0件。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\fs_v3\main.py` を渡す（最後の callable が agent）。
