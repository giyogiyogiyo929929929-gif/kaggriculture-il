# 03 リプレイスキーマ

状態: Implemented
最終更新: 2026-09-18
関連: 02_data_pipeline.md, 04_model_design.md

> 推測で書かない。**本 doc の内容はすべて実データで確認済み**。
> 根拠：ローカル実行（kaggle-environments 1.32.7）と、実リプレイ `episode-110451333`（2026-09-18 取得）。

## 0. 確認方法（根拠）

- 環境：`kaggle-environments==1.32.7` の `envs/kaggriculture`（README.md と実行結果）
- ローカル確認：`episodeSteps=30, seed=42` で対戦を1本走らせ、`env.toJSON()` の構造を調べた
- 実リプレイ：`episode-110451333`（submissionId 56266758 / teamId 16730612 `Unknown Mother-Goose` vs `DSM`、720ステップ、33MB）
- 再確認コマンド：

```cmd
.venv\Scripts\python.exe scripts\inspect_replay.py data\raw\episode-110451333-replay.json
```

- **ローカルと実リプレイでトップレベル・ステップ構造は同じ**。違いは実リプレイに `schema_version: 1` が付くことと `info` の中身だけ。

## 1. リプレイ JSON のトップレベル

| キー | 内容 |
|---|---|
| `id` | 実行時の UUID。**Kaggle の episodeId ではない**（episodeId は `info.EpisodeId`） |
| `name` / `title` / `description` / `version` | 環境の識別情報（`name` は `"kaggriculture"`） |
| `module_version` | kaggle-environments のバージョン（実リプレイも `"1.32.7"`） |
| `schema_version` | 実リプレイでは `1`（ローカル生成には無い） |
| `configuration` | §2 |
| `specification` | 環境仕様の丸ごとコピー（5,749 bytes、ダイジェストでは捨てる） |
| `steps` | `steps[t][i]`：ターン t・プレイヤー i の記録（§3） |
| `rewards` | 最終報酬 `[p0, p1]`。**最終所持金と同じ値**（実測 `[113565.0, 117589.0]`） |
| `statuses` | `["DONE", "DONE"]` |
| `info` | チーム名・episodeId・seed（§5.1） |

## 2. `configuration`

`episodeSteps, actTimeout, runTimeout, boardSize, startingMoney, maxMarketOrdersPerTurn, turnsPerDay, shedCapacity, weedSpawnChance, townShopUnlockInterval, townShopSellInterval, townCenterSellInterval, farmHandCostMult, marketParams, seed`

- `seed` は読み取り後にクリアされるため JSON 上は `null`。実際の値は `info.seed`。
- 実リプレイの値は既定どおり：`episodeSteps=720, turnsPerDay=24, boardSize=10, startingMoney=3000, actTimeout=1, maxMarketOrdersPerTurn=10, marketParams={}`

## 3. `steps[t][i]`

キーは `observation` / `action` / `reward` / `status` / `info` の5つ（ローカル・実リプレイとも）。

### 3.1 行動と観測の対応（最重要・確認済み）

**`steps[t][i].action` は `steps[t-1][i].observation` を見て返された行動であり、その実行結果は `steps[t][i].observation` に反映されている。**

ローカル検証（`seed=42`、step 0 の観測で `BUY_SEED WHEAT 2` を返すエージェント）：

| t | `steps[t][0].action` | `steps[t][0].observation` の所持金 / 種 |
|---|---|---|
| 0 | `{"farmer":["PASS"],"hands":[],"market":[]}`（ダミー） | 3000.0 / 0 |
| 1 | `BUY_SEED WHEAT 2` | 2980.0 / 2 |
| 2 | `PLANT WHEAT` + `HIRE` | 2979.0 / 1 |

実リプレイでも同じ（`inspect_replay.py` の対応チェック）：
t=1 の `action` に `BUY_ANIMAL COW 1` ほか → 所持金は 3000.0（t=0 の観測）から 2454.0（t=1 の観測）へ。

→ **学習ペアは `X = steps[t].observation`, `y = steps[t+1].action`**。`steps[0].action` はダミーなので捨てる。

### 3.2 `observation`

README の「Observation Format」どおり。実キー：

`player, day, hour, farms, market, town, private, remainingOverageTime`（+ **プレイヤー0のみ** `step`）

- **`step` はプレイヤー1の観測には入らない**（ローカル・実リプレイとも）。ターン番号は `day * turnsPerDay + hour` で作る（agent 実装でも同様）。
- `farms[i]`：`money, tiles, farmer, hands, unlocked_quadrants, hires_today`（両者分が見える＝公開情報）
- `private`：`shed, seeds, inventories`（自席の分のみ。`inventories[0]` が本人、以降がその日のファームハンド。実測で最大7要素）
- `market`：`inventory`, `prices`。キーは `WHEAT, CARROT, TOMATO, STRAWBERRY, MELON, EGG, MILK, WOOL, FERTILIZER`
- `private.shed` のキーは上記9種＋`GOOSE, COW, SHEEP`
- `town`：`unlocked_shops`（重複あり）
- タイルの中身（`None` / `"LOCKED"` / PLANT / WEED / COOP・PASTURE の各 dict）は README の Observation Format 節を正とする。

### 3.3 `action`

```py
{"farmer": [<コマンド>, <引数>...], "hands": [[...], ...], "market": [[<注文>, <品目>, <数量>], ...]}
```

