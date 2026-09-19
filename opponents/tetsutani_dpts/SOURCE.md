# 出典：tetsutani_dpts

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-19
関連: doc 07 §5, EXP-20260919-13

| 項目 | 内容 |
|---|---|
| ノートブック | `tetsutani/demand-preserving-turn-sale-timing` |
| 取り出し方 | `ARCHIVE_B64`（tar）を b64 デコードし、中の main.py を取り出す。**セルは実行していない** |
| SHA-256 | `95b02b9b7ca124c92844b7c2907b4ceacf2cce7773890cdf32aba84f20eababe` |
| サイズ | 358,258 bytes |
| 系統 | V47 / V48 系 |
| 安全確認 | 取り出したソースと、その中で `exec` される埋め込みソースを再帰的に ast でたどり、危ない import（subprocess / socket / urllib / shutil など）と呼び出し（system / popen / urlopen / rmtree など）が0件（EXP-20260919-13） |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\tetsutani_dpts\main.py` を渡す（最後の callable が agent）。
