# 出典：peak_2950

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20（UTC）
関連: doc 07 §5, EXP-20260920-18

| 項目 | 内容 |
|---|---|
| ノートブック | `haideptry/the-2950-peak-farm` |
| 取り出し方 | `%%writefile main.py` のセル本文。**セルは実行していない**（`scripts\analysis\extract_notebook_agents.py`） |
| SHA-256 | `00dbf93ea29dd6c597a68f019af73a708b49cbec0fd9ff28098c61fe7cddf2a8` |
| サイズ | 862,941 bytes |
| 系統 | **v9/4 ＋ 別の序盤（`_ALT_MODE='EarlyCycle'`）**。作者の記載は Dmitrii Gluzdov（A Smaller Market Shock と同じ）。先頭 856,428 バイトが v9/4 原本と同一で、後ろに 6,513 バイトの層を足している |
| 安全確認 | `scripts\analysis\audit_agent.py` で、埋め込みソースまで再帰的に危ない import・呼び出しを探した。注意は開発用の `open(path)`（環境変数 `V92_SELL_LIB` があるときだけ読む v9/4 由来の処理）の1件のみ |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\peak_2950\main.py` を渡す（最後の callable が agent）。
