# AGENTS.md — Kaggriculture 共通作業ルール

このファイルが Claude Code / Codex 共通ルールの正。Claude は `CLAUDE.md` 経由、Codex は直接読む。共通ルールはここだけを直し、`CLAUDE.md` には Claude 固有事項だけを書く。

## 0. ユーザー・競技運用

- 返答・説明・doc は日本語（コード識別子、コミット／提出メッセージは英語可）。「いいよ」「はい」「お願い」など短い返事も承認として扱う。
- **Kaggle 提出（`kaggle competitions submit`）はユーザーだけが行う。** エージェントはコマンド提示まで。
- 公開対戦は勝敗双方を調べ、勝因・敗因をデータで確認する。
- 2026-09-20以降は k256net とのチーム「giyogoioがすべてのエージェントを破壊します」。有効2枠・1日5提出を共有するため、提出提案時は外れる提出を示す（`docs/06_submission.md`）。
- 締切は **2026-10-01 09:00 JST**（正確には 09-30 23:59 UTC＝10-01 08:59 JST、`docs/08_competition_rules.md`）。

## 1. 作業開始・引き継ぎ

会話記憶は共有されないため、Claude/Codex間の引き継ぎはファイルだけで行う。

1. 同時編集しない（他方の作業中は閲覧のみ）。
2. 開始時に `git status`、`git log --oneline -5`、`docs/roadmap.md`、対象docを読む。未コミット変更は途中作業として保護し、勝手に戻す／上書きしない。不明ならユーザーに確認する。
3. 終了・中断時はroadmapと、必要なら`docs/experiments/`へ、日付つきで「完了範囲・次・未確認」を残す。会話だけに結論を残さない。
4. 一時物はリポジトリ外へ。再利用する分析だけを`scripts\analysis\`へ置く。
5. コミット／pushはユーザー指示時だけ。メッセージに`[codex]`または`[claude]`を付ける。

## 2. ドキュメント駆動開発

仕様の正は`docs/`で、コードはその実装。AGENTS/CLAUDEにはルールと索引だけを書く。

- 新機能・仕様変更はdocを先に作成／更新し、ユーザー承認で`Approved`になってから実装する。`Draft`は実装不可。
- 仕様とのズレ・不明点が出たら実装で補わず、doc更新→再承認。推測は書かず、実データで確認する。未確認は`TODO(要確認)`。
- 受け入れテスト→実装→全条件確認→docを`Implemented`（実装パス・テスト方法・判明事実を追記）→roadmap更新、の順に進める。
- 小さなbug/typoは事前doc・承認を省略可。ただし挙動が変わるならdocも直す。
- 重要判断は`docs/adr/`へ。過去ADRは書き換えず、新ADRで`Superseded`にする。実験は悪い結果も`docs/experiments/`へ残す。
- docヘッダ：`状態: Draft | Approved | Implemented | Deprecated`、`最終更新: YYYY-MM-DD`、`関連: ...`。

### 索引

| パス | 内容 |
|---|---|
| `docs/00_overview.md` | 目的・スコープ・用語 |
| `docs/01_requirements.md` | 要件・制約 |
| `docs/02_data_pipeline.md` | 上位50チームのリプレイ取得 |
| `docs/03_replay_schema.md` | リプレイJSON構造（実データ確認後に確定） |
| `docs/04_model_design.md` | 模倣学習設計 |
| `docs/05_evaluation.md` | 評価方法・合格基準・分析ツール一覧（§8） |
| `docs/06_submission.md` | 提出・事前確認・有効2枠・チーム |
| `docs/07_v4_improvement.md` | 公開v9/4ベースの改善計画 |
| `docs/08_competition_rules.md` | 競技ルール・締切・ライセンス（§5） |
| `docs/handover.md` | 直近の引き継ぎ |
| `docs/roadmap.md` | タスク状態 |
| `docs/adr/`, `docs/experiments/` | 設計判断・実験ログ（各`_template.md`あり） |

## 3. 環境・構成

- Windows、GPUなし。重い学習はKaggle Notebook。仮想環境は`.venv`。
- ユーザー向けコマンドはcmd構文（`\`、`%VAR%`）で示す。

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -U kaggle kaggle-environments numpy pandas scikit-learn lightgbm tqdm pytest
.venv\Scripts\python.exe -m pytest tests
```

- Kaggle認証は`%USERPROFILE%\.kaggle\kaggle.json`（コミット禁止）。
- 対戦は`scripts\eval.py`（doc 05 §1）、公開対戦分析・相手特定・台帳・公開notebook取込は`scripts\analysis\`。
- コンペページ取得：`.venv\Scripts\kaggle.exe competitions pages kaggriculture list kaggriculture --content --format json`（コンペ名は2回必要）。
- 主要構成：`docs/`仕様、`agent/`自作実行層、`submissions/`版別提出物（`main.py`・tar・SHA付き`SOURCE.md`）、`opponents/`手元評価専用、`scripts/`処理群、`tests/`、`data/`、`models/`、`baselines/`。ルート`main.py`は旧v2で現提出物ではない。`data/raw`と`data/dataset`はコミットしない。
- 各script/moduleの先頭docstringに対応docのパス・節を書く。

## 4. 安全・評価・ファイル管理

- **今後絶対に使わないと断定できるファイルだけ削除可。** 再利用・検証・監査・再現・引き継ぎの可能性が少しでもある／判断不能なら残す。
- 長時間処理は少量（例：2チーム×2エピソード）で確認後に全量実行する。CPUを使う評価・テストは重ねず、時間計測への干渉を避ける。
- **対戦・評価は非表示バックグラウンドrunnerで実行し、結果JSON・ログ・monitor JSONを出す。必ず独立watcherも同時起動し、監視なしの孤立処理を作らない。**
- バックグラウンド処理の起動・正常停止・異常停止は、JST時刻・処理名・PIDつきで`data\automation\background-processes.log`へ追記する（共通部品：`scripts\background_log.py`）。
- 複数段階が決まっている場合は、先行結果で合否判定・記録・安全な次段階へ遷移する1つの監視付きrunnerにまとめる。
- 起動後、AIは`Wait-Process`、sleep、定期ポーリングを行わず、そのターンを終了してユーザーへ制御を返す。次のユーザー指示時にmonitor/watcherを読み、完了済みなら直ちに次工程へ進む。ユーザーが明示的に待機・継続監視を頼んだ場合のみ待つ。実行中も低負荷の会話・閲覧・編集は可。
- 認証情報・生リプレイ・大容量データはコミットしない。提出前は`docs/06_submission.md`のチェックリストを通す。
- `submissions\thomas_v94\main.py`（公開v9/4原本、Apache-2.0）は変更禁止。改良は末尾層とし、先頭バイト一致をテストする（例：`tests\test_v7_relax.py`）。
- **公開notebookのセルは実行しない。** AST/リテラルだけで取り込み、監査する。提出コードは商用利用を制限しないOSI承認ライセンスに限る。

## 5. 既知の落とし穴

- Kaggleはファイル内で最後に現れるcallableをagentとして読み、`__file__`はない。1ターン制限1秒、自前基準は最悪200ms未満。
- kaggle-environmentsはstdoutを取り込むため、debugは`sys.__stderr__`へ出す。
- 関数wrapperは`functools.update_wrapper`で属性を引き継ぐ（v9/4は関数属性を使用）。
- heredoc/sedでWindowsパスを書くと`\t`・`\v`等が制御文字化する。ファイル編集ツールを使い、`[\x00-\x09\x0b\x0c\x0e-\x1f]`がないか確認する。
- Python出力の文字化け対策は`PYTHONIOENCODING=utf-8`。
