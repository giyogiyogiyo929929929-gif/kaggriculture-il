# 出典：score_2820

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-18

| 項目 | 内容 |
|---|---|
| ノートブック | `seyitkaangunes/kaggriculture-2820-score` |
| 取り出し方 | base64 のリテラルを ast で読んで展開。**セルは実行していない**（`scripts\analysis\extract_notebook_agents.py`） |
| SHA-256 | `797d9bca309d481e18cdbb675ce6d6de9967d266cbafb4c2352c68fb10264e2f` |
| サイズ | 327,314 bytes |
| 系統 | V45/V46 系とみられる別系統 |
| 安全確認 | `scripts\analysis\audit_agent.py` で、埋め込みソースまで再帰的に危ない import・呼び出しを探した。0件 |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\score_2820\main.py` を渡す（最後の callable が agent）。