- README には `farmer` と `market` しか書かれていないが、**実際の記録には `hands` が入る**（その日雇ったファームハンドの行動リスト。上位チームは初日から4〜5人雇っていた）。
- `farmer` / `hands` の各コマンド：`NORTH/SOUTH/EAST/WEST, PLANT, WATER, HARVEST, FERTILIZE, FEED, CARE, COLLECT_FERTILIZER, PICKUP, DROP, PLACE, BUILD_COOP, BUILD_PASTURE, DIG, PASS`
- `market` の注文：`BUY_SEED, BUY_ANIMAL, BUY_PRODUCT, SELL, HIRE, BUY_LAND`（1ターン最大 `maxMarketOrdersPerTurn=10`）
  - `HIRE` と `BUY_LAND` は引数なしの1要素リスト（`["HIRE"]` / `["BUY_LAND"]`。実測）
  - **`["INVALID"]` と `["PASS"]` も `market` リストに現れる**（207エピソードで INVALID 229件 / PASS 13件。
    例：`episode-110434882` の t=342 席1 が `[["INVALID"]]`）。エージェントの不正・無意味な注文が
    そのまま記録されている。集計や学習データ作成では弾くこと（EXP-20260918-01）。
- **マクロ行動（04）の抽出元は `market` リスト**。`farmer` / `hands` は実行層（ルール）の担当。

### 3.4 `reward` / `status`

- 全ステップ `status="ACTIVE"` / `reward=0`（int）。最終ステップのみ `"DONE"` と最終所持金（float）。
- `rewards == [最終 observation の farms[i].money]`（実測で一致）。勝敗は大小で判定し、同値なら引き分け。

## 4. サイズ（実測）

| 対象 | サイズ |
|---|---|
| ローカル30ステップ | 約 190KB |
| **実リプレイ720ステップ** | **33.1MB**（1ステップあたり約 46KB） |
| うち `action` だけ抜き出したもの | 327KB |
| 日次（`hour == 0`）の観測30本 | 678KB |
| 1観測の内訳 | `farms` 10.9KB / `market` 0.3KB / `private` 0.34KB / `town` 0.04KB |

→ **容量のほぼ全部が `farms.tiles`**。ダイジェストでは tiles を集計値（作物別タイル数など）に潰せば、1エピソードあたり1MB以下にできる見込み。

## 5. 実リプレイで確認した項目

根拠：`episode-110451333`（2026-09-18 取得）と `kaggle competitions episodes 56266758`。

### 5.1 チーム名・episodeId（`info`）

```json
{"Agents": [{"Name": "DSM", "ThumbnailUrl": null},
            {"Name": "Unknown Mother-Goose", "ThumbnailUrl": null}],
 "EpisodeId": 110451333, "LiveVideoPath": null,
 "TeamNames": ["DSM", "Unknown Mother-Goose"], "seed": 1170568551}
```

- **席 i のチーム名 = `info.TeamNames[i]`**（`info.Agents[i].Name` も同じ並び）。
- `info.EpisodeId` が Kaggle の episodeId。トップレベルの `id`（UUID）とは別物。
- **順位・スコア・submissionId はリプレイに入っていない。** 順位はリーダーボード CSV の `teamName` と突き合わせる（同名チームがあると曖昧 → 02 で注意）。

### 5.2 Validation Episode の見分け方

リプレイの中身ではなく **`kaggle competitions episodes <submissionId>` の `type` 列**で判別する。

- 実測：submission 56266758 の 345 本のうち `EpisodeType.EPISODE_TYPE_VALIDATION` が1本、残りは `EpisodeType.EPISODE_TYPE_PUBLIC`。
- → **ダウンロード前に除外できる**（33MB の無駄打ちを避けられる）。02 §3 に反映する。

### 5.3 その他

- `configuration.marketParams` は `{}`。本番でも上書きされていない。
- リーダーボードの `score`（例 3180.4）は**最終所持金ではなくレーティング**。実際の最終所持金は10万台（`rewards`）。サンプル重み付け（04 §3）ではどちらを使うか区別する。

### 5.4 残った未確認

- [ ] エラー・タイムアウト時の `status` の値 `TODO(要確認)`（このエピソードは全て ACTIVE / DONE。落ちたエピソードを見つけたら追記する）

## 6. `scripts\inspect_replay.py` の仕様

```cmd
.venv\Scripts\python.exe scripts\inspect_replay.py data\raw\<file>.json
```

出力（標準出力に人間が読める形で）：

1. トップレベルのキーと型・サイズ
2. `configuration` 全体
3. `info` 全体（チーム名・順位を探すため）
4. `steps` の長さ、`steps[t][i]` のキー
5. `observation` のキー（席ごと）と、`step` キーの有無
6. `action` の例（最初の5ターンと、`market` が空でない最初の10ターン）＋行動と観測の対応チェック
7. 最終 `rewards` / `statuses` / 勝者
8. ファイルサイズと、`specification` を除いたサイズ

## 7. 受け入れ条件

- [x] ローカル生成リプレイに対して `inspect_replay.py` が落ちずに1〜8を出力する
- [x] 実リプレイ1本に対しても同様に出力できる
- [x] §5 の各項目が「確認済み」か「実リプレイにも無い」のどちらかに決着し、本 doc に追記されている（残りは §5.4 の1件）
- [x] §3.1 の対応関係が実リプレイでも成り立つことを確認した（`market` 注文の直後に所持金が動く：3000.0 → 2454.0）

## 8. 実装

- `scripts\inspect_replay.py`（`load_replay` / `describe` / `observation_keys` / `check_action_alignment` / `final_outcome`）
- テスト：`tests\test_inspect_replay.py`（ローカル対戦を1本生成して検証。6件）

```cmd
.venv\Scripts\python.exe -m pytest tests -q
.venv\Scripts\python.exe scripts\inspect_replay.py data\raw\episode-110451333-replay.json
```

- 調査用に `data\raw\episode-110451333-replay.json`（33MB）をローカルに残している。0-4（ダイジェスト形式）の検証が済んだら削除する。**コミット禁止。**
