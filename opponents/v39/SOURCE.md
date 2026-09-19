# 出典：v39

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-19
関連: doc 07 §5, EXP-20260919-13

| 項目 | 内容 |
|---|---|
| ノートブック | `ahmedberatozer/kaggriculture-v39-ready-before-the-rush` |
| 取り出し方 | `%%writefile main.py` のセル本文。**`guruprasaathas111/kaggriculture-master-engine-v53e01d74d8f` と同一ファイル**（SHA-256 一致）なので master-v53 はこれで代用。**セルは実行していない** |
| SHA-256 | `52bec9e1038ef2b7f94d7f0f4009ac7d2c4cfc369ea83e31e88c72b2d04c1a8d` |
| サイズ | 311,247 bytes |
| 系統 | その他 |
| 安全確認 | 取り出したソースと、その中で `exec` される埋め込みソースを再帰的に ast でたどり、危ない import（subprocess / socket / urllib / shutil など）と呼び出し（system / popen / urlopen / rmtree など）が0件（EXP-20260919-13） |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\v39\main.py` を渡す（最後の callable が agent）。
