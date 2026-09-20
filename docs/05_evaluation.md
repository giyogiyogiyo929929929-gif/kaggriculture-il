# 05 評価

状態: Implemented
最終更新: 2026-09-20
関連: 04_model_design.md §5, 06_submission.md, EXP-20260919-01, EXP-20260919-06

## 1. 方法

```cmd
.venv\Scripts\python.exe scripts\eval.py <agentA> <agentB> -n 20
```

- **同じシードで両席を入れ替えたペア比較**。1ペア = 同じ seed で席0/席1を入れ替えた2試合。
- 1試合の結果はランダム要素（解放される店・weed の発生）で大きくぶれるので、**単発の結果で判断しない**。
- 差はペア単位で取る：`pair_diff = (A席0のとき A−B) + (A席1のとき A−B)) / 2`。
  席の有利不利が相殺されるので、単純な勝率より分散が小さい。

### 1.1 エージェントの指定方法

| 指定 | 意味 |
|---|---|
| `starter` / `random` / `pass` | `kaggle_environments` の組み込み（`kaggriculture.py` の `agents`） |
| `main.py` などのパス | そのファイルを読み込み、**名前空間の中で最後に現れた callable な値**を使う（提出時と同じ規則。06） |

- ★**呼び出すときの引数も Kaggle 本体と同じにする**（2026-09-19 修正）。Kaggle は
  `args = [observation, configuration][: agent.__code__.co_argcount]` で、関数の引数の数に合わせて切り詰める
  （`kaggle_environments/agent.py` 151〜153行・171〜172行で確認）。以前の `eval.py` は常に2つ渡していたため、
  `agent(obs)` と定義された公開エージェント2本が毎ターン `TypeError` になり、「一度も行動しない」と誤評価していた
  （EXP-20260919-10）。`_TimedAgent` で同じ切り詰めをする。回帰テスト `test_single_argument_agent_is_called_like_kaggle`。
- ★**エントリは「最後に def された関数」ではなく「最後の callable な値」**（2026-09-20 修正）。
  Kaggle の `get_last_callable` は名前空間の値を見る（doc 06「仕様」）。以前の `eval.py` は ast で最後の `def` を選んでいたため、
  agent を末尾の代入（`agent = _entry`）で作る公開エージェント（`opponents\v38`・`v43`）で補助関数を呼んでしまい、
  **相手が何もしないまま試合が終わっていた**（EXP-20260920-20）。手元58本のうち食い違うのはこの2本だけで、他の結果に影響は無い。
  回帰テスト `test_entry_is_last_callable_value_not_last_def`。
- ★**読み込むときは、そのファイルのあるフォルダを `sys.path` に入れる**（2026-09-20 修正）。Kaggle は `main.py` の
  ディレクトリを `sys.path` に追加する（doc 06「仕様」）ので、**複数ファイルのエージェント**は `from base_agent import ...`
  のように隣のファイルを import できる。以前の `resolve_agent` はこれをしておらず、`opponents\gods_mode`（4ファイル）が
  `ModuleNotFoundError` で評価できなかった（EXP-20260920-18）。`scripts\preflight.py` の `load_like_kaggle` は元から入れていた。
  回帰テスト `test_multi_file_agent_can_import_sibling`。

### 1.2 実行時間と並列実行

1試合あたり約2.5秒（720ターン、CPU）。`-n 20`（40試合）で直列なら約100秒。

**試合はそれぞれ独立なので並列に回す**（`-j / --jobs`）。

- 既定は `min(4, CPU数 - 1)`（この PC は16コア）。`-j 1` で直列（デバッグ用）。
- `concurrent.futures.ProcessPoolExecutor` を使う。Windows は spawn なので、
  **ワーカー側でエージェントを読み込む**（関数やモジュールを親から渡さない）。
  ワーカーに渡すのは「エージェントの指定文字列・seed・席の入れ替え有無」だけ。
- seed は試合ごとに固定なので、**決定的なエージェント同士なら並列でも直列と結果が一致する**
  （受け入れ条件で確認する）。
- **注意：組み込みの `random` は再現しない。** `random_agent` は毎ターン `random.Random()` を
  シード無しで作るため（`kaggriculture.py` 実装で確認）、同じ seed でも毎回違う手を打つ。
  再現性が要る比較には使わず、勝率の目安としてだけ使う。
