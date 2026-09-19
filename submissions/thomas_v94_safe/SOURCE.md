# 出典：thomas_v94_safe（v9/4 ＋ 例外時フォールバックの包み）

状態: 提出候補 v4
作成日: 2026-09-19
関連: ADR-0003, EXP-20260919-11, `submissions\thomas_v94\SOURCE.md`（原本の出典）

| 項目 | 内容 |
|---|---|
| 元 | `submissions\thomas_v94\main.py`（thomastschinkel「The 2945 Farm」v9/4、Apache-2.0） |
| 改変 | **末尾に包みを追加しただけ**。先頭 856,428 バイトは原本と同一（SHA-256 `bfee70e9…`） |
| SHA-256（全体） | `a955ecec3af98b36b36e89863e577d28f7d2622fa03f772b24cf8fdcf5df611e` |
| エントリ | `_kil_safe_agent(observation, configuration=None)`（最後の callable。`--entry _kil_safe_agent`） |
| 包みの中身 | 原本の最後の callable（`agent`）を呼び、例外が出たら `{"farmer": ["PASS"], "hands": [], "market": []}` を返す |

- 理由：原本は空の観測 `{}` で `KeyError('player')` を出す（実際の試合では出ていない）。万一の例外で反則負けにしない（NFR-2）。
- **実際の試合での行動は原本と1手も変わらない**ことを確認（v16rc5 相手に3シード×両席の6試合、行動列と所持金が完全一致）。
- preflight（720ターン）：全項目 OK。1ターン 中央値 0.55ms / 99%点 5.13ms / 最悪 43.57ms。
