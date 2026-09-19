# 出典：v49

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-19（UTC、夜）
関連: doc 07 §5, EXP-20260919-17

| 項目 | 内容 |
|---|---|
| ノートブック | `ahmedberatozer/kaggriculture-v49-funded-sale-timing-and-worker` |
| 取り出し方 | `SOURCE_BYTES = b''.join(...)` を ast で読んで連結。**`guruprasaathas111/game-theoretic-master-discrete-optimization` と同一**（SHA-256 一致）。**セルは実行していない**（スクラッチパッド `extract_batch3.py`） |
| SHA-256 | `ed89be8cd96fe58ea5ca96c91bbeda28d928a5192ed926639fe6c43aea39b368` |
| サイズ | 437,804 bytes |
| 系統 | V47 系の後継 |
| 安全確認 | 取り出したソースと、その中で `exec` される埋め込みソースを再帰的に ast でたどり、危ない import・呼び出しを探した。0件 |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\v49\main.py` を渡す（最後の callable が agent）。
