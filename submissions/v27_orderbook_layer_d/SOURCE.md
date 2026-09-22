# v27_orderbook_layer_d

- ベース: `submissions/v25_e402_e410/main.py`
- 追加元: shiiin9,
  `https://www.kaggle.com/code/shiiin9/your-market-list-is-an-order-book`
  （Apache-2.0）。
- 選択移植: SELLと固定価格注文の元スロットだけを探索し、v25既存の市場シミュレータで
  元順より0.5円超改善する並びだけを採用するLayer D。1ターン最大800候補。
- `main.py`: 1,022,601 bytes、SHA-256
  `21f2d4a6f6aa72d18015961058edf9172dd4632320ce535f2ba01e034dc9a271`
- focused test 7件。最終preflight全項目合格（中央値1.17ms、p99 6.98ms、最悪42.01ms）。
- 初期5相手50試合: 並べ替え570ターン、5相手すべてで平均差+38〜+178円、
  Pipe19は3-2から4-1、例外0、家畜損失の増加0。
- 18相手同一seed広域回帰: 全相手で平均差改善（平均+202円）、合計73-17→81-9、
  勝数悪化相手0、例外0、家畜損失はv25/v27とも合計10、最大172.9ms。
- 並べ替え2,086ターン、探索979,802候補、推定利得合計62,740円。
- `submission.tar.gz`: 619,554 bytes、SHA-256
  `4b9c7ded1ad475a01181ed4061da266047364100448306fc3188c55dfae3ad6f`。
- v27として採用。2026-09-22 08:22 UTCにユーザーがsubmission `56458614`として提出。
  状態COMPLETE、初期Public Score 600.0。
