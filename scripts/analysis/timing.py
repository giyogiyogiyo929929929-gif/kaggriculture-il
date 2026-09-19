# -*- coding: utf-8 -*-
"""1プロセスで自分の版の1ターンの推論時間を測る（コピー相手など特定の相手と当たったときの重さの確認）。

仕様: docs/05_evaluation.md §8（分析ツール）、doc 01 NFR（最悪 200ms 未満、p99 50ms 未満）
使い方:
    .venv\\Scripts\\python.exe scripts\\analysis\\timing.py <自分 main.py> <相手 main.py> [seed...]
seed の既定は 71 75。測定は他の重い処理を止めて行う（並列だと伸びる）。
"""
import sys
import time

import _common as C

mine, opp = C.load(sys.argv[1]), sys.argv[2]
seeds = [int(x) for x in sys.argv[3:]] or [71, 75]
ts = []
inner = C.wrap(mine)


def timed(o, c=None):
    t = time.perf_counter()
    a = inner(o, c)
    ts.append(time.perf_counter() - t)
    return a


for seed in seeds:
    C.play(timed, opp, seed)
ts.sort()
print(f"n={len(ts)} 中央値 {ts[len(ts) // 2] * 1000:.2f}ms p99 {ts[int(len(ts) * 0.99)] * 1000:.2f}ms 最悪 {ts[-1] * 1000:.2f}ms")
