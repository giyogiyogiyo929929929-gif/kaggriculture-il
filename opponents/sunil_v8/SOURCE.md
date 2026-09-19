# 出典：sunil_v8

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-19
関連: doc 07 §5, EXP-20260919-13

| 項目 | 内容 |
|---|---|
| ノートブック | `sunil123kumar/kaggriculture-v8` |
| 取り出し方 | `SOURCE_BYTES = b''.join(...)` を ast で読んで連結（最後の関数 `_e335_agent` ＝ V48 のコピー）。**セルは実行していない** |
| SHA-256 | `4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96` |
| サイズ | 357,742 bytes |
| 系統 | V47 / V48 系 |
| 安全確認 | 取り出したソースと、その中で `exec` される埋め込みソースを再帰的に ast でたどり、危ない import（subprocess / socket / urllib / shutil など）と呼び出し（system / popen / urlopen / rmtree など）が0件（EXP-20260919-13） |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\sunil_v8\main.py` を渡す（最後の callable が agent）。
