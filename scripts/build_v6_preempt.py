# -*- coding: utf-8 -*-
r"""submissions/v6_preempt/main.py を作る：v5_race（安全包みの前まで）＋ 候補A2 の層 ＋ 安全包み。

仕様: docs/07_v4_improvement.md §3 候補A2

    .venv\Scripts\python.exe scripts\build_v6_preempt.py
"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
original = (ROOT / "submissions" / "thomas_v94" / "main.py").read_bytes()
v5 = (ROOT / "submissions" / "v5_race" / "main.py").read_bytes()
assert v5.startswith(original)
marker = "\n# ---- kaggriculture-il による追加".encode("utf-8")
cut = v5.rindex(marker)
body, safe_tail = v5[:cut], v5[cut:]
old = "安全包み（v4 と同じ。ここより上の候補A の層を包む）".encode("utf-8")
assert old in safe_tail
safe_tail = safe_tail.replace(old, "安全包み（v4 と同じ。ここより上の候補A2 の層を包む）".encode("utf-8"))

LAYER = '''

# ---- kaggriculture-il 追加：候補A2「コピーの PREDICT を1ターン先回りする」 ----
# 仕様: docs/07_v4_improvement.md §3 候補A2（根拠：EXP-20260919-14 結果5）
# コピーと確定した試合（候補A の _KIL_V5_STATE）だけ動く。コピーの PREDICT（_v92_predict）が見る「こちらの売り」を
# 自分で作り、v9/4 自身の _v92_p_forecast で次のターンのコピーの発火を予測して、同じ売りを1ターン前に出す。
_KIL_PE_INNER = [value for value in list(globals().values()) if callable(value)][-1]
_KIL_PE_LEAD = 1
_KIL_PE_STATE = {}
_KIL_PE_REPORT = dict(fires=0, units=0, errors=0)


def _kil_pe_best(st, obs, step):
    """コピーが step に使う最良の記録（コピーは step % _V92_P_EVERY == 0 か最初に作り直し、間は前の結果を使う）。"""
    if step not in st["best"]:
        prev = st["best"].get(step - 1)
        if step % _V92_P_EVERY == 0 or prev is None:
            st["best"][step] = _v92_p_forecast({"step": step, "town": obs["town"]}, {"obs": st["seen"]})
        else:
            st["best"][step] = prev
    return st["best"][step]


def _kil_pe(observation, action, prev):
    player, step = int(observation["player"]), int(observation["step"])
    st = _KIL_PE_STATE.get(player)
    if st is None or step <= st["step"]:
        st = _KIL_PE_STATE[player] = {"step": -1, "seen": {}, "best": {}}
    st["step"] = step
    # コピーが復元する「こちらの売り」＝ こちらが前のターンに実際に売った数（RACE と同じく値段 > 3・2個以上）
    if prev and prev["step"] == step - 1:
        for i, item in enumerate(_V92_P_ITEMS):
            if prev["prices"].get(item, 0) > 3 and prev["own"].get(item, 0) >= 2:
                st["seen"][(step - 1, i)] = prev["own"][item]
    copy_state = _KIL_V5_STATE.get(player)
    if not copy_state or not copy_state["copy"] or step < 150 - _KIL_PE_LEAD or step >= 700 - _KIL_PE_LEAD:
        return action
    for s in range(max(st["best"], default=step - 1) + 1, step + _KIL_PE_LEAD + 1):
        _kil_pe_best(st, observation, s)
    target = step + _KIL_PE_LEAD
    best = st["best"].get(target) or []
    native = _IMPL.chassis.players.get(player)
    if not best or not native or native.get("route") not in _IMPL.chassis.routes:
        return action
    tape = _IMPL.chassis.routes[native["route"]]
    market = [list(o) for o in action.get("market") or []]
    already = {o[1] for o in market if len(o) > 1 and o[0] in ("SELL", "BUY_PRODUCT")}
    stock = None
    changed = False
    for i, item in enumerate(_V92_P_ITEMS):
        if item not in _V92_P_USE or item in already or len(market) >= MAX_ORDERS:
            continue
        # コピーは target で「target+1・target+2 に 4個以上」を見て発火する（_v92_predict と同じ規則）
        if not any(ev.get((target + 1, i), 0) + ev.get((target + 2, i), 0) >= _V92_P_K for ev in best):
            continue
        ours = 0
        for t in range(step + 1, min(len(tape), target + _V92_P_H + 1)):
            ours += sum(min(100, int(o[2])) for o in (tape[t] or {}).get("market") or []
                        if len(o) >= 3 and o[0] == "SELL" and o[1] == item)
        if stock is None:
            stock = projected_shed(action, FarmView(observation))
        qty = min(int(stock.get(item, 0)), ours)
        if qty > 0:
            market.insert(0, ["SELL", item, qty])
            _KIL_PE_REPORT["fires"] += 1
            _KIL_PE_REPORT["units"] += qty
            changed = True
    if not changed:
        return action
    result = dict(action)
    result["market"] = market[:MAX_ORDERS]
    return result


def _kil_pe_agent(observation, configuration=None):
    # 中の RACE 層が prev を今のターンで上書きする前に、前のターンの記録を取っておく
    try:
        prev = (_V9_RACE.get(int(observation["player"])) or {}).get("prev")
    except Exception:
        prev = None
    action = _KIL_PE_INNER(observation, configuration)
    try:
        return _kil_pe(observation, action, prev)
    except Exception:
        _KIL_PE_REPORT["errors"] += 1
        return action
'''.encode("utf-8")

out = ROOT / "submissions" / "v6_preempt"
out.mkdir(exist_ok=True)
data = body + LAYER + safe_tail
(out / "main.py").write_bytes(data)
print("bytes", len(data), "sha256", hashlib.sha256(data).hexdigest())
