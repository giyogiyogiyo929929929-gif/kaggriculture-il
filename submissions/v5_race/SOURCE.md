# 出典：v5_race（v9/4 ＋ 候補A「コピー相手のときだけ売りの先読みを深くする」＋ 安全包み）

状態: 提出候補 v5（doc 07 §6 の受け入れ条件をすべて満たした）
作成日: 2026-09-19
関連: doc 07 §3 候補A・§4, EXP-20260919-14, `submissions\thomas_v94\SOURCE.md`（原本の出典）, `submissions\thomas_v94_safe\SOURCE.md`（v4）

| 項目 | 内容 |
|---|---|
| 元 | `submissions\thomas_v94\main.py`（thomastschinkel「The 2945 Farm」v9/4、Apache-2.0） |
| 作り方 | `.venv\Scripts\python.exe scripts\build_v5_race.py`（原本 ＋ 候補A の層 ＋ v4 と同じ安全包み） |
| 改変 | **末尾に層を足しただけ**。先頭 856,428 バイトは原本と同一（SHA-256 `bfee70e9…`。`tests\test_v5_race.py` で確認） |
| SHA-256（main.py） | `a7b564d09c5a0416af2835ef5ef44c8ac0a83854cf46c5ba5a44bac0d656fca2`（859,536 bytes） |
| SHA-256（submission.tar.gz） | `b49430fd1678249cb1a576aae2be639f25463220b16baf225ac54b15b28e2359`（525,874 bytes、中身は main.py のみ） |
| エントリ | `_kil_safe_agent(observation, configuration=None)`（最後の callable） |

## 層の中身（doc 07 §3 候補A）

- **判定**：雑草タイルを空きとみなした自分と相手の農場が、167ステップ目まで毎ターン一致し続けたら v9/4 のコピーと確定。
  一度でも違えばその試合では二度と反応しない。確定後は比べない。
- **動き**：確定後だけ、v9/4 の `V9_RACE_DEFAULT` / `V9_RACE_MAX`（通常 40 / 48）を呼び出しの間だけ 52 にする。
- コピー以外の相手には何もしない（別系統11本との220試合で、所持金が v4 と1試合残らず完全一致）。

## 提出コマンド（ユーザーが実行）

```cmd
.venv\Scripts\kaggle.exe competitions submit kaggriculture -f submissions\v5_race\submission.tar.gz -m "v5: v9/4 + copy-race H52 (vs v4 27-7-6)"
```
