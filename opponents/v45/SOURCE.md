# 出典：v45

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-19（UTC、夜）
関連: doc 07 §5, EXP-20260919-17

| 項目 | 内容 |
|---|---|
| ノートブック | `ahmedberatozer/kaggriculture-v45-first-turn-wheat-round-trip` |
| 取り出し方 | `SOURCE_BYTES = b''.join(...)` を ast で読んで連結。**セルは実行していない**（スクラッチパッド `extract_batch3.py`） |
| SHA-256 | `2536d41ed5a00c75204b6350f1c76c54259c774cb065ba2a3a0072eedf210d94` |
| サイズ | 329,112 bytes |
| 系統 | V47 系 |
| 安全確認 | 取り出したソースと、その中で `exec` される埋め込みソースを再帰的に ast でたどり、危ない import・呼び出しを探した。0件 |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\v45\main.py` を渡す（最後の callable が agent）。
