# -*- coding: utf-8 -*-
"""本番の試合（seed・席・最終所持金）を、自分の版と手元の候補で再現し、1ドルまで一致する相手を探す。

仕様: docs/05_evaluation.md §8（分析ツール）
使い方:
    .venv\\Scripts\\python.exe scripts\\analysis\\fingerprint.py <自分の main.py> <live.pkl>[,<live2.pkl>...]
        [--min-score 2000] [--losses-only] [--cands 名前,名前] [--extra パス,パス] [--part 0 --parts 4]
- live.pkl は live_summary.py の出力。自分の main.py は、その試合を戦った版（例 submissions\\v6_preempt\\main.py）。
- 候補の既定は opponents\\*\\main.py 全部と submissions\\thomas_v94_safe\\main.py。
- 重いので --part/--parts で分けて並列に走らせられる。
"""
import argparse
import pickle

import _common as C

ap = argparse.ArgumentParser()
ap.add_argument("mine")
ap.add_argument("live")
ap.add_argument("--min-score", type=float, default=0)
ap.add_argument("--losses-only", action="store_true")
ap.add_argument("--cands", default="")
ap.add_argument("--extra", default="")
ap.add_argument("--part", type=int, default=0)
ap.add_argument("--parts", type=int, default=1)
args = ap.parse_args()

if args.cands:
    cands = {n: C.ROOT / "opponents" / n / "main.py" for n in args.cands.split(",")}
else:
    cands = {p.parent.name: p for p in sorted((C.ROOT / "opponents").glob("*/main.py"))}
    cands["v9/4"] = C.ROOT / "submissions" / "thomas_v94_safe" / "main.py"
for e in filter(None, args.extra.split(",")):
    cands[e] = C.path(e)

rows = [r for p in args.live.split(",") for r in pickle.load(open(p, "rb"))]
targets = [r for r in rows if r["kind"] == "public" and (r["op_score"] or 0) >= args.min_score
           and (r["diff"] < 0 or not args.losses_only)]
for i, r in enumerate(targets):
    if i % args.parts != args.part:
        continue
    seat, found = r["me_seat"], []
    for name, p in cands.items():
        try:
            env = C.play(args.mine, p, r["seed"], swap=seat == 1)
            got = (env.state[seat]["reward"], env.state[1 - seat]["reward"])
        except Exception as exc:  # 候補が落ちても続ける
            got = (None, repr(exc)[:40])
        if tuple(got) == tuple(r["final"]):
            found.append(name)
    print(f"{r['op'][:22]:22s} ({r['op_score']}) 本番 {r['final']} 差 {r['diff']:+,.0f} → 一致: {found or 'なし'}", flush=True)