- 1ターンの推論時間はワーカー内で測る。並列実行は他プロセスの影響で時間が伸びるため、
  **合格基準（最悪 < 200ms・99%点 < 50ms。§4）の判定に使う計測は `-j 1` か preflight で行う**。

## 2. 出力

標準出力に人が読める表、`--json <path>` で機械可読な結果も出す。

```
対戦: main.py vs baselines/v1_agent.py   ペア数 20（40試合、-j 4）
勝敗          : 20勝 0敗 0分（ペア単位）
ペア差        : +14,029 ± 1,402（平均 ± 標準誤差）
最終所持金    : A 中央値 61,464 / B 中央値 44,943
1ターン推論   : A 中央値 1.9ms 最悪 8.5ms / B 中央値 1.6ms 最悪 11.0ms
例外          : A 0件 / B 0件
健全性(A)     : 植え付け 68 → 収穫 46 / 損失 0（水切れ 0 + 未収穫 0／寿命終了 17 は正常）/ 家畜逃走 0 / 最終shed 28
健全性(B)     : 植え付け 52 → 収穫 32 / 損失 0（水切れ 0 + 未収穫 0／寿命終了 7 は正常）/ 家畜逃走 4 / 最終shed 30
```

### 2.1 健全性の指標（04 §5.5 の weed 指標を置き換える）

weed は自然発生（100タイル×30日×0.5% ≒ 15枚）と枯死が混ざって区別できないため、
**タイルの遷移を数える**。行動ログを数えるより正確で、成功した行動だけが数えられる。

| 指標 | 数え方（連続する2ステップのタイル比較） |
|---|---|
| 植え付け数 | `None` → 作物 |
| 収穫数（一度きりの作物） | 作物 → `None` |
| **水切れ枯死** | 作物 → `WEED` のうち、遷移直前が `watered_today` False かつ `consecutive_unwatered >= 1` |
| **未収穫損失** | 作物 → `WEED` のうち、寿命切れ（`max_lifespan_step` 到達）かつ `yield_units > 0` |
| 寿命終了 | 作物 → `WEED` のうち、寿命切れかつ `yield_units <= 0`。**正常なので損失に数えない** |
| weed の自然発生 | `None` → `WEED` |
| **家畜の逃走数** | 家畜あり構造物 → 家畜なし構造物 |
| 最終 shed | 最終ステップの shed 合計（100 に張り付いていたら溢れている） |

**作物 → `WEED` を一括で「枯死」と数えてはいけない**（EXP-20260919-06）。
`ongoing` 作物（STRAWBERRY など）は最終収穫の翌日に必ず `WEED` になる仕様で、
これは失敗ではない。実測では `PLANT→WEED` 697 件のうち 693 件（99.4%）がこれだった。
観測には `watered_today` / `consecutive_unwatered` / `max_lifespan_step` / `yield_units` が
そのまま入っているので、遷移直前のタイルを見れば3つを機械的に区別できる。

なお**新しく植えた作物は `consecutive_unwatered = 1` から始まる**ため、
**植えた当日に水をやらないとその日の境界で必ず枯れる**（定着後は1日なら抜いても死なない）。
作付けを増やす変更をするときに壊れやすい箇所。

## 3. 比較対象

`starter`（組み込み）、`random`、フェーズ0のルールベース版（`main.py`）、直前の提出版。

`pass`（何もしない）は所持金が `startingMoney` から動かないので、**席の対応や集計の検算に使える**。

### 3.1 直前の提出版との比較（凍結）

```cmd
.venv\Scripts\python.exe scripts\freeze_agent.py v2 --note "submission xxxx"
.venv\Scripts\python.exe scripts\eval.py main.py baselines\v2_agent.py -n 20 -j 4
```

