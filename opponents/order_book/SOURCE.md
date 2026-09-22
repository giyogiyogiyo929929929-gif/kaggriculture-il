# 出典：Your Market List Is an Order Book

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-22
関連: EXP-20260922-50

| 項目 | 内容 |
|---|---|
| ノートブック | `shiiin9/your-market-list-is-an-order-book` |
| 作者 | shiiin9 |
| 取り出し方 | Kaggle公式CLIで取得後、`extract_notebook_agents.py`でASTリテラル抽出。**セルは実行していない** |
| SHA-256 | `a16e0e9b40c489972630a0b9d04f30e9c1cab03159fa78676db74277d84d82ab` |
| サイズ | 1,026,965 bytes |
| ライセンス | Apache License 2.0の本文・帰属表記を確認 |
| 系統 | Ahmed Berat Özer V55土台。Order Book並べ替え、トマト収益ゲート、4定数再調整を追加 |
| 静的監査 | `open(path)` 1件を検出したが、実コードで `path=None` に固定され通常・任意経路とも無効。ネットワーク・subprocessなし |
| preflight | 正常720 step完走、中央値0.89ms・p99 6.12ms・最悪62.13ms。壊れた観測で `KeyError('step')` のため3項目不合格 |

notebookの変数名が `EXPECTED_SHA256` のため抽出器表示は「期待値なし」だが、記載値と実ファイルの
SHA-256は一致した。Kaggleが選ぶ最後のcallableは `_cxd_agent`。

**このファイルは改変しない。** 現状は比較相手専用。
