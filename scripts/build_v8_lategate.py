# -*- coding: utf-8 -*-
r"""submissions/v8_lategate/main.py を作る：v7_relax の末尾に候補D の層を足す。

仕様: docs/07_v4_improvement.md §3 候補D（探索：EXP-20260920-21 の d7）

    .venv\Scripts\python.exe scripts\build_v8_lategate.py

v9/4 の原本も v5〜v7 の層も1バイトも変えない。末尾に層を足すだけ。
"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
original = (ROOT / "submissions" / "thomas_v94" / "main.py").read_bytes()
v7 = (ROOT / "submissions" / "v7_relax" / "main.py").read_bytes()
assert v7.startswith(original), "v7 の先頭が v9/4 原本と一致しない"

LAYER = '''

# ---- kaggriculture-il 追加：候補D「終盤だけ RACEGATE を開けて、牛乳・いちごを先に売る」 ----
# 仕様: docs/07_v4_improvement.md §3 候補D（探索：EXP-20260920-21 の d7）
#
# v9/4 の RACEGATE は「現在価格が基準価格以下の品目は、予約（テープの将来の売りの前倒し）をしない」。
# 終盤の牛乳（基準160）は 30〜80、いちご（基準120）は 15〜50 で必ず基準以下になるため、
# この2品目は終盤ずっと前倒しが止まり、テープどおりの時刻にしか売れない。
# 相手（v49 など）は値が戻ったところを先に取りに来るので、同じ日の 1〜2 時間の差で負ける。
#
# この層は、終盤だけ・この2品目だけ・値が付いているときだけ、基準価格を一時的に 0 にして予約を通す。
# コピーと確定した試合では何もしない（候補A・A2 が握っている売りの競争を乱すと退行するため。EXP-20260920-21 結果2）。
_KIL_D_INNER = [value for value in list(globals().values()) if callable(value)][-1]
_KIL_D_ITEMS = ("MILK", "STRAWBERRY")
_KIL_D_START = 480          # day 20 から（開始日は 18/20/24 で差が出なかった）
_KIL_D_MINPRICE = 30        # これ未満では何もしない（底値での投げ売りを避ける。下限10 は悪化した）
_KIL_D_REPORT = dict(d_turns=0, d_items=0, d_errors=0)


def _kil_d_agent(observation, configuration=None):
    try:
        step = int(observation["step"])
        if step < _KIL_D_START:
            return _KIL_D_INNER(observation, configuration)
        state = _KIL_V5_STATE.get(int(observation["player"]))
        if state is not None and state.get("copy"):
            return _KIL_D_INNER(observation, configuration)
        prices = observation["market"]["prices"]
        opened = [item for item in _KIL_D_ITEMS
                  if _KIL_D_MINPRICE <= prices.get(item, 0) <= V9_RACEGATE_BASE[item]]
        if not opened:
            return _KIL_D_INNER(observation, configuration)
        saved = {item: V9_RACEGATE_BASE[item] for item in opened}
        _KIL_D_REPORT["d_turns"] += 1
        _KIL_D_REPORT["d_items"] += len(opened)
        for item in opened:
            V9_RACEGATE_BASE[item] = 0
        try:
            return _KIL_D_INNER(observation, configuration)
        finally:
            V9_RACEGATE_BASE.update(saved)
    except Exception:
        # 何かあっても試合を止めない（doc 01 NFR-2）。内側は v7 の安全包みなので例外を出さない。
        _KIL_D_REPORT["d_errors"] += 1
        return _KIL_D_INNER(observation, configuration)


_kil_d_agent.telemetry = _KIL_D_REPORT
'''

out_dir = ROOT / "submissions" / "v8_lategate"
out_dir.mkdir(parents=True, exist_ok=True)
body = v7 + LAYER.encode("utf-8")
target = out_dir / "main.py"
target.write_bytes(body)

assert body.startswith(original)
assert body[:len(v7)] == v7, "v7 の部分が変わっている"
print(f"{target}: {len(body):,} bytes")
print(f"  v9/4 原本と同じ先頭: {len(original):,} bytes  SHA-256 {hashlib.sha256(original).hexdigest()[:16]}…")
print(f"  v7 と同じ先頭      : {len(v7):,} bytes  SHA-256 {hashlib.sha256(v7).hexdigest()[:16]}…")
print(f"  main.py            : SHA-256 {hashlib.sha256(body).hexdigest()}")