`scripts\freeze_agent.py` は `agent\` を **パッケージ名を変えて丸ごと写す**
（`baselines\v2_pkg\` と入口の `baselines\v2_agent.py`）。

**パラメータだけを固定した凍結版では比較にならない。** 両方が同じ `agent\` を import するため、
`macro.py` / `execute.py` の**コード変更が両者に同時に効いて差が出ない**
（実際に EXP-20260919-05 の試行7・8 で誤った「差0」を出した）。

## 4. 合格基準（提出してよい条件）

- [ ] 直前の提出版に対してペア差の平均がプラス（**標準誤差の2倍以上**）
- [ ] `starter` に全勝に近い（20ペア中19ペア以上）
- [ ] 1ターン推論の**最悪値 < 200ms かつ 99%点 < 50ms**（NFR-1）
      ★2026-09-19 改訂（ユーザー承認）。以前は「最悪 < 50ms」。これは自前エージェント用に大きな余裕を取った基準で、
      Kaggle の実際の制限は1ターン1秒。公開エージェント v9/4 は中央値 0.56ms・99%点 5.7ms・最悪 54.9ms
      （3,595ターン中 50ms 超えは1回。EXP-20260919-11）。新しい基準でも実際の制限に対して5倍の余裕がある。
      （**GC のポーズを含めて測る**。実測で GC 有効時は最悪65msまで伸びた。04 §5.4 参照）
- [ ] 例外ゼロ
- [ ] 家畜の逃走ゼロ、最終 shed < 100
- [ ] **水切れ枯死 ＋ 未収穫損失 が植え付けの5%以下**（寿命終了は除外して数える。§2.1）

## 5. 受け入れ条件（タスク 0-7）

- [x] `eval.py starter random -n 2` が表を出して終了コード0
- [x] ペア比較で各 seed について席を入れ替えた2試合が走る
- [x] ファイルパス指定で `main.py` を読み込み、最後の callable を agent として使える
- [x] エージェントが例外を投げても評価が止まらず、例外件数として集計される
- [x] 1ターン推論時間（中央値・最悪）が両者について出る
- [x] `--json` で結果を書き出せる
- [x] `-j 4` と `-j 1` で同じ結果（勝敗・所持金）になる（決定的なエージェント同士）
- [x] `eval.py main.py starter -n 5` が EXP-20260919-01 の数字を再現する
      （5勝0敗、ペア差 +58,913、最終所持金 中央値 63,793。§2 の出力例は現行の v2 対 v1）
- [x] `-j 4` が `-j 1` より速い（47.8秒 → **20.9秒**、2.3倍。-n 5）

## 6. 記録

評価結果は `docs/experiments/` に残す。`--json` の出力を添えること。

## 7. 実装

- `scripts\eval.py`
  - `resolve_agent`（組み込み名／ファイルの最後の callable）/ `_TimedAgent`（時間と例外）
  - `play_match`（1試合）/ `build_matches`（席入れ替え）/ `evaluate`（ペア集計）/ `format_summary`
  - `health_metrics`（§2.1 のタイル遷移カウント）／
    `classify_weed`（`PLANT→WEED` を 水切れ枯死／未収穫損失／寿命終了 に分ける）
- テスト：`tests\test_eval.py`（15件。うち2件は `-m slow`）
  - `test_classify_weed_separates_lifespan_from_loss` が3分類の回帰テスト
  - `test_baseline_loses_no_animals`（`-m slow`）が §4 の「逃走ゼロ・損失5%以下」を見る

```cmd
.venv\Scripts\python.exe scripts\eval.py main.py starter -n 20 -j 4 --json data\eval\latest.json
.venv\Scripts\python.exe scripts\eval.py main.py starter -n 5 -j 1   :: 推論時間の判定はこちら
```

`--episode-steps` で試合を短くできる（テストの動作確認用。既定は720）。

### 7.1 このツールで分かったこと（重要）

0-6 の「受け入れ条件を満たした」という判定のうち**2件が誤りだった**ことが、
タイル遷移を数えて初めて分かった（EXP-20260919-02）。

- **家畜の逃走は1試合あたり平均4頭**。0-6 では「最終盤面の頭数が多い＝逃げていない」と
  判断していたが、逃げた分を買い直していたため頭数では見抜けなかった。
- ~~**枯死は植え付け54件中14件（26%）**~~ → **この判定自体が誤りだった（EXP-20260919-06）。**
  `PLANT→WEED` を一括で数えたため、STRAWBERRY の寿命終了を枯死に含めていた。
  20ペア40試合で数え直すと、植え付け 2,725 件に対し実損失は
  **水切れ枯死4件・未収穫損失0件＝0.15%** で、基準（5%以下）を満たしている。
  §2.1 の指標を3分割に改めた。

→ 04 §5.5 / §5.6 を修正済み。家畜の逃走は EXP-20260919-05（`cash_floor` 800）で解消。

## 8. 分析ツール（`scripts/analysis/`、2026-09-20 追加）

EXP-20260919-11〜17 でスクラッチパッドに作って繰り返し使った分析を、パスと版名を引数にしてリポジトリへ移した。
どれも**挙動を変えない観測だけ**のツール。コマンドはリポジトリ直下で実行する。共通部品は `_common.py`。

| スクリプト | 用途 | 例 |
|---|---|---|
| `fetch_own.py` | 自分の提出の公開対戦リプレイをまとめて取得（要ネットワーク） | `fetch_own.py 56357846 data\raw_own\v6` |
| `live_summary.py` | 本番リプレイを1試合ずつ要約（勝敗・コピー判定・食い違いステップ・日ごとの差）→ pkl | `live_summary.py data\raw_own\v6 <lb.csv> v6_live.pkl` |
| `fingerprint.py` | 本番の seed・席を手元で再現し、最終所持金が1ドルまで一致する相手を探す | `fingerprint.py submissions\v6_preempt\main.py v6_live.pkl --losses-only` |
| `replay_seed.py` | 本番の seed・席で自分の版と相手を対戦（別の版ならどうだったか） | `replay_seed.py submissions\v7_relax\main.py 1234 0 opponents\v50\main.py` |
| `ledger_match.py` | 手元の1試合を約定1個ずつの台帳つきで回す → pkl | `ledger_match.py <A> <B> 3 a.pkl` |
| `ledger_replay.py` | 本番リプレイの両者の行動を流し直して台帳を取る（相手のコード不要） | `ledger_replay.py <replay.json> r.pkl` |
| `ledger_report.py` | 台帳の比較（品目ごとの売上・支出・日ごとの所持金差、勝ち負け別の合計） | `ledger_report.py a.pkl r.pkl` |
| `layer_trace.py` | v9/4 系の層ごとの SELL（`sells`）と PREDICT 層の発火（`predict`） | `layer_trace.py predict <A> <B> 3 pf.pkl` |
| `copy_check.py` | コピー判定の確認（`window`：96〜167 の一致と所持金差、`diff`：食い違いの推移） | `copy_check.py window <自分> 5 <相手>` |
| `eval_compare.py` | `eval.py` の JSON を試合単位で集計・2つの版を比較（所持金の完全一致数） | `eval_compare.py data\eval\v7 data\eval\v6` |
| `timing.py` | 1プロセスで1ターンの推論時間（中央値・p99・最悪） | `timing.py <自分> <相手> 71 75` |
| `extract_notebook_agents.py` | 公開ノートブックから main.py を取り出す（**セルは実行しない**。ast でリテラルだけ読む） | `extract_notebook_agents.py <nb_dir> <out_dir>` |
| `money_trace.py` | 1試合の所持金差を日ごと・ステップごとに追う（差がどこで開くか） | `money_trace.py submissions\v10_de\main.py opponents\v51\main.py 242` |
| `audit_agent.py` | 埋め込みソースまで再帰的に、危ない import・呼び出しを探す（実行しない） | `audit_agent.py opponents\v50\main.py` |

- 実行は `.venv\Scripts\python.exe scripts\analysis\<名前>.py ...`。出力の文字化けは `set PYTHONIOENCODING=utf-8`。
- エージェント内部の表示は `sys.__stderr__` に出る（kaggle-environments が stdout を取り込むため）。
- 自分側の名前は `_common.ME_NAMES`（個人名とチーム名の両方。doc 06）。変わったら `--me` で指定する。
- 動作確認（2026-09-20）：`ledger_match` と `replay_seed` が v7 対 v50 の seed 3 で同じ最終所持金（75,175 対 73,330）、
  `eval_compare` で v7 と v6 が 420/420 一致、`copy_check window`・`layer_trace predict`・`timing`・`audit_agent` が動く。
  `fetch_own`・`live_summary`・`ledger_replay` は手元に生リプレイが無いため未確認（中身はスクラッチパッド版から名前の判定以外変えていない）。
