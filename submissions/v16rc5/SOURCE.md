# 出典：v16rc5

状態: 取り込み済み（改変なし）
取得日: 2026-09-19
関連: ADR-0003, EXP-20260919-10

| 項目 | 内容 |
|---|---|
| ノートブック | `boatlee/v16-rc5-high-score-8c-4s-premium-market-lead`（V16-RC5 \| High-Score 8C/4S Premium Market Lead） |
| 作者 | boatlee |
| 票数（取得時） | 314 |
| 最終実行（取得時） | 2026-08-12 10:25 |
| 取得コマンド | `.venv\Scripts\kaggle.exe kernels pull boatlee/v16-rc5-high-score-8c-4s-premium-market-lead -p <スクラッチ>` |
| 取り出し方 | セル11（`%%writefile main.py`）から、マジック行を除いた本文をそのまま。**セルは実行していない** |
| SHA-256 | `f029fa0cb66a9eb509afbe44e3f59b800332d0419db91607183410e4089c4d19`（ノートブックのセル12の `expected_sha256` と一致） |
| サイズ | 18,946 bytes |
| エントリ | `agent(obs)`（引数1つ。最後の callable） |
| import | `base64 / copy / json / zlib` のみ。通信・ファイル操作・外部コマンド無し（確認済み） |

ノートブックの説明：上位提出（Nikita Lugovoy）のリプレイに基づく行動列（`_ACTIONS`）を再生し、
市場の先回り（`_front_run`）などを加えたもの。

**このファイルは改変しない。** 手を入れるときは別名（例 `submissions\v16rc5_mod\main.py`）で置く。
ライセンス・コンペのルール上の扱いはユーザーが確認（ADR-0003）。
