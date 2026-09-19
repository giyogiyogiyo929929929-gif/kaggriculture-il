# 出典：v41

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-19
関連: doc 07 §5, EXP-20260919-13

| 項目 | 内容 |
|---|---|
| ノートブック | `ahmedberatozer/kaggriculture-v41-review-candidate` |
| 取り出し方 | `%%writefile main.py` のセル本文。**セルは実行していない** |
| SHA-256 | `4a66dc7611e19d7d4df4ce386d509768023f09ec384bd24e8765b4cbc59e08d3` |
| サイズ | 331,609 bytes |
| 系統 | その他 |
| 安全確認 | 取り出したソースと、その中で `exec` される埋め込みソースを再帰的に ast でたどり、危ない import（subprocess / socket / urllib / shutil など）と呼び出し（system / popen / urlopen / rmtree など）が0件（EXP-20260919-13） |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\v41\main.py` を渡す（最後の callable が agent）。
