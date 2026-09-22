# 出典：v12_v51safe（v51 ＋ 例外時フォールバックの包み）

状態: 提出済み（submission 56398792、2026-09-20 15:06 UTC／2026-09-21 00:06 JST）
作成日: 2026-09-20
最終更新: 2026-09-21
関連: ADR-0004（土台の乗り換え）, EXP-20260920-28（取り込み）, EXP-20260920-29（分析）,
EXP-20260920-31（最終チェック）, doc 06

| 項目 | 内容 |
|---|---|
| 元 | `opponents\v51\main.py`（ahmedberatozer「Kaggriculture V51 — Lean Flock」、Apache-2.0。出典は `opponents\v51\SOURCE.md`） |
| 作り方 | `.venv\Scripts\python.exe scripts\build_v12_v51safe.py` |
| 改変 | **先頭 461,739 バイトは v51 の原本と完全に一致**（SHA-256 `c1e3590d…`。`tests\test_v12_v51safe.py` で確認）。末尾に包みを足しただけ |
| SHA-256（main.py） | `fd3231bd638414cbcdd9246be88f544f5367e365388e5debb24fee18834ab652`（462,563 bytes） |
| SHA-256（submission.tar.gz） | `7276f33bc3e1ec3d62cfea90a6e2c46cb81d6c5c73bb1d89d50028fc91dc3cd4`（171,702 bytes、内容はルートの `main.py` だけ） |
| エントリ | `_kil_safe_agent(observation, configuration=None)`（最後の callable） |
| 包みの中身 | 元の最後の callable（`_e350_agent`）を呼び、例外が出たら `{"farmer": ["PASS"], "hands": [], "market": []}` を返す（NFR-2）。v4（`thomas_v94_safe`）と同じ作り |
| ライセンス | Apache-2.0 の派生（原本の表示を保持） |

## 受け入れ条件（ADR-0004 第1段）

- [x] **手元27本で v10 より勝ち数が多い** → **246勝24敗（v10 は 207勝63敗）**。
      ★成績は `opponents\v51\main.py` で測ったもの。**v12 と v51 が同じ動きであることを6試合で確認済み**
      （相手4種・seed 6通りで所持金が1円まで一致。`opponents\v50`・`submissions\v10_de`・`gods_mode`・`metav4_v13` 相手）。
- [x] **preflight 全項目 OK** → 2026-09-20 最終確認：中央値 0.81ms / 99%点 6.15ms / 最悪 36.26ms（NFR-1）
- [x] **例外0** → 手元27本・540試合で0件
- [x] テスト → v12＋preflight の29件合格、全テスト **229件合格**
- [x] ビルド再現性 → 再ビルド前後で main.py の SHA-256 が一致。tar 内の main.py も1バイト一致
- [x] `scripts\analysis\audit_agent.py` → 注意0件。Apache-2.0 表示を保持

## doc 06 提出前チェックの判定

- [ ] **doc 05の直前提出版との比較**：未使用seed 301〜320の20ペアでv10に **7勝13敗、−137 ±272**。
  「平均差がプラス、かつ標準誤差の2倍以上」を満たさない。差自体は小さく、有意な退行とも言えないが、現行基準では不合格。
- [x] starter：20勝0敗、+170,260 ±5,367。例外0、家畜逃走0、作物損失1/237（0.4%）、最終shed 0。
- [x] preflight、アーカイブ、依存、例外、実行時間、ライセンス、全テストは上記のとおり合格。

ADR-0004固有の「27本の相手プールでv10より勝ち数が多い」は満たす一方、doc 05の汎用基準と食い違った。
2026-09-21、ユーザーが**v12に限り、相手プールの成績を優先して公開対戦で様子を見る特例を承認**。
doc 05 §4.1に記録し、提出可とした。

## 成績（seed 241〜250、各20試合。EXP-20260920-29）

| | v10（いまの提出） | **v12（＝v51）** |
|---|---|---|
| 手元27本の合計 | 207勝 63敗 | **246勝 24敗** |
| 相手ごとに上回った数 | 5本 | **14本** |

**負け越すのはコピー系だけ**（`gods_mode` 5-5、`peak_2950` 7-3、`smaller_market_shock` 7-3、
`thomas_v94_safe` 7-3、`yummers` 8-2 と、こちらが勝ってはいるが v10 の 10-0 には届かない）。
ここを埋めるのが ADR-0004 の第2段・第3段。

## 提出コマンド（**ユーザーが実行**。出す前にチームで合わせる）

**2026-09-21、ユーザーが特例提出を承認。下記はユーザーが実行する。**

有効な2枠は v10（56392177、11:21 UTC）と k256net の 56384238（07:00 UTC）。
**現時点で次に出すと、古い56384238が外れ、v10とv12が残る**（2026-09-20 14:41 UTC にCLIと直近対戦で確認）。
k256net が先に新しい提出を出すと順序が変わるため、実行前にチームで合わせる。

```cmd
.venv\Scripts\python.exe scripts\preflight.py --main submissions\v12_v51safe\main.py --entry _kil_safe_agent --build --output submissions\v12_v51safe\submission.tar.gz
.venv\Scripts\kaggle.exe competitions submit kaggriculture -f submissions\v12_v51safe\submission.tar.gz -m "v12: public v51 lean-flock (ahmedberatozer, Apache-2.0) + safety wrapper; 27 bots 246-24 (v10 207-63)"
```

## 提出結果

- submission ID：**56398792**
- 提出時刻：2026-09-20 15:06:29 UTC（2026-09-21 00:06 JST）
- 状態：`SubmissionStatus.COMPLETE`、初期 publicScore 600.0
- Validation Episode：111264840、COMPLETED（15:10:19 UTC）
- 提出直後の有効枠：v10（56392177）とv12（56398792）。古い56384238は14:53 UTC開始の公開対戦を最後に停止。
- チームの当日提出：4本、残り1本。次に新しく出すと、現時点では古いv10が外れる。
