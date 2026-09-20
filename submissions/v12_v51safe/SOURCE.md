# 出典：v12_v51safe（v51 ＋ 例外時フォールバックの包み）

状態: 提出候補（ADR-0004 第1段の受け入れ条件を満たした。**まだ提出していない**）
作成日: 2026-09-20
関連: ADR-0004（土台の乗り換え）, EXP-20260920-28（取り込み）, EXP-20260920-29（分析）, doc 06

| 項目 | 内容 |
|---|---|
| 元 | `opponents\v51\main.py`（ahmedberatozer「Kaggriculture V51 — Lean Flock」、Apache-2.0。出典は `opponents\v51\SOURCE.md`） |
| 作り方 | `.venv\Scripts\python.exe scripts\build_v12_v51safe.py` |
| 改変 | **先頭 461,739 バイトは v51 の原本と完全に一致**（SHA-256 `c1e3590d…`。`tests\test_v12_v51safe.py` で確認）。末尾に包みを足しただけ |
| SHA-256（main.py） | `fd3231bd638414cbcdd9246be88f544f5367e365388e5debb24fee18834ab652`（462,563 bytes） |
| エントリ | `_kil_safe_agent(observation, configuration=None)`（最後の callable） |
| 包みの中身 | 元の最後の callable（`_e350_agent`）を呼び、例外が出たら `{"farmer": ["PASS"], "hands": [], "market": []}` を返す（NFR-2）。v4（`thomas_v94_safe`）と同じ作り |
| ライセンス | Apache-2.0 の派生（原本の表示を保持） |

## 受け入れ条件（ADR-0004 第1段）

- [x] **手元27本で v10 より勝ち数が多い** → **246勝24敗（v10 は 207勝63敗）**。
      ★成績は `opponents\v51\main.py` で測ったもの。**v12 と v51 が同じ動きであることを6試合で確認済み**
      （相手4種・seed 6通りで所持金が1円まで一致。`opponents\v50`・`submissions\v10_de`・`gods_mode`・`metav4_v13` 相手）。
- [x] **preflight 全項目 OK** → 中央値 1.17ms / 99%点 6.65ms / 最悪 37.05ms（NFR-1）
- [x] **例外0** → 手元27本・540試合で0件
- [x] テスト → `tests\test_v12_v51safe.py` 5件

## 成績（seed 241〜250、各20試合。EXP-20260920-29）

| | v10（いまの提出） | **v12（＝v51）** |
|---|---|---|
| 手元27本の合計 | 207勝 63敗 | **246勝 24敗** |
| 相手ごとに上回った数 | 5本 | **14本** |

**負け越すのはコピー系だけ**（`gods_mode` 5-5、`peak_2950` 7-3、`smaller_market_shock` 7-3、
`thomas_v94_safe` 7-3、`yummers` 8-2 と、こちらが勝ってはいるが v10 の 10-0 には届かない）。
ここを埋めるのが ADR-0004 の第2段・第3段。

## 提出コマンド（**ユーザーが実行**。出す前にチームで合わせる）

有効な2枠は v10（56392177）と k256net の 56384238。**新しく出すと v10 が外れる**（doc 06）。

```cmd
.venv\Scripts\python.exe scripts\preflight.py --main submissions\v12_v51safe\main.py --entry _kil_safe_agent --build --output submissions\v12_v51safe\submission.tar.gz
.venv\Scripts\kaggle.exe competitions submit kaggriculture -f submissions\v12_v51safe\submission.tar.gz -m "v12: public v51 lean-flock (ahmedberatozer, Apache-2.0) + safety wrapper; 27 bots 246-24 (v10 207-63)"
```
