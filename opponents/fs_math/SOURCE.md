# 出典：fs_math

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `lynnsakurai/farming-score-a-mathematical-approach` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `1dc166ae2bf0c56a44fac4482f469b8812968c4cb32459cb9860f5077897a7d4` |
| サイズ | 46,342 bytes |
| 系統 | Arlene の数式ベース |
| 安全確認 | `scripts\analysis\audit_agent.py`：注意0件。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\fs_math\main.py` を渡す（最後の callable が agent）。
