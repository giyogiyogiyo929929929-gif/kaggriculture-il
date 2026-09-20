# -*- coding: utf-8 -*-
r"""1試合で所持金の差がどこで開くかを追う（日ごと・ステップごと）。

負けの原因を「生産量の差」「売り方の差」に分けるための道具。
**注文の数量は約定量と違う**（在庫でクリップされる）ので、**所持金の増分**で測る。

仕様: docs/05_evaluation.md §8（分析ツール）
使い方:
    .venv\Scripts\python.exe scripts\analysis\money_trace.py <自分 main.py> <相手 main.py> <seed>...
    → 日ごとの差の動き、1ステップの変化が大きいところ、その時刻に両者が出した SELL と価格
"""
import sys
from pathlib import Path

import _common as C

sys.stdout.reconfigure(encoding="utf-8")


def trace(mine, opponent, seed, top=8):
    env = C.play(mine, opponent, seed)
    steps = env.steps
    money = [[s[0]["observation"]["farms"][p]["money"] for s in steps] for p in (0, 1)]
    n = len(steps)
    diff = [money[0][t] - money[1][t] for t in range(n)]
    print(f"=== seed {seed}  最終差 {diff[-1]:+,.0f}（{Path(mine).parent.name} − {Path(opponent).parent.name}）")

    line = []
    for day in range(n // 24 + 1):
        t0, t1 = day * 24, min((day + 1) * 24, n - 1)
        if t0 >= n:
            break
        line.append(f"d{day:02d} {diff[t1] - diff[t0]:+7.0f}")
    print("  日ごとの差の動き:")
    for i in range(0, len(line), 6):
        print("   " + "  ".join(line[i:i + 6]))

    moves = sorted(range(1, n), key=lambda t: abs(diff[t] - diff[t - 1]), reverse=True)[:top]
    print("  1ステップの変化が大きい順:")
    for t in sorted(moves):
        obs = steps[t][0]["observation"]
        prices = obs["market"]["prices"]

        def sells(player):
            action = steps[t - 1][player].get("action") or {}
            return ",".join(f"{o[1]}x{o[2]}@{prices.get(o[1], 0)}"
                            for o in (action.get("market") or []) if o and o[0] == "SELL") or "-"

        print(f"   step {t:3d} (d{obs['day']:02d} h{obs['hour']:02d}) 差 {diff[t-1]:+8.0f} → {diff[t]:+8.0f} "
              f"({diff[t] - diff[t-1]:+7.0f})  自分: {sells(0)}  | 相手: {sells(1)}")

    first = next((t for t in range(n) if abs(diff[t]) > 0.5), None)
    if first is None:
        print("  差がついた最初のステップ: 最後まで差なし")
    else:
        day = steps[first][0]["observation"]["day"]
        print(f"  差がついた最初のステップ: {first}（d{day:02d}、差 {diff[first]:+,.0f}）")
    return diff


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    for s in sys.argv[3:]:
        trace(sys.argv[1], sys.argv[2], int(s))
        print()
