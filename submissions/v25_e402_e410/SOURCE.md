# v25_e402_e410

- ベース: `submissions/v22_antiv52_brunchguard/main.py`
- 追加元: Ahmed Berat Ozer,
  `https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v56-smarter-seeds-and-fertilizer`
  （Apache-2.0）。
- 選択移植: E402（終盤の余剰WHEAT/CARROT種購入抑制）とE410
  （収穫量を増やさないWHEAT/CARROT肥料投入抑制）のみ。
- V56全体はJAXAへ0-5だったため不採用。小型ゲートではv25がv22へ10-0、v24へ9-0-1。
- 18相手同一seed回帰: 全相手で勝数悪化なし、平均差改善、合計64-26→73-17、
  例外0、家畜逃走0。
- 最終preflight: 全項目合格、中央値0.91ms、p99 5.20ms、最悪40.19ms。
- `main.py`: 1,019,371 bytes、SHA-256
  `29985a04826fe772f03600eec19f817d4c136a7625cf0f39c1e2506580fe8cab`
- `submission.tar.gz`: 618,693 bytes、SHA-256
  `51d732c7b58974666dad7b905c4b86a3b028ba7f0e14bebd1f89a9597d686895`
- Kaggle未提出。
