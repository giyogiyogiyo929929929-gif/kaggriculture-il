# 02 データ取得パイプライン

状態: Implemented
最終更新: 2026-09-18
関連: 03_replay_schema.md, 01_requirements.md (FR-1, FR-2, NFR-4)

## 1. 方針

スクレイピングや非公式 API は使わず、**公式 Kaggle CLI を `subprocess` から呼ぶ**。

### 確認済み（2026-09-18、タスク 0-1・0-2）

- `Kaggle CLI 2.2.4`。`competitions` に `leaderboard / team-submissions / episodes / replay` がすべて存在する。
- 認証は `%USERPROFILE%\.kaggle\access_token`（OAuth）で通っている。**`kaggle.json` は存在しない**
  （CLAUDE.md の記述と実態が違う。どちらもコミット禁止であることに変わりはない）。
- 上の4コマンドすべてで実データの取得に成功（リーダーボード → 提出 → エピソード → リプレイ1本）。

## 2. 手順（列名まで実測済み）

| # | 目的 | コマンド | 出力先 |
|---|---|---|---|
| 1 | 上位50チーム | `kaggle competitions leaderboard kaggriculture -s --format csv --page-size 200` | **標準出力** |
| 2 | 各チームの提出 | `kaggle competitions team-submissions <teamId> --format csv` | **標準出力** |
| 3 | 提出ごとのエピソード | `kaggle competitions episodes <submissionId> --format csv` | **標準出力** |
| 4 | リプレイ | `kaggle competitions replay <episodeId> -p data\raw` | `data\raw\episode-<id>-replay.json` |

出力の実例（列名は実測）：

| # | 列 | 例 |
|---|---|---|
| 1 | `teamId, teamName, submissionDate, score` | `16730612, Unknown Mother-Goose, 2026-09-16 02:07:02.966000, 3180.4` |
| 2 | `id, dateSubmitted, publicScore` | `56266758, 2026-09-16 01:59:10.273000, 3180.4` |
| 3 | `id, createTime, endTime, state, type` | `110451333, ..., EpisodeState.COMPLETED, EpisodeType.EPISODE_TYPE_PUBLIC` |

パースの注意（実測でハマった点）：

- `leaderboard` は **`-s` か `-d` のどちらかが必須**。`--format csv` だけでは
  `Either --show or --download must be specified` で失敗する。
- **`PYTHONIOENCODING=utf-8` を付けて呼ぶこと。** チーム名に絵文字（🤗 など）が含まれており、
  Windows の既定 cp932 のままだと CLI 側が
  `'cp932' codec can't encode character '\U0001f917'` で **exit 1** になる。
  上位50件のうち少なくとも1チームが該当した（`--page-size 200` で28件目で停止）。
- `leaderboard -s` は CSV の**前に** `Next Page Token = ...` という行を出す。**1行目を読み飛ばすのではなく、
  `teamId,` で始まるヘッダ行を探してそこから読む**。続きは `--page-token <token>` で取る。
- `team-submissions` / `episodes` に `-p` は無い。`subprocess` で stdout を受け取り `data\meta\*.csv` に保存する。
- 手順2の `id` が submissionId、手順3の `id` が episodeId。どちらも `publicScore` / 順位は付いてこない。
- 手順2は**そのチームのアクティブな提出が複数返る**（実測2本）。`publicScore` 最大の1本を選ぶ（設定 `submissions_per_team`）。
- 1提出あたりのエピソード数は多い（実測 345 本）。`episodes_per_team` で必ず絞る。

- **上位50件は1リクエストで取れる**（`--page-size 200` で200件返る。実測。`Next Page Token` も付くので
  それ以上必要ならページングできる）。

TODO(要確認)：

- 同名チームが複数ある場合の順位突き合わせ（03 §5.1：リプレイにはチーム名しか入っていない）

## 3. 取得ルール

- **生リプレイは1本 33MB**（実測、720ステップ。03 §4）。**取得したら即ダイジェスト化して生データを削除**。
- **Validation Episode は手順3の `type` 列で除外する**（`EpisodeType.EPISODE_TYPE_VALIDATION`）。
  リプレイを落とす前に弾けるので 33MB の無駄打ちが無い（03 §5.2）。
