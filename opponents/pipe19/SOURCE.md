# 出典：Kaggriculture Pipe19 Sale Advance Overflow

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-22
関連: EXP-20260922-50

| 項目 | 内容 |
|---|---|
| ノートブック | `nathanjacob/kaggriculture-pipe19-sale-advance-overflow` |
| 作者 | Nathan Jacob |
| 取り出し方 | Kaggle公式CLIで取得後、`extract_notebook_agents.py`でASTリテラル抽出。**セルは実行していない** |
| SHA-256 | `111863bd708cc8134d0a7cc26ae9ac8b7cb5266e061cd71d8429caefb48b1c51` |
| サイズ | 1,035,995 bytes |
| ライセンス | Apache License 2.0の本文・帰属表記を確認 |
| 系統 | Pipe18にADV（3ターン売却前倒し）とR148（夜明け前overflow回収）を追加 |
| 静的監査 | 環境変数 `V92_SELL_LIB` 指定時だけ外部ファイルを読む任意経路1件。通常経路にネットワーク・subprocessなし |
| preflight | 正常720 step完走、中央値0.89ms・p99 6.47ms・最悪111.97ms。壊れた観測で `KeyError('step')` のため3項目不合格 |

notebookの `EXPECTED_SHA256` と実ファイルのSHA-256は一致した。Kaggleが選ぶ最後のcallableは
`agent`。`kaggle_submission_agent` は既存キーへの再代入なので辞書順の最後にはならない。

**このファイルは改変しない。** 現状は比較相手専用。
