# AGENTS.md — Kaggriculture エージェント開発（Claude Code / Codex 共通の作業ルール）

このファイルが**作業ルールの正**。Claude Code は `CLAUDE.md` から、Codex はこのファイルを直接読む。
ルールを変えるときはこのファイルだけを直す（`CLAUDE.md` には Claude 固有のことだけを書く）。

## 0. 返答とユーザー

- **ユーザーへの返答・説明・doc はすべて日本語で書く。**（コード中の識別子、コミットメッセージ、提出メッセージは英語でよい）
- ユーザーは短い返事（「いいよ」「はい」「お願い」）で承認する。
- **Kaggle への提出（`kaggle competitions submit`）はユーザーが自分で実行する。** エージェントは提出コマンドを示すだけ。
- 公開対戦・評価の分析では、**負けた試合だけでなく勝った試合も調べ、「なぜ勝てたか」をデータで確かめる。**
- **チーム戦（2026-09-20〜）**：k256net とチーム（「giyogoioがすべてのエージェントを破壊します」）。
  有効な2枠と1日5本の提出上限はチームで共有する。提出を勧める前に、どの提出が外れるかを必ず示す（`docs/06_submission.md`）。
- **最終提出の締め切り：2026-10-01 09:00 JST（正確には 09-30 23:59 UTC ＝ 10-01 08:59 JST）。**（`docs/08_competition_rules.md`）

## 0.1 Claude Code と Codex の引き継ぎ

このフォルダは Claude Code と Codex の両方で作業する。お互いの会話の記憶は見えないので、**引き継ぎはファイルだけで行う。**

1. **同時に作業しない。** 片方が作業している間、もう片方は同じフォルダを編集しない（読むだけならよい）。
2. **作業を始めるとき**：`git status` と `git log --oneline -5` で、前の作業の未コミットの変更と最近のコミットを確認する。
   未コミットの変更は前の作業の途中なので、**勝手に戻したり上書きしたりしない**（分からなければユーザーに聞く）。
   次に `docs/roadmap.md` と対象タスクの doc を読む。
3. **作業を終えるとき（途中で止めるときも）**：`docs/roadmap.md` の該当タスクの状態欄に、
   「どこまでやったか・次に何をするか・未確認のこと」を日付つきで書く。実験なら `docs/experiments/` にも書く。
   会話の中にしか無い結論を残さない。
4. 一時ファイル・使い捨てスクリプトはリポジトリの外（各ツールの作業用フォルダ）に置く。繰り返し使うものだけ `scripts\analysis\` に足す。
5. **コミット・プッシュはユーザーが指示したときだけ。** コミットメッセージにどちらのツールで作業したかを書く（例：`[codex]`、`[claude]`）。

## 1. このリポジトリは「ドキュメント駆動開発」で進める

**仕様の正（source of truth）は `docs/` にある。コードはドキュメントの実装にすぎない。**
AGENTS.md / CLAUDE.md には作業ルールと索引だけを書き、仕様の中身は docs に書く。

### 鉄則

1. **ドキュメントより先にコードを書かない。** 新機能・仕様変更は、まず該当する docs を作成／更新する。
2. **状態が `Approved` のドキュメントだけを実装してよい。** `Draft` のまま実装を始めない。承認はユーザーが行う（エージェントは「Approved にしてよいか」を確認する）。
3. **実装中に仕様とのズレや不明点が出たら、コードで勝手に解決せず、作業を止めて docs を更新 → 再承認。**
4. 実装が終わったら、docs の状態を `Implemented` にし、実装ファイルへのパスとテスト方法を追記する。
5. **推測で仕様を書かない。** リプレイ形式・CSV 列名などは実データを確認し、確認済みの事実として docs に書く。未確認のものは `TODO(要確認)` と明記する。
6. 重要な設計判断は `docs/adr/` に ADR として残す。過去の ADR は書き換えず、覆すときは新しい ADR で `Superseded` にする。
7. 実験（学習・評価）は結果が悪くても `docs/experiments/` に記録する。

### 1タスクの流れ

```
① 対象 doc を読む／なければテンプレから作る（状態: Draft）
② ユーザーにレビュー依頼 → 承認されたら Approved
③ doc の「受け入れ条件」を満たすテストを先に書く
④ 実装
⑤ 受け入れ条件を全部確認
⑥ doc を Implemented に更新（実装パス・コマンド・判明した事実を追記）
⑦ docs/roadmap.md のタスク状態を更新
```

小さなバグ修正や typo は①②を省略してよいが、挙動が変わるなら docs も直す。

### ドキュメントのヘッダ（全 doc 共通）

```
状態: Draft | Approved | Implemented | Deprecated
最終更新: YYYY-MM-DD
関連: 他の doc / ADR へのリンク
```

## 2. ドキュメント索引

| doc | 内容 |
|---|---|
| `docs/00_overview.md` | 目的・スコープ・用語集 |
| `docs/01_requirements.md` | 機能要件・非機能要件・制約 |
| `docs/02_data_pipeline.md` | 上位50チームのリプレイ取得仕様 |
| `docs/03_replay_schema.md` | リプレイ JSON の構造（実データ確認後に確定） |
| `docs/04_model_design.md` | 模倣学習の設計（特徴量・行動表現・モデル） |
| `docs/05_evaluation.md` | 評価方法・合格基準 |
| `docs/06_submission.md` | 提出手順・提出前チェック・有効な2枠・チーム |
| `docs/07_v4_improvement.md` | v4（公開 v9/4）を土台にした改善の計画（銅メダル） |
| `docs/08_competition_rules.md` | コンペの概要とルールの日本語まとめ・締め切り（10/1 09:00 JST） |
| `docs/roadmap.md` | フェーズとタスクの状態 |
| `docs/adr/` | 設計判断の記録（`_template.md` あり） |
| `docs/experiments/` | 実験ログ（`_template.md` あり） |

**作業を始める前に、必ず `docs/roadmap.md` と対象タスクの doc を読むこと。**

## 3. 開発環境

- OS は Windows。**ユーザーに示すシェルコマンドはすべてコマンドプロンプト（cmd）構文**（パス区切り `\`、環境変数 `%VAR%`）。
- GPU なしのノートPC。重い学習は Kaggle Notebook で回す。
- 仮想環境は `.venv`。

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -U kaggle kaggle-environments numpy pandas scikit-learn lightgbm tqdm pytest
```

