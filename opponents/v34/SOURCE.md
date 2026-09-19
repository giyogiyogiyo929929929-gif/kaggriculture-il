# 出典：v34

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-19
関連: doc 07 §5, EXP-20260919-13

| 項目 | 内容 |
|---|---|
| ノートブック | `ahmedberatozer/kaggriculture-v34-observed-market-timing` |
| 取り出し方 | `%%writefile main.py` のセル本文。**セルは実行していない** |
| SHA-256 | `7664283797f48f0d15ff0d45ea4cea5a559d2c26fe0d75cdc86456eef775ef74` |
| サイズ | 254,082 bytes |
| 系統 | その他 |
| 安全確認 | 取り出したソースと、その中で `exec` される埋め込みソースを再帰的に ast でたどり、危ない import（subprocess / socket / urllib / shutil など）と呼び出し（system / popen / urlopen / rmtree など）が0件（EXP-20260919-13） |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\v34\main.py` を渡す（最後の callable が agent）。
