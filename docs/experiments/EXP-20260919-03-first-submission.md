# EXP-20260919-03: 初回提出（フェーズ0 ルールベース・ベースライン）

日付: 2026-09-19
関連 doc: 06_submission.md, 05_evaluation.md §4, 04_model_design.md §5
コミット: （git 未使用）

## 目的

模倣学習に進む前に、**提出経路を一度通す**。あわせてリーダーボード上の実力を測り、
ローカル評価（対 `starter`）との対応を見る。

## 提出物

| 項目 | 内容 |
|---|---|
| submissionId | **56333848**（1回目 56333731 は ERROR。下記） |
| ファイル | `submission.tar.gz`（8,917 bytes）。中身は `main.py`, `agent/{__init__,features,macro,execute}.py` |
| 提出日時 | 2026-09-18 15:32 UTC |
| 説明 | `phase0 baseline v2 (fix __file__ NameError)` |
| 残り提出回数 | 3／日（上限5） |

## preflight（`scripts\preflight.py`、720ターン）

2回目（修正後）の出力。3行目が今回追加したチェック。

```
[OK  ] 提出物が揃っている … 2項目、合計 25,868 bytes
[OK  ] main.py の最後の関数が agent … 最後の関数: agent
[OK  ] Kaggle と同じ方法で読み込める … 最後の callable: agent
[OK  ] 標準ライブラリと自前モジュールだけを import している … 外部ライブラリなし
[OK  ] 行動の形式が正しい … {'farmer': ['PASS'], 'hands': [], 'market': []}
[OK  ] 壊れた観測でも落ちない … 5パターン確認
[OK  ] 1ターンの推論が 50ms 未満で完走する … 中央値 0.96ms / 最悪 3.72ms / status DONE
```

## 提出前のローカル評価（`eval.py main.py starter -n 20 -j 4`）

```
勝敗          : 20勝 0敗 0分（ペア単位）
ペア差        : +57,030 ± 1,945
最終所持金    : A 中央値 62,044 / B 中央値 3,534
例外          : A 0件 / B 0件
健全性(A)     : 植え付け 55 → 収穫 33 / 枯死 10（weed自然発生 8）/ 家畜逃走 4 / 最終shed 30
```

## チェックリストの状態（doc 06）

| # | 項目 | 結果 |
|---|---|---|
| 1 | 05 の合格基準を満たした | **一部未達**（下記） |
| 2 | `preflight.py` が通る | OK |
| 3 | `main.py` の最後の関数が `agent` | OK |
| 4 | try/except とフォールバック | OK |
| 5 | 提出環境に無いライブラリを import していない | OK |
| 6 | `docs/experiments/` に記録 | この文書 |

**未達のまま提出した項目（doc 05 §4）**

- **家畜の逃走ゼロ → 平均4頭/試合**（EXP-20260919-02）
- **枯死が植え付けの5%以下 → 10/55 = 18%**

「直前の提出版に対してペア差がプラス」は初回のため対象外。
`starter` に全勝（20/20）、推論 <50ms、例外ゼロは満たしている。
**未達を承知のうえで、提出経路の確認とリーダーボード基準の把握を優先して提出した。**

## 1回目の提出（56333731）は ERROR

Validation Episode は COMPLETED になったが、提出は `SubmissionStatus.ERROR`。
`kaggle competitions logs 110483236 0` で取得したエージェントログ：

```
File "/kaggle_simulations/agent/main.py", line 10, in <module>
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
NameError: name '__file__' is not defined
kaggle_environments.errors.InvalidArgument: Invalid raw Python: NameError(...)
```

**原因**：Kaggle は `main.py` を `exec(compile(raw), {})` で読み込むため、
`__file__` も `__name__` も存在しない（`kaggle_environments/agent.py` の `get_last_callable`）。
`main.py` の先頭で `__file__` を使っていたため、エージェントの読み込み自体に失敗した。

**なぜ preflight で防げなかったか**：preflight が `importlib` で読み込んでいたため。
`importlib` 経由だと `__file__` が定義されるので、本番と読み込み方が違っていた。
ローカルのテストが全部通っていたのはこのため。

**対処**：

1. `main.py` は `"__file__" in globals()` で分岐する。本番では Kaggle 側が
   `main.py` のあるディレクトリを `sys.path` に追加するので、こちらで触る必要は無い。
2. preflight に **`check_kaggle_loader`** を追加。`exec(compile(raw), {})` でローダーを再現し、
   最後の callable を取り出して呼ぶところまで確認する。
   `__file__` を使う `main.py` で落ちることを確認する回帰テストも追加した。

## 結果（2回目の提出 56333848）

| 項目 | 値 |
|---|---|
| status | **COMPLETE** |
| publicScore | **600.0**（新規提出の初期レーティング。対戦が進むと動く） |
| 順位 | **5,796位 / 9,446チーム**（2026-09-18 15:35 UTC 時点） |
| Validation Episode | 110484330（COMPLETED） |

参考：上位勢の publicScore は 3,018〜3,180、最下位は −202.9。
publicScore はレーティングであり最終所持金ではない（03 §5.3）。
600.0 は**まだ公開対戦がほとんど行われていない初期値**なので、実力の評価には使えない。
数時間〜1日おいて再確認する。

## v1 のレーティングの推移（2026-09-19 追記）

| 時点 | publicScore |
|---|---|
| 提出直後 | 600.0（初期値） |
| 約12時間後 | 509.1 |
| 約19時間後 | **519.3** |

**600 は初期値であって実力ではない**ことが確認できた。公開対戦が進むと 509 まで下がり、
そこから微増して 519 で落ち着いた。これが v1 の実力に近い（上位勢は 3,000 超）。
この落差の原因分析が EXP-20260919-04（公開対戦のリプレイ分析）。

## 次のアクション（状態）

1. ~~レーティングが動いたら追記~~ → 上記のとおり 519.3。分析は EXP-20260919-04。
2. 実行層の改善 → EXP-20260919-05。採用は `cash_floor` 800 のみ（対 v1 +14,029 ± 1,402）。
   v2 として提出済み（56346388、下記）。
3. 枯死（未達）とフェーズ1（マクロ模倣）は未着手。

## v2 の提出（56346388、2026-09-19 02:49 UTC）

| 項目 | 値 |
|---|---|
| 説明 | `v2: cash_floor 800 (+14029 vs v1, 20/20 pairs, zero animal escapes)` |
| preflight | 7項目すべて OK（最悪ターン 3.40ms、アーカイブ 8,989 bytes） |
| status | **COMPLETE**（Validation は提出から約5分で完了） |
| publicScore | 600.0（初期値）／**5,806位 / 9,480チーム** |

**この 600.0 は初期値なので、v1 の 519.3 と比べてはいけない。**
v1 のときと同様、公開対戦が溜まるまで（十数時間）待ってから読む。
v1 との実力差はローカルのペア差（+14,029 ± 1,402、20/20）で既に測ってある。
