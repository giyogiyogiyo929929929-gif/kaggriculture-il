# 出典：v53

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-21
関連: doc 07 §5, EXP-20260921-32（7回目の取り込み）

| 項目 | 内容 |
|---|---|
| ノートブック | `ahmedberatozer/kaggriculture-v53-opening-signature`（Kaggriculture V53 — Opening Signature） |
| 作者 | Ahmed Berat Özer |
| 票数（取得時） | 2 |
| 最終実行（取得時） | 2026-09-20 14:00:38 UTC |
| 取得コマンド | `.venv\\Scripts\\kaggle.exe kernels pull ahmedberatozer/kaggriculture-v53-opening-signature -p <スクラッチ>` |
| 取り出し方 | `scripts\\analysis\\extract_notebook_agents.py`（ast でリテラルのみ）。**セルは実行していない** |
| SHA-256 | `20fe549dd4573b9fd1dfb32a1782c205fa74f0edfdfd6cbe935079533e0a9d0e` |
| サイズ | 1,036,778 bytes |
| ライセンス | Apache License 2.0 の本文・帰属表記をソース内で確認 |
| 系統 | `v52` と先頭1,007,349 bytesが完全一致し、その後に Opening Signature の層を追加 |
| 安全確認 | `scripts\\analysis\\audit_agent.py` で再帰的に検査 → **注意0件** |
| 実行確認 | 未実行。公開コードをimportする preflight は自動承認レビューで拒否されたため、評価は保留 |

**このファイルは改変しない。** Kaggle が選ぶ最後の callable は `_e363_agent`。
