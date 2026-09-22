# 出典：story_of_seasons

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-21
関連: doc 07 §5, EXP-20260921-32（7回目の取り込み）

| 項目 | 内容 |
|---|---|
| ノートブック | `hanifnoerrofiq/story-of-seasons`（story-of-seasons） |
| 作者 | Hanif Noer Rofiq |
| 票数（取得時） | 0 |
| 最終実行（取得時） | 2026-09-20 13:45:47 UTC |
| 取得コマンド | `.venv\\Scripts\\kaggle.exe kernels pull hanifnoerrofiq/story-of-seasons -p <スクラッチ>` |
| 取り出し方 | `scripts\\analysis\\extract_notebook_agents.py`（ast でリテラルのみ）。**セルは実行していない** |
| SHA-256 | `16c7f6b8ed8b5ee152165008352df789db64f8b82c2e072a02a8091cd949e166` |
| サイズ | 1,008,669 bytes |
| ライセンス | Apache License 2.0 の本文・帰属表記をソース内で確認 |
| 系統 | v9/4 系の複数層を統合した別系統。v51/v52/v53とは先頭から異なる |
| 安全確認 | `scripts\\analysis\\audit_agent.py` で注意1件。`V92_SELL_LIB` が設定されたときだけ `open(path)` で開発用データを読む。環境変数未設定なら読まない |
| 実行確認 | 未実行。公開コードをimportする preflight は自動承認レビューで拒否されたため、評価は保留 |

**このファイルは改変しない。** Kaggle が選ぶ最後の callable は `agent`。
