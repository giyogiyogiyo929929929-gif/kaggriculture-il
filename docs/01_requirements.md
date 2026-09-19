# 01 要件

状態: Approved
最終更新: 2026-09-18
関連: 00_overview.md, 06_submission.md

## 機能要件

- FR-1 上位50チームのリプレイを公式 Kaggle CLI で取得できる
- FR-2 リプレイをダイジェストに変換し、生データを削除できる
- FR-3 ダイジェストから (状態特徴, マクロ行動) の学習データを作れる
- FR-4 上位勢の行動傾向を集計できる（パターン分析）
- FR-5 模倣モデルを学習し、提出用の軽量形式に書き出せる
- FR-6 ローカルで対戦評価ができる
- FR-7 Kaggle に提出できる `main.py` / `submission.tar.gz` を作れる

## 非機能要件・制約

- NFR-1 1ターンの推論は**最悪 200ms 未満**（`actTimeout` 1秒の1/5）かつ **99%のターンが 50ms 未満**
  （★2026-09-19 改訂。以前は「最悪でも数十ms以内」。公開エージェント v9/4 は最悪 54.9ms・99%点 5.7ms。EXP-20260919-11）
- NFR-2 agent は例外で落ちない。失敗時はルールベースのフォールバック行動を返す
- NFR-3 学習はまず CPU（GPU なしのノートPC）で回る規模。GPU が要るものは Kaggle Notebook
- NFR-4 取得スクリプトはレート制限対策・再開可能（冪等）
- NFR-5 コマンドは Windows cmd 構文
- NFR-6 取得データの再配布はコンペ規約を確認してから

## 付録：確認済みの環境（タスク 0-1 の結果、2026-09-18）

| 項目 | 実測値 |
|---|---|
| Python | 3.14.4（この PC にはこれ1本のみ） |
| 仮想環境 | `.venv`（作成済み） |
| kaggle CLI | 2.2.4 |
| kaggle-environments | 1.32.7（`envs\kaggriculture` と `kaggriculture_beginner` を同梱） |
| その他 | numpy 2.5.3 / pandas 3.0.6 / scikit-learn 1.9.1 / lightgbm 4.7.0 / pytest 9.1.1 |
| 認証 | `%USERPROFILE%\.kaggle\access_token`（`kaggle.json` は無い） |

### 既知の問題と対処

- **`pip install kaggle-environments` は Python 3.14 で失敗する。** 依存の `pygame` に 3.14 用 wheel が無く、
  ソースビルドに失敗するため。kaggriculture は pygame を使わないので `--no-deps` で入れる。

```cmd
python -m venv .venv
.venv\Scripts\python.exe -m pip install -U pip
.venv\Scripts\python.exe -m pip install -U kaggle numpy pandas scikit-learn lightgbm tqdm pytest
.venv\Scripts\python.exe -m pip install --no-deps kaggle-environments
```

- `make("kaggriculture")` は上記構成で動作する（`open_spiel_env` の読み込み失敗メッセージが出るが無害）。
- ゲームのルール・観測・行動の正は
  `.venv\Lib\site-packages\kaggle_environments\envs\kaggriculture\README.md`。
