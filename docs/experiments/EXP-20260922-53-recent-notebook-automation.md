# EXP-20260922-53: Recently run 公開ノート自動対戦

状態: Implemented（2026-09-22）
日付: 2026-09-22
関連 doc: 05_evaluation.md §8、08_competition_rules.md §5、AGENTS.md §4
コミット: 未コミット

## 仮説

Kaggle の `kaggriculture` 公開ノートを `dateRun` 順で約1時間ごとに確認し、新規または更新されたノートだけを既存候補と自動対戦させれば、新しい戦術への追随を手作業より早くできる。

## 設定（取得・監査・評価）

- 一覧取得: `python -m kaggle kernels list --competition kaggriculture --sort-by dateRun --format json`
- 版の識別: `ref + lastRunTime`
- 初回起動: 現在の一覧を基準として登録し、過去分は評価しない
- 取得: 公式 Kaggle CLI の `kernels pull`
- 抽出: 既存 `scripts/analysis/extract_notebook_agents.py`。ノートのセルは実行しない
- 安全ゲート: 既存 `audit_agent.py` の静的監査で警告0件、構文解析成功、preflight成功
- 対戦: 既存 `scripts/eval.py`、既定候補 `submissions/v27_orderbook_layer_d/main.py`、3ペア、`-j 1`
- 重複: 抽出コードの SHA-256 が既評価なら再対戦しない
- 常駐: runner と独立 watcher を別プロセスで起動し、monitor/state/result/logを永続化する
- 失敗時: そのノートだけ隔離・記録し、常駐処理は次回巡回を続ける
- 提出・採用: 自動では行わない

## 結果（05_evaluation.md の形式で）

- `recent_notebook_service.py`、独立watcher、非表示launcherを実装。
- 単体テスト7件合格。構文コンパイルも合格。
- 本番データ領域で `--once` を実行し、recently run 100本を初回基準として登録。新規0件、終了コード0。
- 2026-09-22 16:15 JST、1時間間隔・上位100本・3ペア・`-j 1`・候補v27で常駐開始。
  起動時PIDはrunner 21364、watcher 25372。以後の生存状態はmonitor/watcher JSONを正とする。
- バックグラウンド処理の共通履歴を `data/automation/background-processes.log` に追加。以後のlauncherは
  runner/watcherの起動を記録し、各プロセスは正常停止・異常停止をJST時刻・処理名・PID付きで追記する。

## 考察

公開コードの自動実行は危険なため、静的監査に1件でも警告があるものは対戦を行わない。取り逃しより安全性を優先し、隔離されたノートは人手確認できる形で残す。

## 次のアクション

1. 次のユーザー指示時に `monitor.json` と `watcher.json` を確認する。
2. 新規版を検出したら結果JSONを読み、勝敗・差額・安全隔離数を報告する。
