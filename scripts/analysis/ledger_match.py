# -*- coding: utf-8 -*-
"""手元で1試合を回し、約定1個ずつの台帳・所持金の推移・行動を pickle に保存する。

仕様: docs/05_evaluation.md §8（分析ツール）
使い方:
    .venv\\Scripts\\python.exe scripts\\analysis\\ledger_match.py <A main.py> <B main.py> <seed> <out.pkl> [--swap]
A が席0（--swap で席1）。出力は ledger_report.py で読む（pickle の a_seat が A の席）。
"""
import argparse
import pickle

import _common as C

ap = argparse.ArgumentParser()
ap.add_argument("a")
ap.add_argument("b")
ap.add_argument("seed", type=int)
ap.add_argument("out")
ap.add_argument("--swap", action="store_true")
args = ap.parse_args()

ledger = C.Ledger()
env = C.play(args.a, args.b, args.seed, swap=args.swap)
ledger.close()
money = [[s[0]["observation"]["farms"][p]["money"] for p in (0, 1)] for s in env.steps]
actions = [[s[p]["action"] for p in (0, 1)] for s in env.steps]
final = C.rewards(env)
pickle.dump(dict(seed=args.seed, a_seat=1 if args.swap else 0, ledger=ledger.rows, money=money, actions=actions, final=final),
            open(args.out, "wb"))
print(args.seed, "final", final)
