# -*- coding: utf-8 -*-
r"""submissions/v13_v51copy/main.py を作る：v51 ＋ コピー判定（記録だけ）＋ 安全包み（ADR-0004 第2段）。

仕様: docs/adr/0004-switch-base-to-v51.md（第2段）、docs/07_v4_improvement.md §3 候補A3（判定の中身）

    .venv\Scripts\python.exe scripts\build_v13_v51copy.py

**第2段は判定を入れるだけで、行動は1つも変えない。** v12 と同じ試合結果になることをテストで確かめる。
`opponents\v51\main.py` は1バイトも変えない。層の順番は v51 → 判定 → 安全包み。
"""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_v12_v51safe import LAYER as SAFE_LAYER  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

COPY_LAYER = '''

# ---- kaggriculture-il 追加：コピー判定の移植（ADR-0004 第2段、2026-09-20） ----
# ここから上は opponents\\v51\\main.py と1バイトも違わない。
# 判定は docs/07_v4_improvement.md §3 候補A3 と同じもの（v9/4 系の v7_relax から移した）：
#   96〜167 ステップで、雑草タイルを空きとみなし所持金を除いた自分と相手の農場が毎ターン一致し、
#   かつ所持金の差（自分 − 相手）が一定のままなら「相手は自分のコピー」と確定する。
#   一度でも違えばその試合では二度と反応しない。確定後は比べない。
# **第2段では確定しても行動を変えない**（誤爆の有無を測るための記録だけ）。動かすのは第3段。
_KIL_C_INNER = [value for value in list(globals().values()) if callable(value)][-1]
_KIL_C_STATE = {}
_KIL_C_START_STEP = 96
_KIL_C_COMMIT_STEP = 167
_KIL_C_REPORT = dict(copy_games=0, copy_turns=0, c_errors=0)


def _kil_c_key(farm):
    """雑草と所持金を除いた農場。雑草は両者で別々の乱数で生え、コピー同士でも食い違う。"""
    tiles = [[None if isinstance(tile, dict) and tile.get("kind") == "WEED" else tile for tile in row]
             for row in farm.get("tiles") or []]
    return tiles, {key: value for key, value in farm.items() if key not in ("tiles", "money")}


def _kil_c_update(observation):
    player = int(observation["player"])
    step = int(observation["step"])
    st = _KIL_C_STATE.get(player)
    if st is None or step <= st["step"]:
        st = _KIL_C_STATE[player] = {"step": -1, "same": True, "copy": False}
        if step == 0:
            _KIL_C_REPORT.update(copy_games=0, copy_turns=0, c_errors=0)
    st["step"] = step
    farms = observation["farms"]
    if st["same"] and not st["copy"] and step >= _KIL_C_START_STEP:
        delta = farms[player]["money"] - farms[1 - player]["money"]
        if st.setdefault("delta", delta) != delta or _kil_c_key(farms[player]) != _kil_c_key(farms[1 - player]):
            st["same"] = False
        elif step >= _KIL_C_COMMIT_STEP:
            st["copy"] = True
            _KIL_C_REPORT["copy_games"] += 1
    if st["copy"]:
        _KIL_C_REPORT["copy_turns"] += 1
    return st["copy"]


def _kil_c_agent(observation, configuration=None):
    try:
        _kil_c_update(observation)
    except Exception:
        # 判定で何かあっても試合は続ける（doc 01 NFR-2）。行動には影響しない。
        _KIL_C_REPORT["c_errors"] += 1
    return _KIL_C_INNER(observation, configuration)
'''

if __name__ == "__main__":
    base = (ROOT / "opponents" / "v51" / "main.py").read_bytes()
    out_dir = ROOT / "submissions" / "v13_v51copy"
    out_dir.mkdir(parents=True, exist_ok=True)
    body = base + COPY_LAYER.encode("utf-8") + SAFE_LAYER.encode("utf-8")
    target = out_dir / "main.py"
    target.write_bytes(body)
    assert body[: len(base)] == base, "v51 の部分が変わっている"
    print(f"{target}: {len(body):,} bytes")
    print(f"  v51 原本と同じ先頭: {len(base):,} bytes  SHA-256 {hashlib.sha256(base).hexdigest()[:16]}…")
    print(f"  main.py           : SHA-256 {hashlib.sha256(body).hexdigest()}")
