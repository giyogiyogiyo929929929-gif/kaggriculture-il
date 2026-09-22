# 出典: dz_one_more_wheat

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-21

| 項目 | 内容 |
|---|---|
| ノートブック | `dmitriigluzdov/kaggriculture-one-more-wheat`（Kaggriculture: One More Wheat） |
| URL | https://www.kaggle.com/code/dmitriigluzdov/kaggriculture-one-more-wheat |
| 作者 | Dmitrii Gluzdov |
| 取得方法 | `.venv\Scripts\python.exe -m kaggle kernels pull dmitriigluzdov/kaggriculture-one-more-wheat -m` |
| 抽出方法 | `scripts/analysis/extract_notebook_agents.py`（セルは実行せず AST とリテラルだけを読む） |
| SHA-256 | `10f58185b916392ca39697c83f67f455df81a74dfb6eb1aacd60fd81d50c9970` |
| サイズ | 1,020,006 bytes |
| ライセンス | Apache-2.0（ソース内の原文と帰属を保持） |
| 系統 | Pipe16 HybridOpening 系。仮設小麦を1日長く成熟させ、day 3に収穫・牧草地復元・搬入する層を追加 |
| 静的監査 | `audit_agent.py` で注意1件。`open(path)` は `path = None` に固定された到達不能な外部ライブラリ読込部 |

ノートに埋め込まれた期待 SHA と抽出ファイルの SHA が一致した。取得内容を改変せず保存する。
