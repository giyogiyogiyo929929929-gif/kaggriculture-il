# -*- coding: utf-8 -*-
"""コピー判定の確認：自分の版と相手の試合で、農場がいつ・どこで食い違うか、96〜167 ステップの一致と所持金差を出す。

仕様: docs/05_evaluation.md §8（分析ツール）、doc 07 候補A・A3（コピー判定）
使い方:
    .venv\\Scripts\\python.exe scripts\\analysis\\copy_check.py window <自分 main.py> <seed数> <相手 main.py>...
        → 各 seed で「96〜167 で雑草と所持金を除いた農場が一致したか / 所持金差の最大 / 差が一定か」（v7 の判定と同じ条件）
    .venv\\Scripts\\python.exe scripts\\analysis\\copy_check.py diff <自分 main.py> <相手 main.py> <seed>
        → 1試合で、農場の違い（雑草は無視）が変わったステップを順に表示
"""
import sys
from pathlib import Path

import _common as C

mode = sys.argv[1]
if mode == "window":
    mine, seeds = sys.argv[2], int(sys.argv[3])
    for opp in sys.argv[4:]:
        out = []
        for seed in range(1, seeds + 1):
            env = C.play(mine, opp, seed, steps=170)
            same, gap, deltas = True, 0.0, set()
            for t in range(96, min(168, len(env.steps))):
                f = env.steps[t][0]["observation"]["farms"]
                if C.copy_key(f[0], ignore_money=True) != C.copy_key(f[1], ignore_money=True):
                    same = False
                gap = max(gap, abs(f[0]["money"] - f[1]["money"]))
                deltas.add(f[0]["money"] - f[1]["money"])
            out.append(f"{'一致' if same else '不一致'}/{gap:.0f}/{'一定' if len(deltas) == 1 else str(len(deltas)) + '種'}")
        print(f"{Path(opp).parent.name:22s} seed1..{seeds}: {' '.join(out)}", flush=True)
elif mode == "diff":
    env = C.play(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    last = None
    for t, s in enumerate(env.steps):
        f0, f1 = s[0]["observation"]["farms"]
        diff = []
        for k in f0:
            if k == "tiles":
                a, b = C.strip_weeds(f0), C.strip_weeds(f1)
                cells = [(x, y) for y, (r0, r1) in enumerate(zip(a, b)) for x, (c0, c1) in enumerate(zip(r0, r1)) if c0 != c1]
                if cells:
                    diff.append(f"tiles{cells}")
            elif f0[k] != f1[k]:
                diff.append(f"money{f0[k] - f1[k]:+.0f}" if k == "money" else k)
        sig = " ".join(diff)
        if sig != last and (t < 400 or t % 24 == 0):
            print(f"step {t:3d}: {sig or '一致'}")
            last = sig
    print("final", C.rewards(env))
else:
    sys.exit("mode は window か diff")
