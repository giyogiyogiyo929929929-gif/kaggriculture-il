# 出典：jaxa_2780

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20
関連: doc 07 §5, EXP-20260920-28（6回目の取り込み）

| 項目 | 内容 |
|---|---|
| ノートブック | `jaxa623/2780-beyond-48-0-128-128-worlds-with-95-cis`（[2780] Beyond 48-0: 128/128 Worlds with 95% CIs ） |
| 作者 | sdy623 |
| 票数（取得時） | 40 |
| 最終実行（取得時） | 2026-09-17 00:02:29 |
| 取得コマンド | `.venv\Scripts\kaggle.exe kernels pull jaxa623/2780-beyond-48-0-128-128-worlds-with-95-cis -p <スクラッチ>` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（ast でリテラルのみ）。**セルは実行していない**（AGENTS.md §5） |
| SHA-256 | `4757f3f5b28db8a2f4614bb08993a8a567a7d49bae1ac324fbcfbcc1af60e95e` |
| サイズ | 350,794 bytes |
| 系統 | jaxa623 の新版（既出の `jaxa_2802` と同じ作者） |
| 安全確認 | `scripts\analysis\audit_agent.py` で再帰的に検査 → **注意0件** |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\jaxa_2780\main.py` を渡す（最後の callable が agent）。
