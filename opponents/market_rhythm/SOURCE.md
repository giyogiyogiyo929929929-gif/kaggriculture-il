# 出典：market_rhythm

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-19（UTC、夜）
関連: doc 07 §5, EXP-20260919-17

| 項目 | 内容 |
|---|---|
| ノートブック | `alperen5252525/kaggriculture-market-rhythm-sale-policy` |
| 取り出し方 | セル1の base64 リテラルを ast で読み、展開。**セルは実行していない**（スクラッチパッド `extract_batch3.py`） |
| SHA-256 | `f3be6392671608e9a575145c6caba4ab2f76d44b7ed64cdc086c8bcf845b541a` |
| サイズ | 361,915 bytes |
| 系統 | First in Line の作者の新作 |
| 安全確認 | 取り出したソースと、その中で `exec` される埋め込みソースを再帰的に ast でたどり、危ない import・呼び出しを探した。0件 |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\market_rhythm\main.py` を渡す（最後の callable が agent）。
