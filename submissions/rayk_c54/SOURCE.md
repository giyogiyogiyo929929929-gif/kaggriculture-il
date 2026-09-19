# 出典：rayk_c54

状態: 取り込み済み（改変なし）
取得日: 2026-09-19
関連: ADR-0003, EXP-20260919-10

| 項目 | 内容 |
|---|---|
| ノートブック | `raykkretzschmar/kaggriculture-findings-from-zero-to-top-meta`（Kaggriculture: Findings from Zero to Top Meta） |
| 作者 | Rayk Kretzschmar |
| 票数（取得時） | 192 |
| 最終実行（取得時） | 2026-08-11 14:13 |
| 取得コマンド | `.venv\Scripts\kaggle.exe kernels pull raykkretzschmar/kaggriculture-findings-from-zero-to-top-meta -p <スクラッチ>` |
| 取り出し方 | セル54 の `_C95_AGENT_B64_PARTS` を ast で読み、b64 デコード → zlib 展開。**セルは実行していない** |
| SHA-256 | `489f5d197527f107027626cce79d850fd2ca90edd43d94384b849b6511e27bdb`（ノートブックのセル54に書かれた値と一致） |
| サイズ | 75,098 bytes |
| エントリ | `c94_submission_agent(obs, config=None)`（最後の callable。`--entry c94_submission_agent`） |
| import | `base64 / copy / json / math / zlib` のみ。内部で別の埋め込みソース（`_SBT_SOURCE`）を `exec` するが、それも取り出して確認済み（同じく標準ライブラリのみ、危ない呼び出し無し） |

**このファイルは改変しない。** 手を入れるときは別名で置く。
ライセンス・コンペのルール上の扱いはユーザーが確認（ADR-0003）。
