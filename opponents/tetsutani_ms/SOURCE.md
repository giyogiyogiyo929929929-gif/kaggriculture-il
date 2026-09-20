# 出典：tetsutani_ms

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-18

| 項目 | 内容 |
|---|---|
| ノートブック | `tetsutani/market-smart-farming-kaggriculture` |
| 取り出し方 | base64 の tar から main.py を取り出す（ノートブックの EXPECTED_MAIN_SHA256 と一致）。**セルは実行していない**（`scripts\analysis\extract_notebook_agents.py`） |
| SHA-256 | `f6a756cfb900b9d5f499905d596b63f1fde2445342ac4b1ae04e353739bd62d2` |
| サイズ | 333,999 bytes |
| 系統 | tetsutani の Market-Smart 版（tetsutani_dpts の前の系統） |
| 安全確認 | `scripts\analysis\audit_agent.py` で、埋め込みソースまで再帰的に危ない import・呼び出しを探した。0件 |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\tetsutani_ms\main.py` を渡す（最後の callable が agent）。
