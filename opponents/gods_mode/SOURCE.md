# 出典：gods_mode（God's Mode: Hacked Stores）

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-18, `opponents\farming_v2_b\SOURCE.md`（同じ base_agent）

| 項目 | 内容 |
|---|---|
| ノートブック | `leoprovorov/god-s-mode-hacked-stores`（AlekseiProvorov） |
| 取り出し方 | セル45 の `PAYLOAD_B85` を ast で読み、**b85 → lzma → 独自の連結形式**（[ファイル数][名前長][名前][サイズ8][中身]…）を復元。**セルは実行していない** |
| 照合 | ノートブック内の `EXPECTED_SHA256` と**6ファイルすべて一致** |
| 構成 | `main.py` 358 bytes / `base_agent.py` 860,103 / `shop_predictor.py` 11,585 / `shop_overlay.py` 13,773（HTML の資料2本は取り込んでいない） |
| SHA-256 | main.py `f9588c469d2c1829e46593faeab7efe088a70f6c77d04a78800217350c812ae5`、base_agent.py `177d78bdf00aa96579d98052558e18cd3081d29f855c8a6f20a2bbfebcdbda11`、shop_predictor.py `900b30017b3c97b0…`、shop_overlay.py `f4a5d2ecae74a008…` |
| 系統 | **`farming_v2_b`（＝ Master Engine V4、v9/4 系）と同じ base_agent に、店（town shop）の抽選を狙う層をかぶせたもの** |
| 安全確認 | `scripts\analysis\audit_agent.py` で main.py・shop_predictor.py・shop_overlay.py はいずれも注意0件（base_agent.py は `farming_v2_b` と同一で、v9/4 由来の `open(path)` が1件） |

## 中身（ノートブックの主張）

- 店の抽選は、その日の終わりに `Random((seed*1,000,003) XOR day)` で決まり、**空きマスの数で乱数の消費位置が変わる**。
  つまり `DIG` などで空きマスを1つ増やすと、次に開く店が変わりうる（128回の対照実験で 76.6%）。
- ただし seed は見えないので、**雑草の出方（1マスあたり 0.005）を観測して seed を絞る**（active sensing）。
  実際に狙った店を出せるのは試合の 10〜18% と書かれている。
- 著者自身の結論：**店を操れても勝てるとは限らない**（PET_CAFE を狙った版は、元の版より margin が下がった）。

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\gods_mode\main.py` を渡す
（`main.py` は同じフォルダの `base_agent` と `shop_overlay` を import する。Kaggle と同じくフォルダが `sys.path` に入る）。
