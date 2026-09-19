# 06 提出

状態: Implemented
最終更新: 2026-09-19
関連: 01_requirements.md, 05_evaluation.md

## 仕様

- Kaggle は提出ファイルを **`exec(compile(raw), {})` で実行**し、
  **名前空間の中で最後に現れた callable な値**を agent として使う
  （`kaggle_environments/agent.py` の `get_last_callable`。実装で確認）。
  - **`__file__` も `__name__` も存在しない。** `__file__` を使うと `NameError` で
    提出が ERROR になる（実測：submission 56333731）。
  - 「最後に定義された関数」ではなく「最後の callable な値」なので、
    agent の後ろでクラスを import すると誤認される。
  - `main.py` のあるディレクトリは **Kaggle 側が `sys.path` に追加する**ので、自分で追加しなくてよい。
- 1ターンの制限時間は1秒。
- 重みを含める場合は、ルートに `main.py` を置いた `submission.tar.gz`。
- 提出直後に Validation Episode（自分のコピーとの対戦）が走る。

## 提出前チェックリスト

`scripts\preflight.py` が下の3〜5と時間・完走を自動で見る。1と6は人が確認する。

1. [ ] `05_evaluation.md` の合格基準を満たした
2. [ ] `.venv\Scripts\python.exe scripts\preflight.py` が通る
3. [ ] `main.py` の最後の関数がエントリ関数（既定 `agent`、`--entry` で指定。preflight が確認）
4. [ ] 壊れた観測5パターンで例外を出さず、形の正しい行動を返す（NFR-2。preflight が確認）
       ★2026-09-19 改訂（ADR-0003）：以前は「PASS と空の market を返すこと」まで求めていたが、
       それは v2 の作りに合わせた判定で、NFR-2（落ちない・フォールバック行動を返す）より厳しかった。
       v16rc5 は壊れた観測でも自分の行動列から行動を返す（例外なし・形は正しい）。
       rayk_c54 は観測 `None` で `AttributeError` になり、改訂後も通らない。
5. [ ] 提出環境にないライブラリを import していない（preflight が ast で確認）
6. [ ] `docs/experiments/` に今回の評価結果を記録した
7. [ ] **`main.py` が模倣モデルを使う場合**：`models\macro.json` が Kaggle と同じ読み込み方で読め、
       ルール表に落ちていない（preflight が確認。★フェーズ1で追加）。
       使わない場合（ADR-0002 以降の既定）は、preflight が「ルール表で提出」と表示する。

**7 が一番危ない。** モデルが読めないと `agent\plan.py` は黙ってルール表（v2）に落ちる設計なので
（doc 04 §3.5、試合中に落ちないための安全装置）、**エラーにならずに v2 と同じ中身を提出してしまう。**
アーカイブにモデルが入っていない・パスがずれている、を提出前に必ず止める。

## コマンド

```cmd
.venv\Scripts\python.exe scripts\preflight.py --build
.venv\Scripts\kaggle.exe competitions submit kaggriculture -f submission.tar.gz -m "説明"
.venv\Scripts\kaggle.exe competitions submissions kaggriculture --format csv
.venv\Scripts\kaggle.exe competitions submission-limits kaggriculture
```

- `preflight.py --build` が `submission.tar.gz` を作る（`main.py` をルート、`agent/` をそのまま）。
  **`models\macro.json` は `main.py` が `plan_for_turn` を使うときだけ自動で同梱する**
  （`preflight.uses_model` が ast で判定。ADR-0002 で既定は「使わない」）。
  - ★**アーカイブ内のパスはリポジトリからの相対パスを保つ**（`models/macro.json`）。
    当初の `build_archive` はファイルを `arcname=path.name` で入れていたため、
    `models\macro.json` がアーカイブ直下の `macro.json` になり、本番でモデルが見つからなくなるところだった。
  - 本番では tar が `/kaggle_simulations/agent/` に展開される。`agent\plan.py` は**自分の `__file__`**
    （import されたモジュールには存在する。無いのは `exec` される `main.py` だけ）から
    `../models/macro.json` を探す。
- **提出は1日5回まで**（`submission-limits` で確認。2026-09-19 時点）。

### 公開エージェントの提出（ADR-0003）

```cmd
.venv\Scripts\python.exe scripts\preflight.py --main submissions\v16rc5\main.py --build --output submissions\v16rc5\submission.tar.gz
.venv\Scripts\kaggle.exe competitions submit kaggriculture -f submissions\v16rc5\submission.tar.gz -m "説明"
```

