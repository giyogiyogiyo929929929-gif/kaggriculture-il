# -*- coding: utf-8 -*-
"""本番リプレイの両者の行動をそのまま環境に流し直し、約定1個ずつの台帳を取る（相手のコードが無くてもよい）。

仕様: docs/05_evaluation.md §8（分析ツール）
使い方:
    .venv\\Scripts\\python.exe scripts\\analysis\\ledger_replay.py <replay.json> <out.pkl> [--me 名前]
席は本番どおり。a_seat は自分の席。最終所持金が本番と一致したかを表示する（一致しなければ台帳は信用しない）。
"""
import argparse
import json
import pickle

import _common as C

ap = argparse.ArgumentParser()
ap.add_argument("replay")
ap.add_argument("out")
ap.add_argument("--me", default=None)
args = ap.parse_args()

d = json.load(open(args.replay, encoding="utf-8"))
steps = d["steps"]


def tape(player):
    def agent(obs, config=None):
        t = int(obs["step"]) + 1
        return steps[t][player]["action"] if t < len(steps) else {"farmer": ["PASS"], "hands": [], "market": []}
    return agent


ledger = C.Ledger()
env = C.make("kaggriculture", configuration={"seed": d["info"]["seed"]})
env.run([tape(0), tape(1)])
ledger.close()
final = C.rewards(env)
names = d["info"]["TeamNames"]
me = C.my_seat(names, args.me) if names[0] != names[1] else 0
money = [[s[0]["observation"]["farms"][p]["money"] for p in (0, 1)] for s in env.steps]
pickle.dump(dict(seed=d["info"]["seed"], a_seat=me, ledger=ledger.rows, money=money, final=final), open(args.out, "wb"))
print(f"相手 {names[1 - me]}: 再現 {final} 本番 {d['rewards']} 一致={final == d['rewards']}")
