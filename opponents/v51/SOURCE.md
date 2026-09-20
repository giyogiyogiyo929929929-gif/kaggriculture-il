# 出典：v51

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20
関連: doc 07 §5, EXP-20260920-28（6回目の取り込み）

| 項目 | 内容 |
|---|---|
| ノートブック | `ahmedberatozer/kaggriculture-v51-lean-flock`（Kaggriculture V51 — Lean Flock） |
| 作者 | Ahmed Berat Özer |
| 票数（取得時） | 2 |
| 最終実行（取得時） | 2026-09-20 09:21:02 |
| 取得コマンド | `.venv\Scripts\kaggle.exe kernels pull ahmedberatozer/kaggriculture-v51-lean-flock -p <スクラッチ>` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（ast でリテラルのみ）。**セルは実行していない**（AGENTS.md §5） |
| SHA-256 | `c1e3590d02e42d16091c5377e87a3db16496e5a462d558dc2925887f835f9891` |
| サイズ | 461,739 bytes |
| 系統 | Ahmed Berat Özer の V51（既出の `v49`・`v50` の後継） |
| 安全確認 | `scripts\analysis\audit_agent.py` で再帰的に検査 → **注意0件** |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\v51\main.py` を渡す（最後の callable が agent）。
