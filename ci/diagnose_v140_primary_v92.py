from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from kaggle_environments import make
from scripts.eval import resolve_agent

EVENT_INSERT = '''        qty = min(int(stock.get(item, 0)), ours)\n        if qty > 0:\n'''
EVENT_REPLACEMENT = '''        qty = min(int(stock.get(item, 0)), ours)\n        _v140_preds = [int(ev.get((step + 1, i), 0) + ev.get((step + 2, i), 0)) for ev in best]\n        _v140_future_sales = []\n        for _t in range(step + 1, min(len(tape), step + _V92_P_H + 1)):\n            _q = sum(min(100, int(o[2])) for o in (tape[_t] or {}).get("market") or []\n                     if len(o) >= 3 and o[0] == "SELL" and o[1] == item)\n            if _q:\n                _v140_future_sales.append([int(_t), int(_q)])\n        _v140_exposure = float(_r37_quote_priority(obs, ["SELL", item, qty], stock)) if qty > 0 else 0.0\n        _V140_PRIMARY_DIAG.append({\n            "step": int(step),\n            "item": item,\n            "threshold": int(_V140_PRIMARY_THRESHOLD),\n            "preds": _v140_preds,\n            "votes_active": int(votes),\n            "votes_k1": int(sum(1 for x in _v140_preds if x >= 1)),\n            "votes_k2": int(sum(1 for x in _v140_preds if x >= 2)),\n            "ours": int(ours),\n            "stock": int(stock.get(item, 0)),\n            "qty": int(qty),\n            "r37_quote_exposure": _v140_exposure,\n            "future_sales": _v140_future_sales[:12],\n            "market_before": [list(o) for o in market],\n            "already": sorted(already),\n            "top_score": float(st.get("top_score", -999.0)),\n            "market_price": int((obs.get("market") or {}).get("prices", {}).get(item, 0) or 0),\n            "market_inventory": int((obs.get("market") or {}).get("inventory", {}).get(item, 0) or 0),\n        })\n        if qty > 0:\n'''


def instrument(src: Path, dst: Path, threshold: int) -> None:
    text = src.read_text(encoding="utf-8")
    count = text.count(EVENT_INSERT)
    if count != 1:
        raise SystemExit(f"{src}: expected one primary V92 qty block, found {count}")
    text = text.replace(EVENT_INSERT, EVENT_REPLACEMENT, 1)
    text += f"\n# diagnostic-only data; non-callable so agent selection is unchanged\n_V140_PRIMARY_THRESHOLD = {threshold}\n_V140_PRIMARY_DIAG = []\n"
    dst.write_text(text, encoding="utf-8")


def canon(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), default=str)


def digest(v: Any) -> str:
    return hashlib.sha256(canon(v).encode()).hexdigest()


class TraceAgent:
    def __init__(self, spec: str):
        self.agent = resolve_agent(spec)
        code = getattr(self.agent, "__code__", None)
        self.argcount = code.co_argcount if code is not None else 2
        self.trace: list[dict[str, Any]] = []
        self.exceptions: list[str] = []

    def __call__(self, obs, config=None):
        before = copy.deepcopy(obs)
        try:
            action = self.agent(*[obs, config][: self.argcount])
        except Exception as exc:
            self.exceptions.append(repr(exc))
            raise
        action = copy.deepcopy(action)
        self.trace.append({
            "step": int(before.get("step", len(self.trace))),
            "obs_hash": digest(before),
            "action_hash": digest(action),
            "action": action,
        })
        return action

    def events(self) -> list[dict[str, Any]]:
        return copy.deepcopy(getattr(self.agent, "__globals__", {}).get("_V140_PRIMARY_DIAG", []))


def run(spec: str, exact_v115: str, seed: int, seat: int) -> dict[str, Any]:
    focal = TraceAgent(spec)
    opponent = resolve_agent(exact_v115)
    env = make("kaggriculture", configuration={"seed": seed})
    env.run([focal, opponent] if seat == 0 else [opponent, focal])
    rewards = [state.get("reward") for state in env.state]
    return {
        "reward": rewards[seat],
        "opponent_reward": rewards[1 - seat],
        "trace": focal.trace,
        "events": focal.events(),
        "exceptions": focal.exceptions,
    }


def removed_orders(a: Any, b: Any) -> list[list[Any]]:
    am = [list(o) for o in (a or {}).get("market") or []] if isinstance(a, dict) else []
    bm = [list(o) for o in (b or {}).get("market") or []] if isinstance(b, dict) else []
    left = [list(o) for o in am]
    for o in bm:
        if o in left:
            left.remove(o)
    return left


def first_div(base: dict[str, Any], cand: dict[str, Any]) -> dict[str, Any]:
    bt, ct = base["trace"], cand["trace"]
    n = min(len(bt), len(ct))
    idx = next((i for i in range(n) if bt[i]["action_hash"] != ct[i]["action_hash"]), None)
    if idx is None:
        return {"first_action_mismatch": None, "trace_len": [len(bt), len(ct)]}
    b, c = bt[idx], ct[idx]
    step = b["step"]
    return {
        "first_action_mismatch": idx,
        "step": step,
        "same_observation": b["obs_hash"] == c["obs_hash"],
        "baseline_action": b["action"],
        "candidate_action": c["action"],
        "removed_from_v115": removed_orders(b["action"], c["action"]),
        "added_by_v140": removed_orders(c["action"], b["action"]),
        "v115_primary_events_at_step": [e for e in base["events"] if int(e["step"]) == step],
        "v140_primary_events_at_step": [e for e in cand["events"] if int(e["step"]) == step],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v115", required=True)
    ap.add_argument("--v140", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    d115 = out.parent / "v115_primary_diag.py"
    d140 = out.parent / "v140_primary_diag.py"
    instrument(Path(args.v115), d115, 1)
    instrument(Path(args.v140), d140, 2)

    # All are already-burned v140 development seeds.  Both seats on the worst
    # and strongest positive seed; seat0 is enough to classify the remaining
    # non-zero direct seeds without consuming fresh evidence.
    cases = [(642, 0), (642, 1), (651, 0), (651, 1), (641, 0), (648, 0), (649, 0), (652, 0)]
    rows = []
    for seed, seat in cases:
        base = run(str(d115), args.v115, seed, seat)
        cand = run(str(d140), args.v115, seed, seat)
        rows.append({
            "seed": seed,
            "seat": seat,
            "reward_delta_v140_minus_v115_counterfactual": float(cand["reward"]) - float(base["reward"]),
            "v115_reward": base["reward"],
            "v140_reward": cand["reward"],
            "v115_exceptions": base["exceptions"],
            "v140_exceptions": cand["exceptions"],
            "divergence": first_div(base, cand),
        })

    report = {
        "purpose": "burned v140 development telemetry only; not promotion evidence",
        "rows": rows,
    }
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    compact = []
    for r in rows:
        d = r["divergence"]
        compact.append({
            "seed": r["seed"], "seat": r["seat"],
            "reward_delta": r["reward_delta_v140_minus_v115_counterfactual"],
            "step": d.get("step"), "same_obs": d.get("same_observation"),
            "removed": d.get("removed_from_v115"), "added": d.get("added_by_v140"),
            "v115_events": d.get("v115_primary_events_at_step"),
            "v140_events": d.get("v140_primary_events_at_step"),
        })
    print(json.dumps(compact, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