- `state` が `EpisodeState.COMPLETED` のものだけ取る。
- 既定上限：1チームあたり20エピソード（設定値）。**この上限は「累積」で数える。**
  コンペ開催中はエピソードが増え続けるため、毎回「直近N本」を取ると再実行のたびに増える。
  manifest の取得済み件数を引いた残りだけ取る（実測：修正前は再実行で新規2本を取ってしまった）。
- episodeId で重複排除。上位50チーム同士の対戦を優先（同じ試合が両チーム側から出てくるため重複が多い）。
- 各リクエスト間に sleep（初期値1.5秒）、エラー時は指数バックオフ。
- `data\meta\manifest.json` に処理済み episodeId を記録し、再実行で続きから再開。

## 4. ダイジェスト形式（タスク 0-4・確定版）

実データ（`episode-110451333`）で試作して測った結果：

| 形式 | サイズ |
|---|---|
| 生リプレイ | 33,135,787 bytes |
| ダイジェスト（JSON） | **329,275 bytes**（1/101） |
| ダイジェスト（JSON gzip） | **28,894 bytes**（1/1147） |

保存は `data\digest\<episode_id>.json.gz`（gzip）。

### 4.1 スキーマ

```jsonc
{
  "episode_id": 110451333,          // info.EpisodeId
  "module_version": "1.32.7",
  "seed": 1170568551,               // info.seed
  "configuration": { ... },         // そのまま（specification は捨てる）
  "seats": [                        // 席順（info.TeamNames の順）
    {"team_name": "DSM", "final_money": 113565.0, "won": false,
     "team_id": "16732748", "rank": 4, "public_score": 3087.5}   // 順位・スコアは meta から結合
  ],
  "turns": [                        // 719件（t=1..719）
    {"t": 1, "day": 0, "hour": 0,   // day/hour は「この行動を決めた観測」= steps[t-1] のもの
     "a": [ {"f": ["PASS"], "h": [], "m": [["BUY_ANIMAL","COW",1], ...]},   // 席0
            {"f": [...],    "h": [...], "m": [...]} ]}                      // 席1
  ],
  "days": [                         // 30件（hour == 0 のステップ）
    {"day": 0, "t": 0,
     "prices":    {"WHEAT": 25, ...},          // market.prices
     "inventory": {"WHEAT": 10000, ...},       // market.inventory
     "shops": ["BAKERY", ...],                 // town.unlocked_shops
     "seats": [
       {"money": 3000.0, "quadrants": ["NW"], "hires_today": 0,
        "tiles": {"crops": {"WHEAT": 25, "STRAWBERRY": 34}, "animals": {"COW": 9, "SHEEP": 3, "GOOSE": 2},
                  "structures": {"PASTURE": 12, "COOP": 2},
                  "weeds": 0, "empty": 2, "locked": 25, "yield_units": 55},
        "shed":  {"WHEAT": 12},                // 値が0の品目は落とす
        "seeds": {"MELON": 2}}
     ]}
  ]
}
```

### 4.2 決めたこと・理由

- **`turns` は全720ターン・両席の行動をそのまま残す**（297KB）。マクロ行動（`m`）の教師データであり、
  `f` / `h` は 0-5 のパターン分析と実行層の設計に要る。キー名は短縮（`a/f/h/m`）。
- **`t` に付ける `day` / `hour` は `steps[t-1]` の観測のもの**（03 §3.1：行動は t-1 の観測に対する応答）。
  これで `turns[i]` がそのまま (状態時刻, 行動) のペアになる。
- **`days` は `hour == 0` のステップだけ**（30件、32KB）。`tiles` は 10×10 の生データを捨てて集計値にする。
  これで容量の99%を占めていた `farms.tiles` が消える。
- `watered_today` / `fed_today` は**日次リフレッシュ直後なので hour 0 では必ず false**。集計しても無意味なので入れない。
- `shed` / `seeds` は席ごとに自席の観測（`steps[t][i].observation.private`）から取る（相手の分は見えない）。
- 席と順位の結合は `data\meta\leaderboard.csv` の `teamName` で行う（03 §5.1：リプレイ側にはチーム名しかない）。
  **リーダーボードに載っていないチーム（取得時の `top_n` より下位）には `rank` が付かない。**
  実測：`--top-n 2` で取ったときは対戦相手の `SpaTaro` / `DSM` が `rank: null` になった。