- 置き場所は `submissions\<名前>\main.py`（ノートブックから取り出したものを**そのまま**）と
  `submissions\<名前>\SOURCE.md`（出典：ノートブック・作者・取得日・取り出し方・SHA-256）。改変は別名で置く。
- `--main` で指定したファイルのディレクトリを提出物のルートにする。`agent\` が無ければ `main.py` だけの tar になる。
- `--entry` で最後の callable の名前を指定する（既定 `agent`。例：rayk_c54 は `c94_submission_agent`）。
- ★**preflight もエージェントを Kaggle と同じ呼び方で呼ぶ**：`[obs, config][: co_argcount]`（doc 05 §1.1 と同じ）。
  v16rc5 は `agent(obs)` の1引数なので、以前の preflight（常に2引数）では落ちていた。
- **`-m "説明"` は cmd か PowerShell から直接実行すること。**
  bash 経由で cmd を呼ぶと引用符が失われて引数が分割される（実測で失敗した）。

## 実装

- `scripts\preflight.py`（`run_checks` / `build_archive` / `check_model_in_archive`）
  - `check_model_in_archive` は一時アーカイブを展開し、**別プロセスで** `main.py` を Kaggle と同じく `exec` してから
    `agent.plan` がモデルを読めるか・プランを出すかを見る。同じプロセスだと、既に import 済みの
    リポジトリの `agent` を読んでしまい、アーカイブの中身を確かめたことにならないため。
- テスト：`tests\test_preflight.py`（14件）

**実行結果（2026-09-19、フェーズ1のモデル入り、720ターン）**：全項目 OK。
提出物 3項目・合計 226,689 bytes、1ターン 中央値 0.93ms / 最悪 3.90ms。

## 提出履歴

| 日時(UTC) | submissionId | 内容 | publicScore |
|---|---|---|---|
| 2026-09-18 15:26 | 56333731 | フェーズ0 ベースライン | **ERROR**（`__file__` NameError） |
| 2026-09-18 15:32 | 56333848 | 同上（`__file__` 依存を修正）＝ v1 | 600.0（初期値）→ 509.1 → 519.3 → **522.0**（09-19 07:26 以降） |
| 2026-09-19 02:49 | 56346388 | v2：`cash_floor` 200 → 800（対 v1 +14,029 ± 1,402、20/20ペア） | 600.0（初期値）→ 526.5（04:31）→ **513.3**（07:26 以降） |
| 2026-09-19 07:26 | **56352206** | v3：公開エージェント v16rc5（改変なし、SHA `f029fa0c`。対 v2 40-0 +80,372、総当たり 146-14。EXP-20260919-10）。**ユーザーが提出**（Claude の提出コマンドは自動許可で止められたため） | 600.0（初期値）→ **1012.0**（08:23、提出から約1時間。3,947位 / 9,507） |

- v3 の説明文はユーザー入力の `v3 : vs v2 40-0`。一覧のファイル名は `submission.tar.gz` だけで
  どのファイルかは区別できないが、**ユーザーに確認し `submissions\v16rc5\submission.tar.gz` だった**（2026-09-19）。
| 2026-09-19 08:53 | **56354076** | v4：公開エージェント v9/4（thomastschinkel「The 2945 Farm」、Apache-2.0）＋例外時フォールバックの包み。`submissions\thomas_v94_safe\`（SHA-256 `a955ecec…`）。対 v3（v16rc5）40-0 +30,637、starter 20/20。EXP-20260919-11。**ユーザーが提出** | 600.0（初期値）→ 2452.0（11:48）→ **2544.0**（13:36） |
| 2026-09-19 11:47 | **56357846** | v6：v9/4 ＋ 候補A（コピー相手のときだけ売りの先読み 52）＋ 候補A2（コピーの PREDICT を1ターン先回り）＋ 包み。`submissions\v6_preempt\`（SHA-256 `3cdfe0ee…`、tar `bfa042bc…`）。対 v4 35-5-0（seed 71〜90）、対 master_v3 20-0-0、別系統11本は v4 と所持金まで完全一致。doc 07 §3・EXP-20260919-14。**ユーザーが提出** | 600.0（初期値）→ 2550.6（13:36）→ 2636.2（14:11）→ **2809.7**（15:52、約125位 / 9,554、銀の範囲） |

- 2026-09-19 13:36 UTC のリーダーボード：参加 9,540 チーム。**銅（上位10%）は 954位・2419.1**、銀（上位5%）は 477位・2648.2。
  チームの成績は良いほうの v6（2550.6）で **約 682位（上位 7.1%）**。1位は 3278.4。

- v4 の説明文は Claude が用意したものと同一なので、`submissions\thomas_v94_safe\submission.tar.gz` を送ったと判断した。
- v3 は 08:23 に 1012.0、09:00 に 941.3。1つの提出のレーティングは ±100 ほどぶれる（EXP-20260919-11 の教訓3）。

- 注意：リポジトリ直下の `submission.tar.gz` は v2 のまま。取り違えを防ぐため、提出するアーカイブは
  必ず `--output submissions\<名前>\submission.tar.gz` で作り、`-f` にもそのパスを書く。

### 最終順位の決まり方と、有効な提出（2026-09-19 にディスカッションで確認）

出典：`kaggle competitions topics show <id>`（CLI でディスカッションが読める）。

| 事実 | 出典 |
|---|---|
| **公開されているものは何でも使ってよい**（"Anything freely and publicly available is fair use."） | #737788、主催者 Addison Howard の回答 |
| **チームで有効な提出は2つだけ**。新しく出すと、古いほうは対戦を止める | #739410（「Each team keeps two active submissions」）、#739179（「A submission only stops receiving episodes when its own team fields newer ones」） |
| **締め切り（9/30）のあと2週間は対戦が続き、最後に1回の Bradley-Terry トーナメントで最終順位を決める**。対象は締め切り時点で有効な提出どうしの対戦 | #731587（主催者 María Cruz）、#739410 |
| **チームの成績は2つのうち良いほう**。2つ目の枠は「損のない保険」 | #739410、主催者の回答 |
| 引き分けは双方に 0.5 勝 | 同上 |
| **公開ノートブックの共有は 9/23 23:59 UTC で締め切り** | #741281、主催者の回答 |

→ **提出の運用ルール（2026-09-19 から）**：
- 有効な2枠には、常に**一番強い2本**を置く。次に提出すると**古いほうが外れる**ことを必ず確認してから出す。
- 最終順位は表示レーティングではなく、締め切り後のトーナメントの勝敗で決まる。**物差しは試合の勝率**（doc 05）。
- 9/23 以降、公開エージェントの顔ぶれは固まる。最終トーナメントの相手には、強い公開エージェントのコピーが多いと考える。

publicScore はレーティングで、**新規提出は必ず 600.0 から始まり公開対戦が進むほど動く**。
提出直後の値は実力を表さない（v1 は 600.0 → 509.1 まで下がってから 519.3 に戻した）。
リーダーボードに載るのはチームにつき1スコア。
~~古い提出も公開対戦を続ける~~ → **訂正（2026-09-19）：続けるのは直近の2つだけ。** v2 の提出後に v1 が動いたのは、
v1・v2 が有効な2枠だったため。v3 の提出後は v1 が 522.0 で止まり、v2 は v4 の提出まで動いていた（526.5 → 501.4）。
~~現在の有効な2枠：v4（56354076）と v6（56357846）~~
→ **訂正（2026-09-20）：k256net とチームを組んだ（チーム名「giyogoioがすべてのエージェントを破壊します」、
TeamId 16921670、メンバー giyogoiohlrlqll・k256net）。有効な2枠と1日5本の上限はチームで共有する。**
`kaggle competitions submissions kaggriculture` にチームメイトの提出も出るようになった。
チームの最新2本は **v6（56357846、11:47）と k256net の tape-router（56357787、11:45、1618.9）**。
各提出の最後の公開対戦は v4 と 56356582 が 9/19 17:17 で止まり、v6（18:41）と 56357787（17:53）だけが続いている
（`kaggle competitions episodes <ID> -v` で確認）。→ **v4 はもう有効枠にない。**
リーダーボード（2026-09-19 18:45 UTC のスナップショット）：チームで **2823.2、110位 / 9,573**（銅ライン 957位 = 2441.7）。
チームメイトの提出：56352751「2945 Farm + clone-aware front-run h2」2827.2（有効枠外）、56356582（同じものの2本目）2328.7、
56350688 2289.8、56348461 2345.6 ほか。**チームメイトも v9/4 を土台に「コピーより先に売る」系を作っている。**
→ **提出の運用ルールの追加（2026-09-20）**：提出する前に、どちらが出すか・どの2本を残すかをチームで合わせる。
新しく出すと、**チーム全体で古いほう**が外れる。チーム内ではコードを共有してよい（doc 08 §5）。いずれにせよ**版どうしの比較は
レーティングではなく `scripts\eval.py` のペア差で行う**（doc 05 §3）。
