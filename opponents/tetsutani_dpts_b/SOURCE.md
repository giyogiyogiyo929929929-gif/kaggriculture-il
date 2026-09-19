# 出典：tetsutani_dpts_b

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-19（UTC、夜）
関連: doc 07 §5, EXP-20260919-17

| 項目 | 内容 |
|---|---|
| ノートブック | `tetsutani/demand-preserving-turn-sale-timing` |
| 取り出し方 | `ARCHIVE_B64`（tar）を b64 デコードし、中の main.py を取り出す。2026-09-19 15:49 更新版。**セルは実行していない**（スクラッチパッド `extract_batch3.py`） |
| SHA-256 | `1aa3717b3201997a95920c80cf5612c23f78f8716c7b1084b6a345ca4eae7e4f` |
| サイズ | 453,957 bytes |
| 系統 | V47 系（旧版は tetsutani_dpts） |
| 安全確認 | 取り出したソースと、その中で `exec` される埋め込みソースを再帰的に ast でたどり、危ない import・呼び出しを探した。0件 |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\tetsutani_dpts_b\main.py` を渡す（最後の callable が agent）。
