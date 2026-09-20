# 出典：kf_v43

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-20

| 項目 | 内容 |
|---|---|
| ノートブック | `kaitofukami/103-128-fresh-public-v43-sparse-shop-hybrid` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（**セルは実行していない**。ast でリテラルだけ読む） |
| SHA-256 | `69f06a802b62aa08f28705dab5728eb924bb6a7c23ffe0164f65b104cc3dadf3` |
| サイズ | 63,309 bytes |
| 系統 | Kaito Fukami の v43（店が少ないときの併用型） |
| 安全確認 | `scripts\analysis\audit_agent.py`：`import sys` などの標準ライブラリのみ（危ない呼び出しは無し）。読み込み＋72ステップの試合で動くことを確認済み |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\kf_v43\main.py` を渡す（最後の callable が agent）。
