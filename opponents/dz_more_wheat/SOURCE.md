# 出典：dz_more_wheat

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20
関連: doc 07 §5, EXP-20260920-28（6回目の取り込み）

| 項目 | 内容 |
|---|---|
| ノートブック | `dmitriigluzdov/kaggriculture-more-wheat-smarter-sales`（Kaggriculture: More Wheat, Smarter Sales） |
| 作者 | Dmitrii Gluzdov |
| 票数（取得時） | 11 |
| 最終実行（取得時） | 2026-09-20 09:04:21 |
| 取得コマンド | `.venv\Scripts\kaggle.exe kernels pull dmitriigluzdov/kaggriculture-more-wheat-smarter-sales -p <スクラッチ>` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py`（ast でリテラルのみ）。**セルは実行していない**（AGENTS.md §5） |
| SHA-256 | `218d72b0a5ce40d23657b9bd6a1385f106948a9dd76d49f786d9cf04eba34b7d` |
| サイズ | 870,455 bytes |
| 系統 | Dmitrii Gluzdov の新版（既出の `dz_v111` と同じ作者） |
| 安全確認 | `scripts\analysis\audit_agent.py` で再帰的に検査 → 注意1件：`open(path)`（環境変数 `V92_SELL_LIB` があるときだけ読む v9/4 系共通の開発用処理）。危ない import・呼び出しは無し |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\dz_more_wheat\main.py` を渡す（最後の callable が agent）。
