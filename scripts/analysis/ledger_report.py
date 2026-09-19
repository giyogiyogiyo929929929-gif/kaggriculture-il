# -*- coding: utf-8 -*-
"""台帳（ledger_match.py / ledger_replay.py の pickle）を比べる：品目ごとの売上、支出、日ごとの所持金差（A − B）。

仕様: docs/05_evaluation.md §8（分析ツール）
使い方:
    .venv\\Scripts\\python.exe scripts\\analysis\\ledger_report.py <pkl>...
A は pickle の a_seat の側（手元の試合なら A、本番なら自分）。勝った試合・負けた試合を分けて合計も出す。
HIRE・BUY_LAND は台帳を通らないので、「雇用・土地など」は所持金の変化から逆算する。
"""
import collections
import pickle
import sys
from pathlib import Path

import _common as C

total = collections.defaultdict(collections.Counter)
for p in sys.argv[1:]:
    g = pickle.load(open(p, "rb"))
    a = g.get("a_seat", g.get("v5_seat", 0))
    seats = (a, 1 - a)
    sell = {s: collections.defaultdict(lambda: [0, 0]) for s in seats}
    spend = {s: collections.Counter() for s in seats}
    for step, s, op, item, price in g["ledger"]:
        if op == "SELL":
            sell[s][item][0] += 1
            sell[s][item][1] += price
        else:
            spend[s][{"BUY_SEED": "種", "BUY_ANIMAL": "家畜", "BUY_PRODUCT": "購入" + item[:4]}.get(op, op)] += price
    fa, fb = g["final"][a], g["final"][1 - a]
    tag = "勝" if fa > fb else ("負" if fa < fb else "分")
    print(f"\n=== {Path(p).name} seed {g['seed']} {tag} 最終差 A−B {fa - fb:+,.0f}（A {fa:,.0f} / B {fb:,.0f}）")
    rows = []
    for item in C.ITEMS:
        x, y = sell[a][item], sell[1 - a][item]
        if x[0] or y[0]:
            total[tag]["売:" + item] += x[1] - y[1]
            rows.append(f"{item[:5]} {x[1] - y[1]:+7d}（{x[0]}個@{x[1] / max(1, x[0]):.0f} / {y[0]}個@{y[1] / max(1, y[0]):.0f}）")
    print("  売上差:", " ".join(rows))
    for s in seats:
        income = sum(v[1] for v in sell[s].values())
        spend[s]["雇用・土地など"] = round(g["money"][0][s] + income - sum(spend[s].values()) - g["final"][s])
    parts = []
    for k in sorted(set(spend[a]) | set(spend[1 - a])):
        total[tag]["支:" + k] += spend[a][k] - spend[1 - a][k]
        parts.append(f"{k} {spend[a][k]:,}/{spend[1 - a][k]:,}")
    print("  支出 A/B:", " | ".join(parts))
    daily = {t // 24: m[a] - m[1 - a] for t, m in enumerate(g["money"])}
    print("  日ごとの所持金差:", " ".join(f"d{d}:{v:+.0f}" for d, v in daily.items() if d % 2 == 1 or d == 29))
for tag, c in total.items():
    print(f"\n=== {tag} の合計（A−B）")
    print("  " + ", ".join(f"{k} {v:+,.0f}" for k, v in sorted(c.items(), key=lambda kv: kv[1]) if v))
