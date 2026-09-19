# 出典：first_in_line

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-19
関連: doc 07 §5, EXP-20260919-13

| 項目 | 内容 |
|---|---|
| ノートブック | `alperen5252525/kaggriculture-first-in-line-stock-into-income` |
| 取り出し方 | `payload`（b64 + zlib）を ast で読んで展開。**セルは実行していない** |
| SHA-256 | `53dc224a75301affb6ba6ea549b6d9842110b6b9913f001510d36991c8dfe07a` |
| サイズ | 357,814 bytes |
| 系統 | V47 / V48 系 |
| 安全確認 | 取り出したソースと、その中で `exec` される埋め込みソースを再帰的に ast でたどり、危ない import（subprocess / socket / urllib / shutil など）と呼び出し（system / popen / urlopen / rmtree など）が0件（EXP-20260919-13） |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\first_in_line\main.py` を渡す（最後の callable が agent）。
