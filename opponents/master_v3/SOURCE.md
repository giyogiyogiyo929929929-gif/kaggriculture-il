# 出典：master_v3

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-19
関連: doc 07 §5, EXP-20260919-13

| 項目 | 内容 |
|---|---|
| ノートブック | `guruprasaathas111/kaggriculture-master-engine-v3` |
| 取り出し方 | `%%writefile main.py` のセル本文。**セルは実行していない** |
| SHA-256 | `dbc709febaef6b7b3f77ce8ee7dd2466548be0bd52763aa89905f61940f153b7` |
| サイズ | 841,471 bytes |
| 系統 | **v9/4 のコピー**（v4 と20試合すべて同額の引き分け。EXP-20260919-13）。コピー判定が正しく発動するかの確認にも使う |
| 安全確認 | 取り出したソースと、その中で `exec` される埋め込みソースを再帰的に ast でたどり、危ない import（subprocess / socket / urllib / shutil など）と呼び出し（system / popen / urlopen / rmtree など）が0件（EXP-20260919-13） |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\master_v3\main.py` を渡す（最後の callable が agent）。
