# 出典：farming_v2_b

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-19（UTC、夜）
関連: doc 07 §5, EXP-20260919-17

| 項目 | 内容 |
|---|---|
| ノートブック | `lynnsakurai/farming-score-v2-a-better-approach` |
| 取り出し方 | `SOURCE_BYTES = b''.join(...)` を ast で読んで連結。2026-09-19 12:05 更新版。**セルは実行していない**（スクラッチパッド `extract_batch3.py`） |
| SHA-256 | `177d78bdf00aa96579d98052558e18cd3081d29f855c8a6f20a2bbfebcdbda11` |
| サイズ | 860,103 bytes |
| 系統 | **v9/4 系のコードを含む**（旧版 farming_v2 は V48 系） |
| 安全確認 | 取り出したソースと、その中で `exec` される埋め込みソースを再帰的に ast でたどり、危ない import・呼び出しを探した。注意は開発用の `open(path)`（環境変数 `V92_SELL_LIB` があるときだけ読む v9/4 由来の処理）の1件のみ |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\farming_v2_b\main.py` を渡す（最後の callable が agent）。
