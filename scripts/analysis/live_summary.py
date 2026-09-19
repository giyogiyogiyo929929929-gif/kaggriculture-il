# -*- coding: utf-8 -*-
"""本番の公開対戦（生リプレイ）を1試合ずつ要約し、fingerprint.py 用の pickle を作る。

仕様: docs/05_evaluation.md §8（分析ツール）
使い方:
    .venv\\Scripts\\python.exe scripts\\analysis\\live_summary.py <raw_dir> <leaderboard.csv> <out.pkl> [--me 名前]
- コピー判定：雑草を空きとみなした両者の農場（所持金込み）が step 0〜167 で一致し続けたか（v6 の判定）
- 最初に農場が食い違ったステップ、日ごとの所持金差、品目ごとの売り注文数
leaderboard.csv は `kaggle competitions leaderboard kaggriculture -d` の zip の中身（相手のスコア表示用）。
"""
import argparse
import collections
import glob
import json
import os
import pickle

import pandas as pd

import _common as C

ap = argparse.ArgumentParser()
ap.add_argument("raw")
ap.add_argument("lb")
ap.add_argument("out")
ap.add_argument("--me", default=None)
args = ap.parse_args()
score = dict(zip(*[pd.read_csv(args.lb)[c] for c in ("TeamName", "Score")]))

rows = []
for p in sorted(glob.glob(os.path.join(args.raw, "*.json"))):
    d = json.load(open(p, encoding="utf-8"))
    names = d["info"]["TeamNames"]
    kind = "validation" if names[0] == names[1] else "public"
    me = 0 if kind == "validation" else C.my_seat(names, args.me)
    op = 1 - me
    steps, rewards = d["steps"], d["rewards"]
    first = None
    for t, s in enumerate(steps):
        f = s[0]["observation"]["farms"]
        if C.copy_key(f[me]) != C.copy_key(f[op]):
            first = t
            break
    daily = {}
    for t, s in enumerate(steps):
        f = s[0]["observation"]["farms"]
        daily[t // 24] = f[me]["money"] - f[op]["money"]
    sells = {x: collections.Counter() for x in (me, op)}
    for t in range(1, len(steps)):
        for x in (me, op):
            for o in (steps[t][x].get("action") or {}).get("market") or []:
                if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL":
                    sells[x][o[1]] += int(o[2])
    diff = (rewards[me] or 0) - (rewards[op] or 0)
    rows.append(dict(ep=d["info"]["EpisodeId"], seed=d["info"].get("seed"), kind=kind, op=names[op], op_score=score.get(names[op]),
                     me_seat=me, final=(rewards[me], rewards[op]), diff=diff, copy=first is None or first > 167, first=first,
                     daily=daily, sells_me=dict(sells[me]), sells_op=dict(sells[op]),
                     statuses=[s.get("status") for s in steps[-1]]))
pickle.dump(rows, open(args.out, "wb"))
res = collections.Counter()
for r in rows:
    tag = "勝" if r["diff"] > 0 else ("負" if r["diff"] < 0 else "分")
    res[(r["kind"], "コピー" if r["copy"] else "別系統", tag)] += 1
    print(f"{r['ep']} {r['kind'][:3]} 席{r['me_seat']} {tag} {r['diff']:+9.0f} 相手 {r['op'][:24]:24s} "
          f"({r['op_score']}) コピー={'Y' if r['copy'] else 'n'} 食い違い={r['first']} 状態={r['statuses']}")
print()
for k, v in sorted(res.items()):
    print(k, v)
