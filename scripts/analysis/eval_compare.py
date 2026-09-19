# -*- coding: utf-8 -*-
"""scripts\\eval.py の JSON（data\\eval\\<版>\\vs_<相手>.json）を試合単位で集計し、2つの版を比べる。

仕様: docs/05_evaluation.md §8（分析ツール）
使い方:
    .venv\\Scripts\\python.exe scripts\\analysis\\eval_compare.py <eval_dir>               # 1つの版の相手ごとの勝敗
    .venv\\Scripts\\python.exe scripts\\analysis\\eval_compare.py <eval_dir_A> <eval_dir_B> # 2つの版を同じ相手・seed・席で比べる
「所持金が完全一致」は、同じ相手・seed・席で A と B の所持金が1ドルまで同じだった試合数（改変が他の相手に影響しないかの確認）。
"""
import json
import sys
from pathlib import Path

import _common as C  # noqa: F401（出力の文字コード設定）


def load(p):
    d = json.load(open(p, encoding="utf-8"))
    g = {(m["seed"], m["swap"]): m["money"] for m in d["matches_detail"]}
    w = sum(a > b for a, b in g.values())
    l = sum(a < b for a, b in g.values())
    diff = sum(a - b for a, b in g.values()) / max(1, len(g))
    return g, w, l, len(g) - w - l, diff


dirs = [Path(x) for x in sys.argv[1:3]]
same_total = total = 0
for f in sorted(dirs[0].glob("vs_*.json")):
    ga, w, l, d, diff = load(f)
    line = f"{f.stem[3:]:22s} A {w}勝 {l}敗 {d}分 平均差 {diff:+,.0f}"
    if len(dirs) == 2 and (dirs[1] / f.name).exists():
        gb, w2, l2, d2, diff2 = load(dirs[1] / f.name)
        same = sum(ga[k] == gb.get(k) for k in ga)
        same_total += same
        total += len(ga)
        line += f"   B {w2}勝 {l2}敗 {d2}分 平均差 {diff2:+,.0f}   所持金が完全一致 {same}/{len(ga)}"
    print(line)
if total:
    print(f"合計 所持金が完全一致 {same_total}/{total}")
