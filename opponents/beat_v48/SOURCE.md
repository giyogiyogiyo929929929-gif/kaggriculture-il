# 出典：beat_v48

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20
関連: doc 07 §5, EXP-20260920-28（6回目の取り込み）

| 項目 | 内容 |
|---|---|
| ノートブック | `shiiin9/beat-v48-100-0-your-herd-is-decided-on-day-6`（Beat V48 100-0: Your Herd Is Decided on Day 6） |
| 作者 | shiiin9 |
| 票数（取得時） | 0 |
| 最終実行（取得時） | 2026-09-19 07:50:14 |
| 取得コマンド | `.venv\Scripts\kaggle.exe kernels pull shiiin9/beat-v48-100-0-your-herd-is-decided-on-day-6 -p <スクラッチ>` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（ast でリテラルのみ）。**セルは実行していない**（AGENTS.md §5） |
| SHA-256 | `ba612b6f7af67aac1889f65a8a5e052e72fe9d9ca6c7928478dd95158e668329` |
| サイズ | 374,095 bytes |
| 系統 | shiiin9。「V48 に 100-0」を掲げる家畜重視の版 |
| 安全確認 | `scripts\analysis\audit_agent.py` で再帰的に検査 → **注意0件** |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\beat_v48\main.py` を渡す（最後の callable が agent）。
