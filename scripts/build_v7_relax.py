# -*- coding: utf-8 -*-
r"""submissions/v7_relax/main.py を作る：v6_preempt のコピー判定だけを候補A3 の判定に変える。

仕様: docs/07_v4_improvement.md §3 候補A3

    .venv\Scripts\python.exe scripts\build_v7_relax.py
"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
original = (ROOT / "submissions" / "thomas_v94" / "main.py").read_bytes()
v6 = (ROOT / "submissions" / "v6_preempt" / "main.py").read_bytes()
assert v6.startswith(original)
head, tail = v6[:len(original)], v6[len(original):].decode("utf-8")

REPLACEMENTS = [
    (
        "# 判定：雑草タイルを空きとみなした自分と相手の農場が、167ステップ目まで毎ターン一致し続けたら v9/4 のコピーと確定する。\n"
        "#       一度でも違えばその試合では二度と反応しない。確定後は比べない（自分が動きを変えても判定は崩れない）。\n",
        "# 判定（候補A3 で変更、docs/07_v4_improvement.md §3 候補A3・EXP-20260919-17）：96〜167 ステップで、雑草タイルを空きとみなし\n"
        "#       所持金を除いた自分と相手の農場が毎ターン一致し、かつ所持金の差（自分 − 相手）が一定のままなら v9/4 のコピーと確定する\n"
        "#       （序盤だけ変えて所持金を上乗せした「コピー＋小さな上乗せ」も捕まえる。別系統は売り買いが違うので差が動く）。\n"
        "#       一度でも違えばその試合では二度と反応しない。確定後は比べない（自分が動きを変えても判定は崩れない）。\n",
    ),
    (
        "_KIL_V5_COMMIT_STEP = 167\n",
        "_KIL_V5_START_STEP = 96\n_KIL_V5_COMMIT_STEP = 167\n",
    ),
    (
        '    """雑草を除いた農場。雑草は両者で別々の乱数で生え、コピー同士でも食い違う。"""\n',
        '    """雑草と所持金を除いた農場。雑草は両者で別々の乱数で生え、コピー同士でも食い違う。所持金は差が一定かを別に見る。"""\n',
    ),
    (
        '    return tiles, {key: value for key, value in farm.items() if key != "tiles"}\n',
        '    return tiles, {key: value for key, value in farm.items() if key not in ("tiles", "money")}\n',
    ),
    (
        '    if st["same"] and not st["copy"]:\n'
        '        if _kil_v5_key(farms[player]) != _kil_v5_key(farms[1 - player]):\n',
        '    if st["same"] and not st["copy"] and step >= _KIL_V5_START_STEP:\n'
        '        delta = farms[player]["money"] - farms[1 - player]["money"]\n'
        '        if st.setdefault("delta", delta) != delta or _kil_v5_key(farms[player]) != _kil_v5_key(farms[1 - player]):\n',
    ),
]
for old, new in REPLACEMENTS:
    assert tail.count(old) == 1, old
    tail = tail.replace(old, new)

out = ROOT / "submissions" / "v7_relax"
out.mkdir(exist_ok=True)
data = head + tail.encode("utf-8")
(out / "main.py").write_bytes(data)
print("bytes", len(data), "sha256", hashlib.sha256(data).hexdigest())
