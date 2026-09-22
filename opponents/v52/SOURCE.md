# 出典：v52

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-21
関連: doc 07 §5, EXP-20260920-28（6回目の取り込み）, EXP-20260921-32（7回目の取り込み）

| 項目 | 内容 |
|---|---|
| ノートブック | `ahmedberatozer/kaggriculture-v52-lean-flock-yarn-route`（Kaggriculture V52 — Lean Flock, Yarn Route） |
| 作者 | Ahmed Berat Özer |
| 票数（取得時） | 2 |
| 最終実行（取得時） | 2026-09-20 10:38:58 UTC |
| 取得コマンド | `.venv\\Scripts\\kaggle.exe kernels pull ahmedberatozer/kaggriculture-v52-lean-flock-yarn-route -p <スクラッチ>` |
| 取り出し方 | `scripts\\analysis\\extract_notebook_agents.py`（ast でリテラルのみ）。**セルは実行していない** |
| SHA-256 | `8c0f7d90db965a676bd0e211e0250aa9b9235d64d43ff0b4e3852a71d1ef7c24` |
| サイズ | 1,007,349 bytes |
| ライセンス | Apache License 2.0 の本文・帰属表記をソース内で確認 |
| 系統 | `v51` の先頭461,510 bytesを共有し、その後に Yarn Route の層を追加 |
| 安全確認 | `scripts\\analysis\\audit_agent.py` で再帰的に検査 → **注意0件** |
| 実行確認 | 未実行。公開コードをimportする preflight は自動承認レビューで拒否されたため、評価は保留 |

**このファイルは改変しない。** Kaggle が選ぶ最後の callable は `_e350_agent`。
