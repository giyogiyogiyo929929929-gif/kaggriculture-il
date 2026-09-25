# EXP-20260925-68: 公開分析Notebook・上位リプレイ資産の取得

状態: Implemented
日付: 2026-09-25
最終更新: 2026-09-25
関連: EXP-20260924-63, EXP-20260924-64, EXP-20260922-53
関連 doc: docs/02_data_pipeline.md, docs/05_evaluation.md §8, AGENTS.md §4
コミット: 未コミット
プロファイル: 評価型
Round: -
親候補: `submissions/v80_submitted/main.py`

## 仮説

公開された個別submission診断、日次Top-10リプレイアーカイブ、ラダー全体の軽量特徴量をローカルへ保存すれば、
v80の世界別・系統別診断と公開敗戦の回帰集合拡張を、巨大な全量リプレイを重複取得せずに進められる。

## 設定（相手・seed・席・ペア数・候補差分）

- 取得先はGit管理外の`data/imports/public_analysis_20260925/`。
- 公開Notebook 3本は公式Kaggle CLIでソースとmetadataを取得し、セルは実行しない。
- `ashok205/kaggriculture-top10-replay-archive`は全ファイルを取得する。
- `georgymamarin/kaggriculture-episodes`は分析に必要な軽量表・説明・特徴抽出コードだけ取得し、
  20GB超の`replays_*.parquet`と117MBのcrawler stateは重複取得しない。
- 取得後にファイル一覧・サイズ・SHA-256 manifestを保存する。対戦・提出・agent変更は行わない。

## スモークテスト

- Notebook 3本の最新ソース取得とJSON構文を確認する。
- Top-10 archiveは公開`archive_manifest.json`の自己ハッシュと各取得ファイルのSHA-256を確認する。
- 軽量表は最低限CSV/Markdown/Pythonとして読み取り可能であることを確認する。

## 結果（05_evaluation.md の形式で。Local指標と安全ゲート）

- 取得先: `data/imports/public_analysis_20260925/`（Git管理外）。
- 公開Notebook 3本をソース＋`kernel-metadata.json`として取得し、JSON構文を確認した。セルは実行していない。

| Notebook | cell数 | bytes | SHA-256 |
|---|---:|---:|---|
| `x-ray-your-agent.ipynb` | 41 | 98,686 | `3ca5da4f9d0b3be8f6e141e92be24f38a36a69e52067e9a850dc2e098b66f2df` |
| `top10-replay-dataset-archive.ipynb` | 11 | 35,945 | `dbe9746ec94116507a4ca25887c3dd72126afa923a82129bb4ca4f57fca3125a` |
| `kaggriculture-what-2600-farms-do-differently.ipynb` | 36 | 87,158 | `7f15418eeac390417219f9e061b1ad28acb5c54c53eecbfe551624724782991d` |

- Top-10 archive全体をZIPと展開済みファイルの両方で保存した。ZIPは3,745,061,808 bytes、
  SHA-256は`4608e1371e5dfc218168440f02783872304306d679e57f1f822c86d663ff5219`。
- archive schema 3、56日（2026-07-30〜2026-09-23）、25,377 unique episodes、日次順位560行。
- 公開manifest SHA-256 `e1c1b2ca5266b86e3884bd079f615e688afae4fca98c08e30653b836877e7253`は
  自己ハッシュ一致。manifest記載ファイルについて欠損0、サイズ不一致0、SHA不一致0。
- Kaggriculture Episodesから10個の軽量資産、合計175,169,740 bytesを取得した。

| ファイル | SHA-256 |
|---|---|
| `DESCRIPTION.md` | `0daf89bf721b9dd0c4ba5003587fe03e978df424100350ca054af3903c87e792` |
| `README.md` | `29a0ae122d34f5714d60fc35a06406ece8f4ddc653995743ce20682924567e6a` |
| `agents.csv` | `989e90d7ed56dd7c2135c3113fd22ab5478cdfc92db92266f525ad6facf93250` |
| `daily_stats.csv` | `74e409ca7013bcb4c2863ee4041b2735028df808269517bdcbf97f9332fe5ee9` |
| `episode_features.csv` | `e7b2101f88776e268b0b2fc115dbb9947519377e432f8345ddd2ea6f753a79a5` |
| `episodes.csv` | `ff2c4e0fd4ae5a4f15b6faa957f5ed3d28ed4097710cb34633a1dcf7d7af5634` |
| `features.py` | `3b70a7cdbfa85a551681461427a4871b736820d3996ce4025a34d7aff64a5e07` |
| `per_submission_coverage.csv` | `792f5519d254c7a387cb5a98a4ad7cd9d553412182c6ddf7c43c01c848293e66` |
| `stream_hashes.csv` | `991f396862339a23e43cd2c09eb007430500684873081bfd505df9047e4ebfd9` |
| `teams.csv` | `e901391a21ffcde789e1179910be2c2759899907623aad38cdad5cd9f2f67a47` |

- CSV 7本はヘッダを読み取り、想定列を確認した。対戦・提出・agent変更は行っていない。

## Public/LB（未提出・未確認は `-`）

-

## 考察

Top-10 archiveの日次順位は試合ペアの`avg_score`を使う代理順位で、真のleaderboard順位とは扱わない。
全体メタのfinal bank相関は仮説生成に限定し、採否は既存の同seed・席交換・相手別勝敗で判断する。

## 次のアクション

v80診断へ使う対象日・世界・相手系統を別EXPで定義する。まず`episodes.parquet`と
`top10_history.parquet`だけで対象を絞り、必要な日次replay shardだけを読む。

## 共有記録

- [x] 診断資産取得のため`docs/SCORES.md`へのスコア行は省略
- [x] 再利用知見を`docs/KNOWLEDGE.md`へ追記
