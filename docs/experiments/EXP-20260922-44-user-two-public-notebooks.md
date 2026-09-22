# EXP-20260922-44: ユーザー指定の最新公開2本

状態: Complete / 全面ベース不採用
最終更新: 2026-09-22
関連: EXP-20260922-39、EXP-20260922-42、ADR-0007

## 対象

1. `dmitriigluzdov/kaggriculture-more-wheat-smarter-sales`
2. `ahmedberatozer/kaggriculture-v56-smarter-seeds-and-fertilizer`

2026-09-22にKaggle公式APIから最新版を取得。ノートブックセルは実行せず、リテラルの
`main.py`だけを抽出した。埋込SHA照合は両方一致。

## 初期確認

- More Wheat最新版: 2026-09-21 17:29 UTC更新、1,023,447 bytes、SHA-256
  `853d6df99682faa8f4e9be059956df96612f78cae5f0fae34018873880b0e270`。既存旧版
  `opponents/dz_more_wheat`（870,455 bytes）とは別物。一時WHEAT成熟層と、非継続作物の
  収穫遅れによる減衰をPASSターンで救済するC02層を含む。
- V56: 2026-09-21 15:28 UTC更新、1,056,142 bytes、SHA-256
  `a1ad0fd1d174477ee2cbdd561a812bcb7029647ce34599e79d6b79e9057eff6c`。取得時のKaggle
  `scoreDescending`一覧で2位。v54へ終盤の余剰WHEAT/CARROT種購入削減と、収穫量を
  増やさないWHEAT/CARROT肥料投入の抑制を追加している。
- 両方ともApache-2.0表記あり。静的監査は各1警告のみで、`path=None`直後の到達不能な
  `open(path)`。ネットワーク・サブプロセス利用はない。
- More Wheatは更新直後のためか、取得時の上位100一覧には現れず現在順位を確定できない。

## 評価方法

- v22と各5ペア・両席、seed 801からスモークする。
- 勝数が敗数以下、または平均差の絶対値が標準誤差の2倍以下ならseed 851から10ペア追加する。
- 例外・家畜逃走・勝敗・平均差を保存し、monitor JSONで完了を監視する。
- Kaggleへの追加提出は行わない。

## 結果

v22とのseed 851〜860追加確認は両方ともv22側3勝7敗、例外0、家畜逃走0。

- More Wheat最新版: v22から見て-192.4±175.0円。
- V56: v22から見て-401.0±201.8円。

V56は同じ10 seedのうち8 seedでMore Wheatよりv22との差を大きくし、平均では約209円強い。
ただし両者ともv54/Pipe16近縁で、v54は異系統パネルのJAXAへ0-5・約-16,000円だった。
直接戦だけでベース採用せず、JAXA、v49、story_of_seasonsの3系統へ各5ペアを追加し、
最後に2本同士を10ペアで比較する。

## 異系統安全性パネル

全7セットが完了。例外は全試合0だった。

| 候補 | 相手 | 勝敗 | 平均差±標準誤差 | 家畜逃走 |
|---|---|---:|---:|---:|
| More Wheat | JAXA | 0-5 | -11,198.2±1,098.4円 | 1 |
| More Wheat | v49 | 2-3 | -465.2±521.8円 | 0 |
| More Wheat | story_of_seasons | 5-0 | +77.8±0.5円 | 0 |
| V56 | JAXA | 0-5 | -15,912.6±2,680.0円 | 1 |
| V56 | v49 | 2-3 | -243.8±481.4円 | 0 |
| V56 | story_of_seasons | 5-0 | +567.4±200.5円 | 0 |
| V56 | More Wheat | 10-0 | +252.1±57.7円 | 0 |

## 判断

- 2本だけならV56が明確に強く、More Wheatへ10-0だった。
- ただし両方ともJAXAへ0-5で、家畜逃走も再現した。V56の約-15,913円は、全面ベースを
  不採用にしたv54の約-16,117円と同水準である。
- v49にも両方2-3であり、公開上位・近縁相手への強さだけで全面ベースにすると、v54と同じ
  局所適合を繰り返す。
- よって全面ベースは両方不採用、v22を維持する。次はV56の差分のうち独立性が高い
  E402（終盤の余剰種購入抑制）とE410（収穫量を増やさない肥料投入抑制）だけを分離し、
  v22へ一層ずつ移植して小さいゲートで評価する。

成果物: `data/eval/v22_user_two_latest.monitor.json`、
`data/eval/two_latest_safety.monitor.json`、`data/eval/two_latest_safety/summary.json`
