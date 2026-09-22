# v14_queueclosure

- 状態: Rejected（未提出、安全性は維持したが効果が標準誤差未満）
- 土台: `submissions/v12_v51safe/main.py`（先頭バイト完全一致）
- 追加機構: final effective-queue closure
- 機構の出典: `lynnsakurai/farmer-john-and-the-idle-seller`（Apache-2.0）
- 仕様: `docs/adr/0005-selective-public-base-adoption.md`
- ビルド: `scripts/build_v14_queueclosure.py`

- `main.py`: 466,027 bytes
- SHA-256: `706260c19b1f4602cf1a0cc50c80851081129fd81a5e9dfa863066ef1496d501`
- v12 prefix: 462,563 bytes、SHA-256 `fd3231bd638414cbcdd9246be88f544f5367e365388e5debb24fee18834ab652`
- focused tests: 37件合格
- preflight: 全項目合格（中央値0.70ms、p99 4.38ms、最悪22.50ms、status DONE）
- smoke対戦結果: v12直接比較（seed 501〜510・両席）で3勝0敗7分、組平均差+0.9±0.53、例外0。差が出た3組は+5、+2、+2で、健康指標の悪化なし
- 回帰パネル: 10相手すべて完了。例外0・家畜逃走0・必須回帰の勝敗悪化なし。ただし同seed基準からの改善は0〜12円で標準誤差を大幅に下回るため不採用
- 詳細: `docs/experiments/EXP-20260921-36-v14-queueclosure-panel.md`
