# -*- coding: utf-8 -*-
r"""v14_queueclosure を作る：v12 の末尾に有効売却キューの前詰め層を足す。

仕様: docs/adr/0005-selective-public-base-adoption.md

    .venv\Scripts\python.exe scripts\build_v14_queueclosure.py

`submissions\v12_v51safe\main.py` は1バイトも変えず、末尾に独立層を追加する。
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

QUEUE_LAYER = r'''

# ---- kaggriculture-il 追加：final effective-queue closure（ADR-0005、2026-09-21） ----
# ここから上は submissions\v12_v51safe\main.py と1バイトも違わない。
# 実効数量0の現金商品SELLだけを穴にし、後続の実行可能SELLを安定的に前詰めする。
# 出典：lynnsakurai/farmer-john-and-the-idle-seller（Apache-2.0）。
_KIL_QUEUE_PARENT = [value for value in list(globals().values()) if callable(value)][-1]
_KIL_Q_ITEMS = frozenset((
    "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL",
))
_KIL_Q_REPORT = {
    "changed_turns": 0,
    "zeroed_orders": 0,
    "pulled_orders": 0,
    "pulled_slots": 0,
    "errors": 0,
}


def _kil_q_standard(configuration):
    if configuration is None:
        return True
    getter = configuration.get if hasattr(configuration, "get") else None
    if getter is None:
        return False
    return all(getter(key, expected) == expected for key, expected in (
        ("boardSize", 10),
        ("turnsPerDay", 24),
        ("shedCapacity", 100),
        ("maxMarketOrdersPerTurn", 10),
    ))


def _kil_q_close(observation, action):
    if not isinstance(action, dict):
        return action
    market = action.get("market") or []
    if not isinstance(market, list) or len(market) < 2:
        return action

    projected = dict(projected_shed(action, FarmView(observation)))
    remaining = {item: max(0, int(projected.get(item, 0))) for item in _KIL_Q_ITEMS}
    revised = []
    zeroed = 0

    for raw in market:
        order = list(raw) if isinstance(raw, (list, tuple)) else raw
        if (isinstance(order, list) and len(order) >= 3 and
                order[0] == "SELL" and order[1] in _KIL_Q_ITEMS):
            requested = max(0, int(order[2]))
            quantity = min(requested, remaining[order[1]])
            remaining[order[1]] -= quantity
            if quantity <= 0:
                revised.append([])
                zeroed += 1
            else:
                revised.append(order)
        else:
            revised.append(order)

    holes = []
    pulled = 0
    distance = 0
    for index, order in enumerate(revised):
        if not order:
            holes.append(index)
            continue
        movable = (
            isinstance(order, list) and len(order) >= 3 and
            order[0] == "SELL" and order[1] in _KIL_Q_ITEMS and int(order[2]) > 0
        )
        if not movable or not holes:
            continue
        target = holes.pop(0)
        revised[target] = order
        revised[index] = []
        holes.append(index)
        pulled += 1
        distance += index - target

    if revised == market:
        return action
    _KIL_Q_REPORT["changed_turns"] += 1
    _KIL_Q_REPORT["zeroed_orders"] += zeroed
    _KIL_Q_REPORT["pulled_orders"] += pulled
    _KIL_Q_REPORT["pulled_slots"] += distance
    return dict(action, market=revised)

def _kil_queue_agent(observation, configuration=None):
    action = _KIL_QUEUE_PARENT(observation, configuration)
    try:
        if isinstance(observation, dict) and int(observation.get("step", 0)) == 0:
            for key in _KIL_Q_REPORT:
                _KIL_Q_REPORT[key] = 0
        if _kil_q_standard(configuration):
            action = _kil_q_close(observation, action)
    except Exception:
        _KIL_Q_REPORT["errors"] += 1
    return action


_kil_queue_agent.telemetry = _KIL_Q_REPORT
_kil_queue_agent = globals().pop("_kil_queue_agent")
'''


if __name__ == "__main__":
    base = (ROOT / "submissions" / "v12_v51safe" / "main.py").read_bytes()
    out_dir = ROOT / "submissions" / "v14_queueclosure"
    out_dir.mkdir(parents=True, exist_ok=True)
    body = base + QUEUE_LAYER.encode("utf-8")
    target = out_dir / "main.py"
    target.write_bytes(body)
    assert body[: len(base)] == base, "v12 の部分が変わっている"
    print(f"{target}: {len(body):,} bytes")
    print(f"  v12 原本と同じ先頭: {len(base):,} bytes  SHA-256 {hashlib.sha256(base).hexdigest()[:16]}…")
    print(f"  main.py          : SHA-256 {hashlib.sha256(body).hexdigest()}")
