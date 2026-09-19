# -*- coding: utf-8 -*-
"""v9/4 系エージェントの層ごとの出力を追う（挙動は変えない）。

仕様: docs/05_evaluation.md §8（分析ツール）
v9/4 は機能を「親 agent を包む層」として積み重ね、各層の親を `*_PARENT` などのグローバル名で持っている。
その参照を記録つきの関数に差し替えて、どの層が何を足したかを見る。

使い方:
    .venv\\Scripts\\python.exe scripts\\analysis\\layer_trace.py sells <A main.py> <B main.py> <seed> <ITEM> <step_from> <step_to>
        → 各層の出力のうち ITEM の SELL をステップごとに表示（内側の層 → 外側の層の順に並ぶ）
    .venv\\Scripts\\python.exe scripts\\analysis\\layer_trace.py predict <A main.py> <B main.py> <seed> <out.pkl>
        → PREDICT 層（_V92_P_PARENT → _V92_Q_PARENT）が売りを足したステップ・品・個数を両者について記録
A が席0。表示は sys.__stderr__ に出す（kaggle-environments は stdout を取り込むため）。
"""
import functools
import pickle
import sys

import _common as C

out = sys.__stderr__


def sells(action):
    total = {}
    for o in (action or {}).get("market") or []:
        if len(o) > 2 and o[0] == "SELL":
            total[o[1]] = total.get(o[1], 0) + int(o[2])
    return total


def trace_sells(g, tag, item, s0, s1):
    names = [k for k, v in list(g.items())
             if callable(v) and not isinstance(v, type) and getattr(v, "__name__", "") == "agent" and k != "agent"]
    for name in names:
        inner = g[name]

        def logged(observation, configuration=None, _inner=inner, _name=name):
            action = _inner(observation, configuration)
            step = int(observation["step"])
            if s0 <= step <= s1:
                qty = [o[2] for o in (action or {}).get("market") or [] if len(o) > 2 and o[0] == "SELL" and o[1] == item]
                print(f"  {tag} step {step} {_name:24s} SELL {item} {qty}", file=out, flush=True)
            return action
        functools.update_wrapper(logged, inner)
        g[name] = logged


def trace_predict(g, player, fires):
    before = {}
    inner_p, outer_p = g["_V92_P_PARENT"], g["_V92_Q_PARENT"]

    def p_in(observation, configuration=None):
        action = inner_p(observation, configuration)
        before[int(observation["step"])] = sells(action)
        return action

    def p_out(observation, configuration=None):
        action = outer_p(observation, configuration)
        step = int(observation["step"])
        prior = before.get(step, {})
        for item, qty in sells(action).items():
            if qty > prior.get(item, 0):
                fires.append((step, player, item, qty - prior.get(item, 0)))
        return action

    functools.update_wrapper(p_in, inner_p)
    functools.update_wrapper(p_out, outer_p)
    g["_V92_P_PARENT"], g["_V92_Q_PARENT"] = p_in, p_out


mode, a_path, b_path, seed = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
a, b = C.load(a_path), C.load(b_path)
if mode == "sells":
    item, s0, s1 = sys.argv[5], int(sys.argv[6]), int(sys.argv[7])
    trace_sells(a.__globals__, "A", item, s0, s1)
    trace_sells(b.__globals__, "B", item, s0, s1)
    env = C.play(a, b, seed)
    print("final", C.rewards(env), file=out)
elif mode == "predict":
    fires = []
    trace_predict(a.__globals__, 0, fires)
    trace_predict(b.__globals__, 1, fires)
    env = C.play(a, b, seed)
    pickle.dump(fires, open(sys.argv[5], "wb"))
    print(seed, "final", C.rewards(env), "発火 A", sum(f[1] == 0 for f in fires), "B", sum(f[1] == 1 for f in fires), file=out)
else:
    sys.exit("mode は sells か predict")
