# 出典：v15_v52safe（v52 ＋ 例外時フォールバック）

状態: 提出候補完成・全検証合格（未提出）
作成日: 2026-09-21
関連: ADR-0006, EXP-20260921-37, doc 06

| 項目 | 内容 |
|---|---|
| 元 | `opponents\v52\main.py`（Ahmed Berat Özer「Kaggriculture V52 — Lean Flock, Yarn Route」、Apache-2.0） |
| 作り方 | `scripts\build_v15_v52safe.py` |
| 改変 | v52原本の末尾に、例外時だけPASSを返す安全ラッパーを追加。戦略本体は変更しない |
| 原本SHA-256 | `8c0f7d90db965a676bd0e211e0250aa9b9235d64d43ff0b4e3852a71d1ef7c24` |
| main.py | 1,008,125 bytes、SHA-256 `3608fc1590444b6a523afa9e28fc70e4ca00b9a2e4280c5f8452287f471eb5b9` |
| submission.tar.gz | 615,684 bytes、SHA-256 `30149f1f710d49a9fc8e2a62c42a0af8afb8a8959508d06cf180e552a5f24920` |
| エントリ | `_kil_v52_safe_agent(observation, configuration=None)` |
| 提出状況 | 未提出。Kaggleへの提出はユーザーだけが行う |

## 検証結果

- v52原本1,007,349 bytesは完全一致。原本SHA-256もSOURCE記録と一致。
- `tests/test_v15_v52safe.py`と`tests/test_preflight.py`の29件合格。
- preflight全項目合格。中央値0.84ms、p99 4.90ms、最悪29.43ms、720ターンDONE。
- 外部ライブラリなし、壊れた観測5パターン合格、最後のcallableは`_kil_v52_safe_agent`。
- tarの中身はルートの`main.py`だけで、展開した1,008,125 bytesがローカル候補と完全一致。
- 戦略評価は`EXP-20260921-37`。v12に10勝0敗、21相手の回帰と追加確認を通過。

再検証コマンド：

```cmd
.venv\Scripts\python.exe scripts\preflight.py --main submissions\v15_v52safe\main.py --entry _kil_v52_safe_agent --build --output submissions\v15_v52safe\submission.tar.gz
```
