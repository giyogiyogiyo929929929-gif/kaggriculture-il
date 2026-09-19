# 出典：smaller_market_shock

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-19（UTC、夜）
関連: doc 07 §5, EXP-20260919-17

| 項目 | 内容 |
|---|---|
| ノートブック | `dmitriigluzdov/kaggriculture-a-smaller-market-shock` |
| 取り出し方 | セル4の base64 の tar から main.py を取り出す。**セルは実行していない**（スクラッチパッド `extract_batch3.py`） |
| SHA-256 | `d5460fc2e5488e0a340f0e4e795f2709c48b58cff7c204ced3821a4c7dae4555` |
| サイズ | 862,940 bytes |
| 系統 | **v9/4 系のコードを含む** |
| 安全確認 | 取り出したソースと、その中で `exec` される埋め込みソースを再帰的に ast でたどり、危ない import・呼び出しを探した。注意は開発用の `open(path)`（環境変数 `V92_SELL_LIB` があるときだけ読む v9/4 由来の処理）の1件のみ |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\smaller_market_shock\main.py` を渡す（最後の callable が agent）。
