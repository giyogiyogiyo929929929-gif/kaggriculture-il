# EXP-20260920-31: v12 の提出前最終チェック

状態: Implemented（チェック完了・特例承認後にsubmission 56398792として提出）
最終更新: 2026-09-21
関連: ../06_submission.md 提出前チェックリスト, ../adr/0004-switch-base-to-v51.md 第1段, ../roadmap.md 3-18
コミット: 未コミット（Codex）

## 目的

`submissions\v12_v51safe\` を提出できる状態か、doc 06のチェックリストに沿って再確認する。
提出は行わない。性能評価はEXP-20260920-29、v12と記録層だけのv13の同一性はEXP-20260920-30を使う。

## 方法

```cmd
set PYTHONDONTWRITEBYTECODE=1
set PYTHONIOENCODING=utf-8
.venv\Scripts\python.exe scripts\preflight.py --main submissions\v12_v51safe\main.py --entry _kil_safe_agent --build --output submissions\v12_v51safe\submission.tar.gz --json data\eval\v12_v51safe_preflight.json
.venv\Scripts\python.exe -m pytest tests\test_v12_v51safe.py tests\test_preflight.py -q -p no:cacheprovider
.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
.venv\Scripts\python.exe scripts\analysis\audit_agent.py submissions\v12_v51safe\main.py
.venv\Scripts\python.exe scripts\eval.py submissions\v12_v51safe\main.py submissions\v10_de\main.py -n 20 -j 4 --seed-start 301 --json data\eval\v12_vs_v10_preflight.json
.venv\Scripts\python.exe scripts\eval.py submissions\v12_v51safe\main.py starter -n 20 -j 4 --seed-start 301 --json data\eval\v12_vs_starter_preflight.json
.venv\Scripts\kaggle.exe competitions submissions -c kaggriculture --csv
.venv\Scripts\kaggle.exe competitions submission-limits kaggriculture
```

再ビルド前後のmain.pyのSHA-256を比較し、tarをPythonの`tarfile`で読み、メンバー名と中身のバイトを確認した。
有効枠は提出一覧の時刻と、v10・56384238の両方に14時台まで公開対戦が付いていることで確認した。

## 結果

- preflight：全項目OK。中央値0.81ms、p99 6.15ms、最悪36.26ms、720ターン完走、status DONE。
- エントリ：最後のcallableは `_kil_safe_agent`。Kaggleと同じ方法で読み込め、壊れた観測5パターンでも落ちない。
- 依存：外部ライブラリなし、模倣モデルなし。提出物はmain.pyだけ。
- テスト：v12＋preflightの29件合格。全テスト **229件合格（37.65秒）**。
- 原本：v51の先頭461,739 bytesと一致。main.pyは再ビルド前後で同じSHA-256
  `fd3231bd638414cbcdd9246be88f544f5367e365388e5debb24fee18834ab652`。
- アーカイブ：171,702 bytes、SHA-256
  `7276f33bc3e1ec3d62cfea90a6e2c46cb81d6c5c73bb1d89d50028fc91dc3cd4`。
  メンバーはルートの `main.py` だけで、提出候補のmain.pyと1バイト一致。
- コード監査：注意0件。Apache License 2.0本文とSPDX表示を保持。
- 既存の性能評価：手元27本で246勝24敗（v10は207勝63敗）、例外0（EXP-29）。
  EXP-30でもv12を280試合実行し、全試合720ターン・DONE、内側を含め例外0。
- **直前提出v10との直接比較は不合格**：未使用seed 301〜320の20ペアで **7勝13敗、−137 ±272**。
  doc 05 §4の「平均がプラス、標準誤差の2倍以上」を満たさない。差の絶対値は小さく、ゼロとの差も有意ではない。
- starter：20勝0敗、+170,260 ±5,367。例外0、家畜逃走0、作物損失1/237（0.4%）、最終shed 0。
  並列実行の最悪時間は採用せず、時間基準は単独preflightの値を使う。
- 提出枠：v10（56392177、11:21 UTC）とk256netの56384238（07:00 UTC）が有効。
  **現時点でv12を次に出すと古い56384238が外れ、v10とv12が残る。**
  本日の提出は3本、残り2本。

## 判定

コード・アーカイブ・安全性・starter戦は合格。doc 05の通常の直接比較基準は未達だが、
ADR-0004固有の相手プール基準ではv12が優位で、直接差は標準誤差未満だった。

**2026-09-21、ユーザーが「特例で提出して様子を見る」と承認。** doc 05 §4.1にv12限定の特例を記録した。
ユーザーが提出コマンドを実行し、**submission 56398792**として15:06:29 UTCに提出。Validation Episode 111264840はCOMPLETED。
初期publicScoreは600.0。有効枠はv10とv12になり、56384238は14:53 UTC開始の公開対戦を最後に停止した。
当日4本提出、残り1本。次の提出では現時点で古いv10が外れる。