- Kaggle 認証情報は `%USERPROFILE%\.kaggle\kaggle.json`。**コミット禁止。**
- テスト：`.venv\Scripts\python.exe -m pytest tests`
- 対戦評価：`scripts\eval.py`（doc 05 §1）。公開対戦の分析・相手の特定・台帳・公開ノートブックの取り込みは
  `scripts\analysis\`（使い方の一覧は doc 05 §8）。使い捨ての分析はリポジトリの外に置き、繰り返し使うものだけここに足す。
- コンペのページ（概要・規約・遊び方）は CLI で読める（コンペ名を2回書くのが必要）：
  `.venv\Scripts\kaggle.exe competitions pages kaggriculture list kaggriculture --content --format json`

## 4. ディレクトリ構成

```
kaggriculture-il/
├─ AGENTS.md        # 作業ルールの正（Claude / Codex 共通）
├─ CLAUDE.md        # Claude Code 用の入口（AGENTS.md を読み込む）
├─ docs/            # 仕様（正）
├─ main.py          # 初期の自作エージェント（v2。今の提出物ではない）
├─ agent/           # 特徴量化・行動デコード・ルール実行層（自作版）
├─ submissions/     # 提出物。版ごとに main.py・submission.tar.gz・SOURCE.md（SHA-256）
├─ opponents/       # 手元評価用の公開エージェント（提出物には入れない）
├─ baselines/
├─ scripts/         # 取得・変換・学習・評価・組み立てスクリプト
├─ tests/
├─ data/            # meta/ raw/ digest/ dataset/ eval/（raw と dataset はコミットしない）
└─ models/
```

各スクリプト・モジュールの先頭 docstring に、**対応する doc のパスと節**を書く（例：`仕様: docs/02_data_pipeline.md §3`）。

## 5. その他の作業ルール

- 長時間の取得・学習は、まず少量（例：2チーム×2エピソード）で動作確認してから全量。
- 認証情報・生リプレイ・大きなデータはコミットしない。
- 提出前は必ず `docs/06_submission.md` のチェックリストを通す。
- **`submissions\thomas_v94\main.py`（公開 v9/4 の原本、Apache-2.0）は書き換えない。** 改良は後ろに層を足す形で行い、
  先頭バイトが原本と一致することをテストで確かめる（例：`tests\test_v7_relax.py`）。
- **公開ノートブックのセルは実行しない。** 取り込みは ast / リテラルの読み取りだけで行い、中身を監査する。
- 提出に使うコードは、OSI 承認で商用利用を制限しないライセンスに限る（コンペ規約。`docs/08_competition_rules.md` §5）。

## 6. 既知の落とし穴

- Kaggle はエージェントを**ファイルの最後の callable**として読み込み、`__file__` は無い。1ターン 1 秒制限（自前の基準は最悪 200ms 未満）。
- kaggle-environments はエージェントの stdout を取り込むので、デバッグ出力は `sys.__stderr__` に出す。
- エージェントを関数で包むときは `functools.update_wrapper` で属性を引き継ぐ（v9/4 は関数属性を使う）。
- シェルの heredoc や sed で Windows パスを書くと `\t` `\v` などが制御文字に化ける。doc やスクリプトはファイル編集ツールで書き、
  書いた後に制御文字（タブを含む `[\x00-\x09\x0b\x0c\x0e-\x1f]`）が無いか確かめる。
- 文字化け対策：Python の出力は `PYTHONIOENCODING=utf-8`。
