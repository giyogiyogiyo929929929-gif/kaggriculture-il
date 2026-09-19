# -*- coding: utf-8 -*-
r"""submissions/v5_race/main.py を作る：v9/4 原本 + 候補A の層 + v4 と同じ安全包み。

仕様: docs/07_v4_improvement.md §3 候補A, §4

    .venv\Scripts\python.exe scripts\build_v5_race.py
"""
import hashlib
from pathlib import Path

ROOT = Path(r"C:\Users\nay92\Desktop\kaggriculture-il")
original = (ROOT / "submissions" / "thomas_v94" / "main.py").read_bytes()
v4 = (ROOT / "submissions" / "thomas_v94_safe" / "main.py").read_bytes()
assert v4.startswith(original)
safe_tail = v4[len(original):]
old = "ここより上は thomas_v94 の main.py と1バイトも違わない".encode("utf-8")
assert old in safe_tail
safe_tail = safe_tail.replace(old, "安全包み（v4 と同じ。ここより上の候補A の層を包む）".encode("utf-8"))

LAYER = '''

# ---- kaggriculture-il 追加：候補A「コピー相手のときだけ売りの先読みを深くする」（ここから上は v9/4 原本と1バイトも違わない） ----
# 仕様: docs/07_v4_improvement.md §3 候補A（根拠：EXP-20260919-14）
# 判定：雑草タイルを空きとみなした自分と相手の農場が、167ステップ目まで毎ターン一致し続けたら v9/4 のコピーと確定する。
#       一度でも違えばその試合では二度と反応しない。確定後は比べない（自分が動きを変えても判定は崩れない）。
# 動き：確定後だけ、v9/4 の売りの先読み幅 V9_RACE_DEFAULT / V9_RACE_MAX を呼び出しの間だけ 52 に固定する。
_KIL_V5_INNER = [value for value in list(globals().values()) if callable(value)][-1]
_KIL_V5_STATE = {}
_KIL_V5_COMMIT_STEP = 167
_KIL_V5_HORIZON = 52
_KIL_V5_REPORT = dict(copy_games=0, copy_turns=0)


def _kil_v5_key(farm):
    """雑草を除いた農場。雑草は両者で別々の乱数で生え、コピー同士でも食い違う。"""
    tiles = [[None if isinstance(tile, dict) and tile.get("kind") == "WEED" else tile for tile in row]
             for row in farm.get("tiles") or []]
    return tiles, {key: value for key, value in farm.items() if key != "tiles"}


def _kil_v5_agent(observation, configuration=None):
    player = int(observation["player"])
    step = int(observation["step"])
    st = _KIL_V5_STATE.get(player)
    if st is None or step <= st["step"]:
        st = _KIL_V5_STATE[player] = {"step": -1, "same": True, "copy": False}
    st["step"] = step
    farms = observation["farms"]
    if st["same"] and not st["copy"]:
        if _kil_v5_key(farms[player]) != _kil_v5_key(farms[1 - player]):
            st["same"] = False
        elif step >= _KIL_V5_COMMIT_STEP:
            st["copy"] = True
            _KIL_V5_REPORT["copy_games"] += 1
    if not st["copy"]:
        return _KIL_V5_INNER(observation, configuration)
    _KIL_V5_REPORT["copy_turns"] += 1
    g = globals()
    saved = (g["V9_RACE_DEFAULT"], g["V9_RACE_MAX"])
    g["V9_RACE_DEFAULT"] = g["V9_RACE_MAX"] = _KIL_V5_HORIZON
    try:
        return _KIL_V5_INNER(observation, configuration)
    finally:
        g["V9_RACE_DEFAULT"], g["V9_RACE_MAX"] = saved
'''.encode("utf-8")

out = ROOT / "submissions" / "v5_race"
out.mkdir(exist_ok=True)
data = original + LAYER + safe_tail
(out / "main.py").write_bytes(data)
print("bytes", len(data), "sha256", hashlib.sha256(data).hexdigest())
print(safe_tail.decode("utf-8")[:200])
