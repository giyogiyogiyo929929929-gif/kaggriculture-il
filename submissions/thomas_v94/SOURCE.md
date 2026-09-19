# 出典：thomas_v94（The 2945 Farm, v9/4）

状態: 取り込み済み（改変なし）
取得日: 2026-09-19
関連: ADR-0003, EXP-20260919-11

| 項目 | 内容 |
|---|---|
| ノートブック | `thomastschinkel/the-2945-farm-96-vs-the-top-10-public-bots`（The 2945 Farm） |
| 作者 | thomastschinkel（Thomas Tschinkel） |
| 参照のきっかけ | ユーザーの指定（2026-09-19） |
| 取得コマンド | `.venv\Scripts\kaggle.exe kernels pull thomastschinkel/the-2945-farm-96-vs-the-top-10-public-bots -p <スクラッチ>` |
| 取り出し方 | セル5（`%%writefile main.py`）の本文＋末尾の改行1つ（`%%writefile` の挙動と同じ）。**セルは実行していない** |
| SHA-256 | `bfee70e9daaebeae0737a880f1df8f1c60d0783c59af620136cc0d28ef482bc7`（セル6の `EXPECTED_SHA256` と一致。作者の submission 56269928 の提出ファイル） |
| サイズ | 856,428 bytes / 5,760行 |
| エントリ | `agent(observation, configuration)`（最後の callable） |
| import | 標準ライブラリのみ（`base64 / copy / itertools / json / math / os / zlib`） |
| ライセンス | **Apache-2.0**（ノートブックに明記。上流の告知はファイル先頭にそのまま残されている） |

安全確認（EXP-20260919-11）：
- `exec` 2か所は埋め込み文字列（`kaggle-environments` から抜き出したコードと改変）。中身は `copy / time` のみで危ない呼び出し無し。
- `open(path)` は環境変数 `V92_SELL_LIB` があるときだけ読む開発用の処理で、通常は実行されない。

作者の記載：本番ラダー 2944.7（2026-09-16）。**このファイルは改変しない。** 手を入れるときは別名で置く。
