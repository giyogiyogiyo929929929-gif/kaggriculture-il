# 出典：melon_squeeze

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-19（UTC、夜）
関連: doc 07 §5, EXP-20260919-17

| 項目 | 内容 |
|---|---|
| ノートブック | `goodpjw2008/kaggriculture-melon-threshold-squeeze-2749` |
| 取り出し方 | `%%writefile main.py` のセル本文。**セルは実行していない**（スクラッチパッド `extract_batch3.py`） |
| SHA-256 | `b81c6027d935a0581acae2f3a257c5c984bce621038f06e324ad8b5243bce432` |
| サイズ | 338,274 bytes |
| 系統 | V45 の改変 |
| 安全確認 | 取り出したソースと、その中で `exec` される埋め込みソースを再帰的に ast でたどり、危ない import・呼び出しを探した。0件 |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\melon_squeeze\main.py` を渡す（最後の callable が agent）。
