# ADR-0005: Pipe16 系の全面採用を避け、売却キュー改善だけを選択移植する

状態: Accepted
日付: 2026-09-21
関連: `docs/adr/0004-switch-base-to-v51.md`, `docs/experiments/EXP-20260921-35-user-referenced-public-bases.md`, `docs/05_evaluation.md`

## 背景

Kaggle の公開 Notebook を Public Score 降順で確認したところ、
`nathanjacob/kaggriculture-pipe16-idle-workers` が上位にあり、公開 Notebook 内では
Metav4 v13 など7相手に318勝32敗と報告されている。

一方、手元の同一 seed 評価（EXP-20260921-35）では、Pipe16 系は v12 に対して
7勝3敗、平均差 +363 円だったものの、JAXA 2802 に0勝10敗、平均差 -14,319 円となった。
v51/v12 は同じ相手に10勝0敗、平均差 +2,782 円であり、全面的な土台変更には
致命的な退行がある。farming_v2、v49、v50、tetsutani_dpts_b にも退行がある。

`lynnsakurai/farmer-john-and-the-idle-seller` は Pipe16 系に次の2変更を加える。

1. 仮設小麦の失敗時だけ step 29 の WATER を BUILD_PASTURE に戻す。
2. 同一ターンの市場キューで、実効数量0の売却スロットを穴として扱い、後続の
   実行可能な現金商品の売却を安定的に前詰めする。

1はPipe16固有の序盤ルートに依存する。2はv12で観測した終盤の売却順競争に
独立して適用できる可能性がある。

## 決定案

- Pipe16、Haodou V54、One More Wheat のいずれにも全面移行しない。
- 現行の v12/v51 系を土台として維持する。
- Farmer John の failure-atomic opening は移植しない。
- final effective-queue closure だけを、v12 の返却 action を後処理する独立層として
  新候補へ追加する。
- v12 原本部分は1バイトも変更せず、ビルドスクリプトで末尾に層を追加する。
- 買い、雇用、土地、種、動物、肥料、WHEAT の注文位置は変更しない。
- 対象は CARROT、TOMATO、STRAWBERRY、MELON、EGG、MILK、WOOL の SELL のみとする。
- 注文リスト長、商品別の実効売却数量、実行可能な固定価格注文の位置を保存する。
- 例外時は元の v12 action をそのまま返す。

## 実装前の受け入れ条件

1. テストで、v12 の先頭バイト完全一致と最後の callable を確認する。
2. 人工キューで、実効数量0の売却だけが穴になり、後続の実行可能 SELL が安定的に
   前詰めされることを確認する。
3. 商品別の実効売却数量、注文リスト長、対象外注文の位置が保存されることを確認する。
4. 壊れた観測・不足した private inventory・非標準 action では例外を出さず、元 action に戻る。
5. preflight の時間、完走、依存、最後の callable の全項目を通す。

## 評価ゲート

- まず少数 seed で層の発火回数と売却位置の変化を確認する。
- CPU を使う評価は AGENTS.md に従い、非表示のバックグラウンドプロセスを1本だけ起動する。
- 必須回帰相手: `jaxa_2802`, `farming_v2`, `v49`, `v50`, `tetsutani_dpts_b`。
- 強み確認相手: `metav4_v13`, `v52`, `story_of_seasons`, `pipe16`, `dz_one_more_wheat`。
- 例外0、家畜逃走0を必須とする。
- 必須回帰相手の勝敗を1本でも悪化させた候補は不採用とする。
- 改善が標準誤差内、または層がほぼ発火しない場合も不採用とする。
- 合格しても提出は別判断とし、現在の有効2枠と当日の提出上限を再確認する。

## 検討した他の案

### Pipe16 をそのまま新しい土台にする

現在の公開順位とNotebook内評価は強いが、手元のJAXA評価で致命的に退行するため不採用。

### One More Wheat を土台にする

Pipe16より仮設小麦が1個多いが、共通するJAXA退行を解消しない。Notebook内の固定試合確認も
Pipe16の横断評価より弱いため不採用。

### Farmer John を丸ごと採用する

売却キュー改善は有望だが、土台はPipe16系であり、同じ構造的退行を引き継ぐため不採用。

## 結果・トレードオフ

Public Score上位の完成品をそのまま利用する速さは失う。一方、v51系が持つJAXAなどへの強さを
維持しながら、v12の終盤売却競争に対応する変更だけを独立に検証できる。

2026-09-21、ユーザー承認。
