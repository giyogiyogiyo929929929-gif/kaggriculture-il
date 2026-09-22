# v26_r148_overflow

- ベース: `submissions/v25_e402_e410/main.py`
- 追加元: Ahmed Berat OzerのV43 R148をPipe19経由で分離移植。
  `https://www.kaggle.com/code/nathanjacob/kaggriculture-pipe19-sale-advance-overflow`
  （Apache-2.0）。
- 選択移植: 夜明けの倉庫超過で失われる貨物と同量・同品目だけを事前売却し、
  夜明け後の在庫ベクトルが追加前と完全一致する場合だけ採用するR148層。
- ADV、Pipe19本体、そのほかの層は移植していない。
- `main.py`: 1,023,149 bytes、SHA-256
  `5584b6dd49ae7cc90a7bc6270e3836630349a6d12efc4643f39ef037a9ab2193`
- focused test 8件・preflight全項目合格（中央値0.82ms、p99 4.88ms、最悪34.40ms）。
- JAXA・Order Book・Pipe19・v49・More Wheatの同一seed代表パネルでは、
  v25と勝敗・平均差が全相手で完全一致。候補側50試合で発火0回・回収0個。
- 実効性がないため不採用。再検証用に保持し、Kaggle未提出。
