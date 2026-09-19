# 出典：v31

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-19
関連: doc 07 §5, EXP-20260919-13

| 項目 | 内容 |
|---|---|
| ノートブック | `ahmedberatozer/kaggriculture-v31-production-and-sale-priority` |
| 取り出し方 | `%%writefile main.py` のセル本文。**セルは実行していない** |
| SHA-256 | `1a66c7902b4d7ff8d1c7a51d1a3f927e177d578218effd6c5e9e800f998e7d9d` |
| サイズ | 235,112 bytes |
| 系統 | その他 |
| 安全確認 | 取り出したソースと、その中で `exec` される埋め込みソースを再帰的に ast でたどり、危ない import（subprocess / socket / urllib / shutil など）と呼び出し（system / popen / urlopen / rmtree など）が0件（EXP-20260919-13） |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\v31\main.py` を渡す（最後の callable が agent）。
