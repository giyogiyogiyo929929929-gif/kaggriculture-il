# 出典：k256_h2_q_v1（チームメイト k256net の提出 56384238）

状態: 評価用の比較相手（チームメイトの提出物。自分の提出物には入れない）
取得日: 2026-09-20（ユーザーがチームメイトから受け取り、`%USERPROFILE%\Downloads\main.py` として渡した）
関連: doc 06 §チーム, doc 08 §5, roadmap 3-11

| 項目 | 内容 |
|---|---|
| 提出 | **56384238**（2026-09-20 07:00:22 UTC、`main.py`、公開スコア **2588.3**） |
| 提出メッセージ | `k256 h2_q_v1: 2945 Farm + clone-aware front-run h2 + endgame sell Q policy (fitted Q from counterfactual rollouts, exp019). held-out vs 2945 0.79->0.94, vs h2 0.04->0.74, 14-bot pool 0.89->0.91` |
| 作者 | k256net（チームメイト。チーム「giyogoioが相手の農地を燃やします」、TeamId 16921670） |
| SHA-256 | `ef59770bfbe1ccc67b478809ea1f560bee8f57f99d4b842197c7340fca2d0afa` |
| サイズ | 1,603,586 bytes（5,967 行） |
| エントリ | `agent(observation, configuration=None)`（最後の callable、5959 行目。例外時は `PASS` に落ちる二重 try） |
| 系統 | 先頭の注記では「v9/3 ＝ 公開 V39（Apache-2.0）＋ v9 層（RACEPX / RACE / COURIER / CARROT / HERD）」。その後ろに k256net の層が3つ積んである |
| k256net の層 | ① `_K_TET_AGENT` 系（コピー検知つき front-run h2、`_K_CLONE_LAYOUTS` にステップ 24〜168 の農場配置の型を持つ）／② `_k_shifted_plan`・`_k_front_run`（ルートずらし）／③ `_K_Q_*`（終盤の売りを fitted Q で決める `QSellPolicy`・`SellHook`） |
| ライセンス | Apache-2.0 の派生（ファイル先頭に thomastschinkel・yhay81・destbreso・aurax7・tetsutani・prvsiyan・Dmitrii Gluzdov らの表示と Apache License 全文を保持） |
| 安全確認 | `scripts\analysis\audit_agent.py` で再帰的に検査 → **注意1件のみ**：`open(path)`（3590 行。環境変数 `V92_SELL_LIB` があるときだけ読む開発用の処理で、v9/4 系に共通の正常パターン）。危ない import・呼び出しは無し。**実行前に ast で監査した** |
| 動作確認 | `scripts\eval.py` で v7 と 4ペア8試合：2勝2敗、ペア差 +261 ± 812、例外 0 件、1ターン推論 中央値 1.2ms / 最悪 112.2ms |

**このファイルは改変しない。** 評価では `scripts\eval.py` に `opponents\k256_h2_q_v1\main.py` を渡す（最後の callable が agent）。

```cmd
.venv\Scripts\python.exe scripts\eval.py submissions\v7_relax\main.py opponents\k256_h2_q_v1\main.py -n 20 -j 4 --json data\eval\v7\vs_k256_h2_q_v1.json
```
