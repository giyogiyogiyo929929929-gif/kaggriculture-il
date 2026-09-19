# 出典：farming_v2

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-19
関連: doc 07 §5, EXP-20260919-13

| 項目 | 内容 |
|---|---|
| ノートブック | `lynnsakurai/farming-score-v2-a-better-approach` |
| 取り出し方 | `SOURCE_BYTES = b''.join(...)` を ast で読んで連結（最後の関数 `_e336_agent`）。**セルは実行していない** |
| SHA-256 | `99604be9332db3e6cc2167e7425587c2a77a69825ca5ca116de9a48f37f08364` |
| サイズ | 362,237 bytes |
| 系統 | V47 / V48 系 |
| 安全確認 | 取り出したソースと、その中で `exec` される埋め込みソースを再帰的に ast でたどり、危ない import（subprocess / socket / urllib / shutil など）と呼び出し（system / popen / urlopen / rmtree など）が0件（EXP-20260919-13） |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\farming_v2\main.py` を渡す（最後の callable が agent）。
