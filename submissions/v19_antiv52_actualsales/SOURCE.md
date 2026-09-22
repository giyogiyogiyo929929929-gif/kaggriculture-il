# v19_antiv52_actualsales

- ベース: `submissions/v17_antiv52_strict/main.py`
- 変更: 先回り後の実販売量を市場在庫の差分計算に使い、比較対象には元のv52販売量を使う。
- 追加安全策: 確定後に相手の販売が元のv52と不一致になった場合は、その試合では先回りを永久停止する。
- Kaggle未提出。