- ~~全量取得時は解消する。~~ → **解消しなかった（2026-09-19 に判明）。**
  **ダイジェストの `rank` / `team_id` は、ダイジェストを作った時点のリーダーボードのスナップショットで固定される。**
  全量取得ではダイジェスト済みのエピソードが飛ばされるため、付け直されない。
  実測：`--top-n 2` の試し取得（2026-09-18 22:56、`leaderboard.csv` 作り直しの 23:08 より前）で作った
  6エピソードに、当時2位で今は圏外の `Unknown Mother-Goose` が `rank: 2` のまま残り、
  現2位の `SpaTaro`・現3位の `DSM` が `rank: null` のままだった（460席中8席）。
  → **ダイジェストの `rank` は参考値として扱い、使う側で `leaderboard.csv` から引き直す**
  （学習データは doc 04 §3.3）。ダイジェストは作り直さない（生リプレイは削除済みのため）。

### 4.3 受け入れ条件（0-4）

- [x] ダイジェストが 1MB 以下（実測：6本すべて gzip 27.9〜29.4KB）
- [x] `turns` が 719 件、`days` が 30 件（6本すべて）
- [x] `turns[0]` の `m` が生リプレイの `steps[1]` の market 注文と一致する（テストで検証）
- [x] `tiles` のタイル数合計が `boardSize^2` = 100 になる（6本×30日×2席すべて 100）
- [x] ダイジェスト化に成功したら生リプレイを削除し、manifest に `digested` として記録する
- [x] `fetch_replays.py` から呼ばれ、取得 → ダイジェスト → 生データ削除が1コマンドで通る

## 5. 設定値

| キー | 既定値 |
|---|---|
| top_n | 50 |
| submissions_per_team | 1 |
| episodes_per_team | 20 |
| request_interval_sec | 1.5 |

## 6. 受け入れ条件

取得部分（タスク 0-3）：

- [x] 2チーム×2エピソードで手順1〜4が通る（実測：4本取得、1本33MB前後）
- [x] 途中で強制終了 → 再実行で重複取得せず再開できる（manifest 判定。再実行で `planned=0`）
- [x] Validation Episode が除外されている（手順3の `type` 列で判定）
- [x] 上限が累積で効く（再実行で新規取得が増えない）

ダイジェスト部分（タスク 0-4）：

- [x] 取得したリプレイがダイジェスト化される
- [x] `data\raw` に処理済みファイルが残らない
- [x] ダイジェスト1本が1MB以下（実測 約28KB）

## 7. 実装

- `scripts\fetch_replays.py`（手順1〜4 + ダイジェスト呼び出し）
  - `FetchConfig`（§5 の設定値）/ `FetchPipeline`（手順1〜4）/ `Manifest`（再開・累積上限）
  - `parse_csv_stdout`（`Next Page Token` 行のスキップ）/ `select_episodes`（Validation・未完了の除外）
  - `pick_submissions`（publicScore 最大）/ `call_with_retry`（指数バックオフ）/ `_team_lookup`（順位結合）
- `scripts\digest_replay.py`（§4 のダイジェスト化）
  - `digest_replay`（変換）/ `tile_summary`（tiles の集計）/ `write_digest`・`load_digest`（gzip）
  - `load_teams`（leaderboard.csv から順位）/ `digest_file`（1本処理＋生データ削除）/ `update_manifest`
- テスト：`tests\test_fetch_replays.py`（15件）、`tests\test_digest_replay.py`（12件）。
  どちらも kaggle CLI をフェイクに差し替え、ネットワークを使わない。

```cmd
.venv\Scripts\python.exe -m pytest tests -q
.venv\Scripts\python.exe scripts\fetch_replays.py --top-n 2 --episodes-per-team 2 --dry-run
.venv\Scripts\python.exe scripts\fetch_replays.py --top-n 2 --episodes-per-team 2
.venv\Scripts\python.exe scripts\digest_replay.py data\raw --delete-raw
```

実行結果（2026-09-18）：上位2チーム × 2エピソード = 6本を取得しダイジェスト化。
**198,000,000 bytes → 171,792 bytes（1/1150）**、`data\raw` は空。
`data\meta\` に `leaderboard.csv` / `submissions.csv` / `episodes.csv` / `manifest.json`、
`data\digest\` に `<episode_id>.json.gz` を出力。

全量（上位50チーム×20本＝最大1000本）の見積り：
生リプレイは都度削除されるのでディスクは**ダイジェスト約28MB**で済む。
所要時間は1本あたりダウンロード＋変換で数秒＋リクエスト間隔1.5秒。
