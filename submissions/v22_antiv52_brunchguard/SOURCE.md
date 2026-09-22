# v22_antiv52_brunchguard

- ベース: `submissions/v17_antiv52_strict/main.py`
- 変更: 最初の2店舗が`BRUNCH_SPOT / BRUNCH_SPOT`なら先回りを行わない。
- 根拠: seed 242では旧v52・v49・v50のいずれにも最初の先回りが不利だった。
- 21相手同seed回帰: 全相手で勝敗悪化なし、例外0、家畜逃走0。
- `main.py` SHA-256: `09d7d03ee56cd34822c56c33147af879ef3c9b5fae804b51c5396b9b054aedca`
- `submission.tar.gz`: 617,180 bytes、SHA-256 `c9b0a50f31dfa1af8f4dbdabc31a1b919fcda2d4a096ef5ae406d47910092cf5`
- Kaggle提出済み: submission `56439885`、2026-09-21 17:30:53 UTC
  （2026-09-22 02:30:53 JST）、説明
  `v22: v52 + mirror PREDICT pre-emption with BRUNCH guard`。
- Kaggle API確認時の状態は`COMPLETE`、初期Public Scoreは600.0。
