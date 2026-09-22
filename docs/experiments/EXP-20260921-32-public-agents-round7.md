# EXP-20260921-32: 公開ノートブックの7回目の収集

日付: 2026-09-21
関連: EXP-20260920-28, docs/05_evaluation.md §8

公開ノートブックは565本から577本へ増えた。新規・更新候補をリポジトリ外へ取得し、セルを実行せずにAST抽出、SHA-256比較、静的監査をした。

| 結果 | 内容 |
|---|---|
| 収集 | `opponents\\v52`、`opponents\\v53`、`opponents\\story_of_seasons` の3本 |
| V52 | Apache-2.0、監査注意0件。v51と先頭461,510 bytesを共有 |
| V53 | Apache-2.0、監査注意0件。v52と先頭1,007,349 bytesが完全一致 |
| Story of Seasons | Apache-2.0。`V92_SELL_LIB` が設定された時だけの開発用 `open(path)` を1件検出 |
| God’s Mode | 更新版の埋め込み期待SHAは既存4ファイルと一致し、再取り込み不要 |
| Visible-Price Switch Lab | 提出エージェント候補を抽出できず |
| KoshinM Local Best | 3公開版は同一SHA。圧縮ペイロードを含めライセンス表記が無く、取り込まない |

公開コードのimportを伴うpreflight・対戦評価は自動承認レビューにより拒否され、今回の3本は未実行の評価用相手として記録した。
