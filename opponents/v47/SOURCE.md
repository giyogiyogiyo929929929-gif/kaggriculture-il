# 出典：v47

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-19
関連: doc 07 §5, EXP-20260919-13

| 項目 | 内容 |
|---|---|
| ノートブック | `ahmedberatozer/kaggriculture-v47-reactive-market-coordination` |
| 取り出し方 | `SOURCE_BYTES = b''.join(...)` を ast で読んで連結。**セルは実行していない** |
| SHA-256 | `f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842` |
| サイズ | 354,288 bytes |
| 系統 | V47 / V48 系 |
| 安全確認 | 取り出したソースと、その中で `exec` される埋め込みソースを再帰的に ast でたどり、危ない import（subprocess / socket / urllib / shutil など）と呼び出し（system / popen / urlopen / rmtree など）が0件（EXP-20260919-13） |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\v47\main.py` を渡す（最後の callable が agent）。
