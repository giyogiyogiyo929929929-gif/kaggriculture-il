# 出典：v6_preempt（v5 ＋ 候補A2「コピーの PREDICT を1ターン先回りする」＋ 安全包み）

状態: 提出候補 v6（doc 07 §3 候補A2 の受け入れ条件をすべて満たした）
作成日: 2026-09-19
関連: doc 07 §3 候補A・A2, EXP-20260919-14, `submissions\v5_race\SOURCE.md`, `submissions\thomas_v94\SOURCE.md`（原本の出典）

| 項目 | 内容 |
|---|---|
| 元 | `submissions\thomas_v94\main.py`（thomastschinkel「The 2945 Farm」v9/4、Apache-2.0） |
| 作り方 | `.venv\Scripts\python.exe scripts\build_v6_preempt.py`（v5_race の安全包みの前まで ＋ 候補A2 の層 ＋ 安全包み） |
| 改変 | **末尾に層を足しただけ**。先頭 856,428 バイトは原本と同一（SHA-256 `bfee70e9…`）。候補A の層は v5 と同一（`tests\test_v6_preempt.py`） |
| SHA-256（main.py） | `3cdfe0eeb251b3583640af0cecc5c66805c46db3d0ff804b9913894beb47629d`（863,730 bytes） |
| SHA-256（submission.tar.gz） | `bfa042bc0ee7b257684eaa1dd57ced46b90570f681cf0ec367cf841eea8d7ef1`（526,991 bytes、中身は main.py のみ） |
| エントリ | `_kil_safe_agent(observation, configuration=None)`（最後の callable） |

## 層の中身

- 候補A（v5 と同じ）：167ステップまで農場が一致し続けたらコピーと確定し、売りの先読み幅を 52 にする。
- 候補A2：コピーと確定した試合だけ、コピーの PREDICT（`_v92_predict`）が次のターンに発火するかを
  v9/4 自身の `_v92_p_forecast` で計算し、発火するなら同じ売りを1ターン前に出す。
- コピー以外の相手には何もしない（別系統11本との220試合で、所持金が v4 と1試合残らず完全一致）。

## 提出コマンド（ユーザーが実行）

```cmd
.venv\Scripts\kaggle.exe competitions submit kaggriculture -f submissions\v6_preempt\submission.tar.gz -m "v6: v9/4 + copy-race H52 + PREDICT pre-empt (vs v4 35-5)"
```
