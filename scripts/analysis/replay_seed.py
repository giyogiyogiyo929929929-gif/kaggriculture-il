# -*- coding: utf-8 -*-
"""本番と同じ seed・席で、自分の版と手元の相手を対戦させ、最終所持金を出す（本番との照合や「別の版ならどうだったか」用）。

仕様: docs/05_evaluation.md §8（分析ツール）
使い方:
    .venv\\Scripts\\python.exe scripts\\analysis\\replay_seed.py <自分の main.py> <seed> <自分の席> <相手 main.py>...
"""
import sys
from pathlib import Path

import _common as C

mine, seed, seat = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
for opp in sys.argv[4:]:
    env = C.play(mine, opp, seed, swap=seat == 1)
    r = C.rewards(env)
    print(f"seed {seed} {Path(opp).parent.name:20s} 自分 {r[seat]:,.0f} 相手 {r[1 - seat]:,.0f} 差 {r[seat] - r[1 - seat]:+,.0f}",
          flush=True)
