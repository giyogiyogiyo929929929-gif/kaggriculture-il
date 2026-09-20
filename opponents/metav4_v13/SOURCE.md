# 出典：metav4_v13（The Metav4 Farm: Submission v13）

状態: 評価用の対戦相手（提出物には入れない）
取得日: 2026-09-20
関連: doc 07 §5, EXP-20260920-23, `submissions\thomas_v94\SOURCE.md`（同じ作者の v9/4＝こちらの土台）

| 項目 | 内容 |
|---|---|
| ノートブック | `thomastschinkel/the-metav4-farm-submission-v13`（The Metav4 Farm: Submission v13） |
| 作者 | Thomas Tschinkel（**v9/4「The 2945 Farm」と同じ作者。v9/4 はこちらの v4〜v8 の土台**） |
| 票数（取得時） | 11 |
| 最終実行（取得時） | 2026-09-20 06:58:38 UTC |
| 取得コマンド | `.venv\Scripts\kaggle.exe kernels pull thomastschinkel/the-metav4-farm-submission-v13 -p <スクラッチ>` |
| 取り出し方 | `scripts\analysis\extract_notebook_agents.py` で ast からリテラルを読んで復元。**セルは実行していない**（AGENTS.md §5） |
| SHA-256 | `9d63494603f88219857a3101d7dc19cc750ded04e5886732ee428580326967d9` |
| サイズ | 1,004,288 bytes（6,466 行） |
| エントリ | `agent(observation, configuration=None)`（最後の def。末尾に `agent.telemetry = _V13V_REPORT` と `agent = globals().pop("agent")`） |
| 系統 | 先頭の注記は「v9/3 ＝ 公開 V39 ＋ v9 層」。**v9/4（`submissions\thomas_v94\main.py`）とは先頭 304,518 バイトまで同一**で、そこから別物。末尾に `_e334` / `_e335` / `_V13V`（トマトの要求を止める層）などが積んである |
| ライセンス | Apache-2.0 の派生（thomastschinkel・yhay81・destbreso・aurax7・tetsutani・prvsiyan・Dmitrii Gluzdov らの表示と Apache License 全文を保持） |
| 安全確認 | `scripts\analysis\audit_agent.py` で再帰的に検査 → **注意1件のみ**：`open(path)`（3590 行。環境変数 `V92_SELL_LIB` があるときだけ読む開発用の処理で、v9/4 系に共通の正常パターン）。危ない import・呼び出しは無し |
| 手元の成績 | **v7 が 5勝15敗（ペア単位）／9勝31敗（試合単位）、ペア差 −974 ± 288**。例外0件。EXP-20260920-23 |

**注意：手元の公開エージェントの中で、v7 がはっきり負け越す初めての相手**（それまで58本に通算 1,126勝74敗）。
しかも **20 seed のうち16 seed で v7 のコピー判定が発火している**のに負ける＝候補A・A2・A3 の先回りが効いていない。
くわしくは EXP-20260920-23。

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\metav4_v13\main.py` を渡す（最後の callable が agent）。

```cmd
.venv\Scripts\python.exe scripts\eval.py submissions\v7_relax\main.py opponents\metav4_v13\main.py -n 20 -j 4 --json data\eval\v7\vs_metav4_v13.json
```
