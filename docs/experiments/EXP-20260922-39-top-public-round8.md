# EXP-20260922-39: Public Score上位10本とのv22対戦

状態: Implemented
最終更新: 2026-09-22
関連: docs/05_evaluation.md、EXP-20260921-38、ADR-0007

## 目的

2026-09-22にKaggle APIを`scoreDescending`で取得した公開ノート上位10本と、現行候補
`submissions/v22_antiv52_brunchguard/main.py`を同一条件で対戦させる。Kaggleへの提出は行わない。

API応答には数値スコアが含まれないため、ここでいう順位はAPIが返した降順であり、数値スコア順位の再現ではない。

## 対象（API順）

1. `dmitriigluzdov/kaggriculture-a-smaller-market-shock`
2. `ahmedberatozer/kaggriculture-v47-reactive-market-coordination`
3. `lynnsakurai/farmer-john-and-the-idle-seller`
4. `ahmedberatozer/kaggriculture-v54-productive-wheat-and-patient`
5. `guruprasaathas111/kaggriculture-master-engine-v3`
6. `lynnsakurai/farmer-john-and-the-wheat-seller`
7. `anhadmahajan06/kaggriculture-autonomous-ai-farming-agent`
8. `hanifnoerrofiq/a-wonderful-life`
9. `nathanjacob/kaggriculture-pipe16-idle-workers`
10. `dmitriigluzdov/kaggriculture-more-wheat-smarter-sales`

## 方法と受け入れ条件

- 全10本をseed 601から5ペア（両席、各10試合）、並列数4でスモーク評価する。
- 勝数が敗数以下、または平均差の絶対値が標準誤差の2倍以下なら、seed 701から10ペアを追加確認する。
- 例外数、家畜逃走数、勝敗、平均差、標準誤差をJSONへ保存する。
- バックグラウンド実行中はmonitor JSONを各相手の終了時に更新し、全終了時に`complete`、異常時に`failed`を記録する。
- 新規4本はノートブックのセルを実行せず、AST/リテラル抽出だけで取得した。静的監査の警告は到達不能な`open(path)` 1件のみ（直前で`path = None`固定）。ネットワーク・サブプロセス利用はない。

## 結果

全10本が完走し、例外0、v22の家畜逃走0。結果は
`data/eval/v22_top_public_round8/summary.json`へ保存した。

- 明確な勝ち越し: `v47` 5-0（+6,168円）、`smaller_market_shock` 8-2
  （+1,107円）、`master_v3` 8-2（+1,163円）、`wonderful_life` 8-2
  （+1,107円）、`dz_more_wheat` 8-2（+1,082円）。
- 僅差の勝ち越し: `farmer_john_idle` 6-4（+117円）、`farmer_john_wheat` 6-4
  （+89円）、`autonomous_ai` 6-4（+89円）、`pipe16` 6-4（+117円）。いずれも
  平均差は標準誤差より小さく、優位とは断定しない。
- 引き分け: `v54` 5-5（+62円）。平均差は標準誤差より小さい。
- スモークでは近縁系が1-4だったが、独立seedの追加確認では6-4または5-5へ戻った。
  5ペアだけの判定が不安定だったため、自動追加確認は必要だった。

監視ランナーは全処理後に`SystemExit(0)`を`BaseException`で捕捉し、結果が完成しているのに
monitorだけ`failed`と記録する不具合があった。捕捉対象を`Exception`へ狭め、完成済みmonitorを
`complete`へ訂正した。対戦結果には影響しない。

## 接戦群の初期分析

追加確認seed 701〜710のペア差を照合すると、`farmer_john_idle`と`pipe16`は10 seedすべて
完全一致し、`farmer_john_wheat`と`autonomous_ai`も完全一致した。`v54`も同じ増減形状で、
各seedの差はこの2群からおおむね数十円だけずれる。したがって別々の5課題ではなく、同じ
強い近縁系統に対する1課題として扱う。

共通して大きく負けるのはseed 707（約-2,000円）、勝つのはseed 709〜710
（約+1,200〜+2,100円）。v54だけseed 704が-7円になり、ほかの近縁版の小幅勝ちを
反転させたため5-5になった。次はseed 707の敗因とseed 710の勝因を同じ台帳条件で比較する。

台帳比較では生産・販売個数はほぼ同じで、差は主に売値だった。seed 707のv22はv54に対し
MILK売上-1,031円、WOOL売上-425円で計-2,021円。seed 710はWOOL売上+1,893円、
STRAWBERRY売上+742円が主因で計+2,047円だった。生産配分の全面変更より、day 17以降の
MILK/WOOL/STRAWBERRY売却タイミングを対象にするのが妥当。

元のv52を同じseed 707・710でv54と対戦させると、最終差はそれぞれ-2,021円、+2,047円で
v22と完全一致した。したがって、この近縁群ではv22の対旧v52先回り層は発火しておらず、
勝敗を悪化させても改善してもいない。次の改善対象は先回り層ではなく、v54が追加した
一時WHEAT周期と低価格時の初回売却待機の独立評価になる。
