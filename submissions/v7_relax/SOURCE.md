# 出典：v7_relax（v6 のコピー判定を候補A3 の判定に変えた版）

状態: 提出候補 v7（doc 07 §3 候補A3 の受け入れ条件をすべて満たした）
作成日: 2026-09-20
関連: doc 07 §3 候補A・A2・A3, EXP-20260919-17, `submissions\v6_preempt\SOURCE.md`, `submissions\thomas_v94\SOURCE.md`（原本の出典）

| 項目 | 内容 |
|---|---|
| 元 | `submissions\thomas_v94\main.py`（thomastschinkel「The 2945 Farm」v9/4、Apache-2.0） |
| 作り方 | `.venv\Scripts\python.exe scripts\build_v7_relax.py`（v6_preempt のコピー判定の部分だけを書き換える） |
| 改変 | 先頭 856,428 バイトは原本と同一（SHA-256 `bfee70e9…`、`tests\test_v7_relax.py` で確認） |
| SHA-256（main.py） | `07be7beab2c399d6990956e7ca89d2c773fc903cf688f717e44c466c8bb4ad39`（864,304 bytes） |
| SHA-256（submission.tar.gz） | `7f8a928001459a0fd4494f654350367acd1f5bdf5629c6bc000cfbfb13a75225`（527,238 bytes、中身は main.py のみ） |
| エントリ | `_kil_safe_agent(observation, configuration=None)`（最後の callable） |

## v6 からの違い（候補A3）

- コピー判定：「0〜167 ステップで、雑草を除いた農場（所持金を含む）が完全一致」→
  「**96〜167 ステップで、雑草と所持金を除いた農場が一致し、かつ所持金の差が一定**」。
- 「v9/4 ＋ 序盤の小さな上乗せ」（公開ノートブック A Smaller Market Shock など）もコピーとして扱い、候補A・A2 の動きで勝つ。
- それ以外の相手では v6 と同じ動き（手元の公開エージェント19本との380試合で、所持金が v6 と1試合残らず完全一致）。

## 提出コマンド（ユーザーが実行）

```cmd
.venv\Scripts\kaggle.exe competitions submit kaggriculture -f submissions\v7_relax\submission.tar.gz -m "v7: v6 + relaxed copy detection (beats copy+opening-bonus; vs SMS 40-0)"
```
